from app.services.embedding_service import generate_embedding
from app.services.retrieval_service import retrieve_relevant_chunks

chunks = [
    "A fuzzy set allows elements to have membership values between 0 and 1.",
    "Python is a high-level programming language.",
    "PostgreSQL is an open-source relational database system.",
]
embeddings = [
    generate_embedding(chunk)
    for chunk in chunks
]
results = retrieve_relevant_chunks(
    question="What is a fuzzy set?",
    chunks=chunks,
    embeddings=embeddings,
    top_k=2,
)

for result in results:
    print("\nScore:", result["score"])
    print("Chunk:", result["chunk"])