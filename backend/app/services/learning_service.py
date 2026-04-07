from app.services.llm_service import generate_answer_with_llm


def generate_lecture_notes(chunks):
    combined_text = "\n".join([chunk["text"] for chunk in chunks])

    prompt = f"""
You are an expert teacher.

Create well-structured lecture notes.

Content:
{combined_text}

Notes:
"""

    return generate_answer_with_llm(prompt, []).strip()


def generate_flashcards(chunks):
    combined_text = "\n".join([chunk["text"] for chunk in chunks])

    prompt = f"""
You are an expert teacher.

Generate flashcards from the following lecture content.

Instructions:
- Create clear Question and Answer pairs
- Keep answers concise
- Focus on key concepts
- Generate at least 8–12 flashcards

Format:
Q: ...
A: ...

Content:
{combined_text}

Flashcards:
"""

    flashcards = generate_answer_with_llm(prompt, [])

    return flashcards.strip()