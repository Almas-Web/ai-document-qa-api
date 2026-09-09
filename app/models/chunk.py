from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from pgvector.sqlalchemy import Vector

from app.db.database import Base

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
    )

    content = Column(Text, nullable=False)

    embedding = Column(
        Vector(384),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )