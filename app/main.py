from fastapi import FastAPI

from app.api.documents import router as document_router
from app.api.auth import router as auth_router


app = FastAPI(title="AI Document Q&A API")

app.include_router(auth_router)
app.include_router(document_router)


@app.get("/")
def root():
    return {
        "message": "AI Document Q&A API is running"
    }