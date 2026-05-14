import json
from app.services.retrieval_service import retrieve
from app.services.evaluation_service import evaluate_full
from app.core.model_loader import model_loader

# 🔥 IMPORTANT: Load models
model_loader.load_models()

VIDEO_ID = "i_LwzRVP7bg"  # change if needed


def run_evaluation():
    with open("evaluation_data.json", "r") as f:
        data = json.load(f)

    results = []

    print("\n🚀 Running Evaluation...\n")

    for i, item in enumerate(data):
        query = item["query"]

        print(f"\n🔹 Query {i+1}: {query}")

        # -----------------------------
        # Retrieve + Answer
        # -----------------------------
        result = retrieve(VIDEO_ID, query, top_k=8)

        answer = result["answer"]
        chunks = result["sources"]

        # -----------------------------
        # Evaluate
        # -----------------------------
        scores = evaluate_full(query, answer, chunks)

        print("Scores:", scores)

        results.append(scores)

    # -----------------------------
    # Average Scores
    # -----------------------------
    avg_scores = {
        "precision": sum(r["precision"] for r in results) / len(results),
        "recall": sum(r["recall"] for r in results) / len(results),
        "faithfulness": sum(r["faithfulness"] for r in results) / len(results),
        "answer_relevance": sum(r["answer_relevance"] for r in results) / len(results),
    }

    print("\n📊 FINAL AVERAGE SCORES:\n")
    print(avg_scores)


if __name__ == "__main__":
    run_evaluation()