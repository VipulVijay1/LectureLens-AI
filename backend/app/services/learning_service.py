from app.services.llm_service import generate_answer_with_llm


def structure_summary(summary_text):

    prompt = f"""
You are an expert teacher.

Convert the following explanation into structured notes.

Rules:
- ONLY use the given content
- DO NOT add extra information
- DO NOT introduce new topics
- Keep it clean and structured

Format:
- Headings
- Bullet points

Content:
{summary_text}

Notes:
"""

    return generate_answer_with_llm(prompt, []).strip()


def generate_flashcards_from_chunks(chunks):

    combined_text = "\n".join([chunk["text"] for chunk in chunks])

    # 🔥 limit size
    combined_text = combined_text[:2000]

    prompt = f"""
You are an expert teacher.

Generate flashcards ONLY from the given content.

STRICT RULES:
- Focus ONLY on the topic present in content
- DO NOT introduce new topics
- DO NOT generalize to full lecture
- Keep answers concise

Format:
Q: ...
A: ...

Content:
{combined_text}

Flashcards:
"""

    return generate_answer_with_llm(prompt, []).strip()