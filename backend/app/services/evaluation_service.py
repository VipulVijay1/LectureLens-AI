from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def evaluate_retrieval(query: str, chunks: list):
    relevant_count = 0

    for chunk in chunks:
        prompt = f"""
        Query: {query}

        Chunk:
        {chunk['text']}

        Evaluate relevance strictly:

        - 5 → directly answers the query
        - 4 → strongly related
        - 3 → somewhat related
        - 2 → weakly related
        - 1 → completely irrelevant

        Return ONLY a number (1–5).
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        verdict = response.choices[0].message.content.strip()

        try:
            score = int(verdict)
        except:
            score = 3  
        if score >= 4:
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

def evaluate_recall(query: str, chunks: list):
    """
    Estimate if important info is present
    """
    context = "\n\n".join([c["text"] for c in chunks])

    prompt = f"""
    Query:
    {query}

    Retrieved Context:
    {context}

    Does the retrieved context contain enough information to answer the query?
    Score from 1 (missing info) to 5 (complete).
    Return only number.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        return int(response.choices[0].message.content.strip())
    except:
        return 3
    

def evaluate_full(query, answer, chunks):
    return {
        "precision": evaluate_retrieval(query, chunks),
        "recall": evaluate_recall(query, chunks),
        "faithfulness": evaluate_faithfulness(answer, chunks),
        "answer_relevance": evaluate_answer_relevance(query, answer)
    }


def map_confidence(faithfulness_score: int):
    """
    Map 1–5 faithfulness score → label + badge
    """
    if faithfulness_score >= 4:
        return {"label": "HIGH", "badge": "🟢"}
    elif faithfulness_score >= 3:
        return {"label": "MEDIUM", "badge": "🟡"}
    else:
        return {"label": "LOW", "badge": "🔴"}