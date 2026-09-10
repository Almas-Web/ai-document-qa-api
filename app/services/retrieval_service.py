from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.services.embedding_service import generate_embedding


def retrieve_relevant_chunks_from_db(
    db: Session,
    document_id: int,
    question: str,
    top_k: int = 3,
):
    question_embedding = generate_embedding(question)

    results = (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id)
        .order_by(
            Chunk.embedding.cosine_distance(question_embedding)
        )
        .limit(top_k)
        .all()
    )

    return results