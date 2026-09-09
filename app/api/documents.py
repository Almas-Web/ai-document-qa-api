from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil

from app.schemas.qa import QuestionRequest, AnswerResponse
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import chunk_text
from app.services.embedding_service import generate_embedding
from app.services.rag_service import answer_question


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(str(file_path))

    chunks = chunk_text(text)

    embeddings = [
        generate_embedding(chunk)
        for chunk in chunks
    ]

    return {
        "filename": file.filename,
        "text_length": len(text),
        "chunk_count": len(chunks),
        "first_chunk": chunks[0],
        "embedding_dimension": len(embeddings[0]),
        "first_embedding": embeddings[0],
    }


@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    chunks = [
        "A fuzzy set allows elements to have membership values between 0 and 1.",
        "Python is a high-level programming language.",
        "PostgreSQL is an open-source relational database system.",
    ]

    embeddings = [
        generate_embedding(chunk)
        for chunk in chunks
    ]

    answer = answer_question(
        question=request.question,
        chunks=chunks,
        embeddings=embeddings,
        top_k=2,
    )

    return {
        "question": request.question,
        "answer": answer,
    }