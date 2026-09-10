from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.chunk import Chunk

def save_document(
    db: Session,
    filename: str,
    text: str,
    chunks: list[str],
    embeddings: list[list[float]],
):
    document = Document(
        filename=filename,
        text_length=len(text),
        chunk_count=len(chunks),
    )

    db.add(document)
    db.flush()

    for content, embedding in zip(chunks, embeddings):
        chunk = Chunk(
            document_id=document.id,
            content=content,
            embedding=embedding,
        )

        db.add(chunk)

    db.commit()
    db.refresh(document)

    return document