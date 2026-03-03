from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def evaluate_retrieval(query: str, chunks: list):
    """
    Returns precision score (0-1)
    """

    relevant_count = 0

    for chunk in chunks:
        prompt = f"""
        Query: {query}

        Chunk:
        {chunk['text']}

        Is this chunk relevant to the query?
        Answer only YES or NO.
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        verdict = response.choices[0].message.content.strip().upper()

        if "YES" in verdict:
            relevant_count += 1

    precision = relevant_count / len(chunks) if chunks else 0

    return precision

def evaluate_faithfulness(answer: str, chunks: list):
    context = "\n\n".join([c["text"] for c in chunks])

    prompt = f"""
    Context:
    {context}

    Answer:
    {answer}

    Is the answer fully supported by the context?
    Score from 1 (not supported) to 5 (fully supported).
    Return only the number.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    score_text = response.choices[0].message.content.strip()

    try:
        score = int(score_text)
    except:
        score = 3

    return score

def evaluate_answer_relevance(query: str, answer: str):

    prompt = f"""
    Query:
    {query}

    Answer:
    {answer}

    Does this answer correctly and sufficiently address the query?
    Score from 1 (poor) to 5 (excellent).
    Return only the number.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    score_text = response.choices[0].message.content.strip()

    try:
        score = int(score_text)
    except:
        score = 3

    return score