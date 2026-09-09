from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    text_length = Column(Integer, nullable=False)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)