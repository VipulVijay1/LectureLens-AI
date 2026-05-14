from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

from app.services.retrieval_service import retrieve


from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="llama3-8b-8192",
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key="YOUR_GROQ_API_KEY"
)



def run_ragas_evaluation(video_id: str, eval_data: list):
    """
    eval_data format:
    [
        {
            "query": "...",
            "ground_truth": "..."
        }
    ]
    """

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in eval_data:
        query = item["query"]
        gt = item.get("ground_truth", "")

        result = retrieve(video_id, query, top_k=10)

        answer = result["answer"]
        retrieved_chunks = result["sources"]

        context_texts = [chunk["text"] for chunk in retrieved_chunks]

        questions.append(query)
        answers.append(answer)
        contexts.append(context_texts)
        ground_truths.append(gt)

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ],
        llm=llm
    )

    return result