from pydantic import BaseModel

class ChunkResponse(BaseModel):
    id: int
    document_id: int
    content: str