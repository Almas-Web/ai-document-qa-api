from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: int
    filename: str
    text_length: int
    chunk_count: int