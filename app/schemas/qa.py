from pydantic import BaseModel

class QuestionRequest(BaseModel):
    document_id: int
    question: str

class AnswerResponse(BaseModel):
    question: str
    answer: str