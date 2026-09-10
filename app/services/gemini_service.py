from google import genai
from google.genai import types
from app.core.config import settings

client = genai.Client(
    api_key=settings.gemini_api_key
)

def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a helpful document question-answering assistant.

Answer the user's question using only the provided context.

Context:
{context}

Question:
{question}

If the answer is not available in the context, say:
"I could not find the answer in the provided document."

Answer:
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2
        ),
    )
    return response.text