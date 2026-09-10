from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pathlib import Path
import shutil
import uuid
from sqlalchemy.orm import Session
from app.schemas.qa import QuestionRequest, AnswerResponse
from app.schemas.document import DocumentResponse
from app.db.dependencies import get_db
from app.api.dependencies import get_authenticated_user
from app.models.document import Document
from app.models.chunk import Chunk
from app.models.user import User
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import chunk_text
from app.services.embedding_service import generate_embedding
from app.services.document_service import save_document
from app.services.retrieval_service import retrieve_relevant_chunks_from_db
from app.services.gemini_service import generate_answer

router = APIRouter(prefix="/documents", tags=["Documents"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    file_header = file.file.read(5)
    file.file.seek(0)
    if file_header != b"%PDF-":
        raise HTTPException(status_code=400, detail="Invalid PDF file.")
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size must not exceed 10 MB.")
    original_filename = Path(file.filename).name
    stored_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = UPLOAD_DIR / stored_filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        text = extract_text_from_pdf(str(file_path))
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF contains no readable text.",
            )
        chunks = chunk_text(text)
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not create chunks from the document.",
            )
        embeddings = [generate_embedding(chunk) for chunk in chunks]
        document = save_document(
            db=db,
            user_id=current_user.id,
            filename=stored_filename,
            text=text,
            chunks=chunks,
            embeddings=embeddings,
        )
        return {
            "id": document.id,
            "filename": original_filename,
            "text_length": document.text_length,
            "chunk_count": document.chunk_count,
            "embedding_dimension": len(embeddings[0]),
        }
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise
    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process the uploaded document.",
        )

@router.post("/ask", response_model=AnswerResponse)
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    document = db.query(Document).filter(
        Document.id == request.document_id,
        Document.user_id == current_user.id,
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    relevant_chunks = retrieve_relevant_chunks_from_db(
        db=db,
        document_id=request.document_id,
        question=request.question,
        top_k=3,
    )
    if not relevant_chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant information found in the document.",
        )
    context = "\n\n".join(chunk.content for chunk in relevant_chunks)
    answer = generate_answer(
        question=request.question,
        context=context,
    )
    return {
        "question": request.question,
        "answer": answer,
    }

@router.get("/", response_model=list[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).all()
    return documents

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    file_path = UPLOAD_DIR / document.filename
    db.query(Chunk).filter(
        Chunk.document_id == document.id
    ).delete()
    db.delete(document)
    db.commit()
    if file_path.exists():
        file_path.unlink()
    return {
        "message": "Document deleted successfully."
    }