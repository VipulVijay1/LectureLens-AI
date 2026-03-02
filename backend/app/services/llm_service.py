import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_answer_with_llm(query, retrieved_chunks):
    context = "\n\n".join(
        [f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(retrieved_chunks)]
    )

    prompt = f"""
You are an expert AI tutor.

Using ONLY the context below, answer the question clearly
in 4-6 well-structured sentences.
When referencing information, mention chunk numbers like [1], [2].
Do NOT repeat phrases.
Be concise but informative.
If context is insufficient, say so.

Context:
{context}

Question:
{query}

Answer:
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful AI tutor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=300
    )

    return response.choices[0].message.content