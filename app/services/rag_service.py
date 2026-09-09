from app.services.gemini_service import generate_answer
from app.services.retrieval_service import retrieve_relevant_chunks

def answer_question(
    question: str,
    chunks: list[str],
    embeddings: list[list[float]],
    top_k: int = 3,
) -> str:
    relevant_chunks = retrieve_relevant_chunks(
        question=question,
        chunks=chunks,
        embeddings=embeddings,
        top_k=top_k,
    )

    context = "\n\n".join(
        result["chunk"]
        for result in relevant_chunks
    )

    answer = generate_answer(
        question=question,
        context=context,
    )

    return answer