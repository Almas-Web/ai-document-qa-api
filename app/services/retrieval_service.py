from app.services.embedding_service import generate_embedding

def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = sum(a * a for a in vector_a) ** 0.5
    magnitude_b = sum(b * b for b in vector_b) ** 0.5
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)

def retrieve_relevant_chunks(
    question: str,
    chunks: list[str],
    embeddings: list[list[float]],
    top_k: int = 3,
):
    question_embedding = generate_embedding(question)

    results = []

    for chunk, embedding in zip(chunks, embeddings):
        score = cosine_similarity(
            question_embedding,
            embedding
        )

        results.append({
            "chunk": chunk,
            "score": score,
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]