from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    document_id: int
    question: str = Field(min_length=1, max_length=2000)

class AnswerResponse(BaseModel):
    question: str
    answer: str