from fastapi import APIRouter, UploadFile, File, Depends
from pathlib import Path
import shutil

from sqlalchemy.orm import Session

from app.schemas.qa import QuestionRequest, AnswerResponse
from app.db.dependencies import get_db
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import chunk_text
from app.services.embedding_service import generate_embedding
from app.services.document_service import save_document
from app.services.retrieval_service import retrieve_relevant_chunks_from_db
from app.services.gemini_service import generate_answer


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(str(file_path))

    chunks = chunk_text(text)

    embeddings = [
        generate_embedding(chunk)
        for chunk in chunks
    ]

    document = save_document(
        db=db,
        filename=file.filename,
        text=text,
        chunks=chunks,
        embeddings=embeddings,
    )

    return {
        "id": document.id,
        "filename": document.filename,
        "text_length": document.text_length,
        "chunk_count": document.chunk_count,
        "embedding_dimension": len(embeddings[0]),
    }


@router.post("/ask", response_model=AnswerResponse)
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    relevant_chunks = retrieve_relevant_chunks_from_db(
        db=db,
        document_id=request.document_id,
        question=request.question,
        top_k=3,
    )

    context = "\n\n".join(
        chunk.content
        for chunk in relevant_chunks
    )

    answer = generate_answer(
        question=request.question,
        context=context,
    )

    return {
        "question": request.question,
        "answer": answer,
    }