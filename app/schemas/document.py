from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DocumentResponse(BaseModel):
    id: int
    filename: str
    text_length: int
    chunk_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)