from app.services.gemini_service import generate_answer

answer = generate_answer(
    "What is a fuzzy set?",
    "A fuzzy set is a set where elements have degrees of membership between 0 and 1."
)

print(answer)