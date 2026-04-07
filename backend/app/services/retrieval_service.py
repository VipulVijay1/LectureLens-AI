import os
import json
import numpy as np
import faiss
import time

from app.core.index_manager import index_manager
from app.core.config import DATA_DIR
from app.core.logger import logger
from app.services.llm_service import generate_answer_with_llm
from app.core.model_loader import model_loader
from app.services.evaluation_service import (
    evaluate_retrieval,
    evaluate_faithfulness,
    evaluate_answer_relevance
)


#-----------------------------
# ReWrite Query
#-----------------------------
def rewrite_query(query: str):
    prompt = f"""
Rewrite the following query to make it more clear, detailed, and specific 
for retrieving relevant information from a lecture.

Query: {query}

Rewritten Query:
"""

    response = generate_answer_with_llm(prompt, [])
    return response.strip()


# -----------------------------
# Multi Query Generation
# -----------------------------
def generate_multi_queries(query: str):
    prompt = f"""
Generate 3 different variations of the following query.
Each should capture a different perspective.

Query: {query}

Return only the queries, one per line.
"""

    # Use your existing LLM pipeline
    response = generate_answer_with_llm(prompt, [])

    queries = response.strip().split("\n")
    queries = [q.strip("- ").strip() for q in queries if q.strip()]

    return [query] + queries[:3]

# -----------------------------
# MMR Selection
# -----------------------------
def mmr_selection(query_embedding, chunk_embeddings, chunks, top_k=4, lambda_param=0.7):
    selected = []
    selected_indices = []

    similarity_to_query = np.dot(chunk_embeddings, query_embedding.T).flatten()

    while len(selected) < top_k:
        if len(selected) == 0:
            idx = np.argmax(similarity_to_query)
            selected.append(chunks[idx])
            selected_indices.append(idx)
            continue

        mmr_scores = []

        for i in range(len(chunks)):
            if i in selected_indices:
                continue

            relevance = similarity_to_query[i]

            if selected_indices:
                diversity = max(
                    np.dot(chunk_embeddings[i], chunk_embeddings[j])
                    for j in selected_indices
                )
            else:
                diversity = 0

            mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity
            mmr_scores.append((i, mmr_score))

        if not mmr_scores:
            break
        idx = max(mmr_scores, key=lambda x: x[1])[0]
        selected.append(chunks[idx])
        selected_indices.append(idx)

    return selected


# -----------------------------
# Main Retrieval
# -----------------------------
def retrieve(video_id: str, query: str, top_k: int = 20):

    video_path = os.path.join(DATA_DIR, video_id)
    start_time = time.time()

    if not os.path.exists(video_path):
        raise ValueError("Video not ingested.")

    index = index_manager.get_index(video_id)

    chunks_path = os.path.join(video_path, "chunks.json")
    if not os.path.exists(chunks_path):
        raise ValueError("Video artifacts incomplete.")

    with open(chunks_path, "r") as f:
        chunks = json.load(f)

    chunk_embeddings = np.array([chunk["embedding"] for chunk in chunks])

    # -----------------------------
    # Multi Query
    # -----------------------------
    rewritten_query = rewrite_query(query)
    queries = generate_multi_queries(rewritten_query)

    all_results = []

    for q in queries:
        q_embedding = model_loader.embedding_model.encode([q])
        q_embedding = np.array(q_embedding).astype("float32")
        faiss.normalize_L2(q_embedding)

        faiss_scores, faiss_indices = index.search(q_embedding.reshape(1, -1), top_k)

        for score, idx in zip(faiss_scores[0], faiss_indices[0]):
            if idx < len(chunks):
                chunk = chunks[idx]
                all_results.append({
                    "timestamp": chunk["timestamp"],
                    "text": chunk["text"],
                    "score": float(score)
                })

    # -----------------------------
    # Deduplicate + Merge
    # -----------------------------
    score_map = {}

    for item in all_results:
        key = item["text"][:200]

        if key not in score_map:
            score_map[key] = item
        else:
            if item["score"] > score_map[key]["score"]:
                score_map[key] = item

    hybrid_results = list(score_map.values())
    hybrid_results.sort(key=lambda x: x["score"], reverse=True)

    # -----------------------------
    # Reranking
    # -----------------------------
    rerank_inputs = [(query, item["text"]) for item in hybrid_results]
    rerank_scores = model_loader.reranker.predict(rerank_inputs)

    for i, score in enumerate(rerank_scores):
        hybrid_results[i]["score"] = float(score)

    hybrid_results.sort(key=lambda x: x["score"], reverse=True)

    # -----------------------------
    # Filtering + Dedup
    # -----------------------------
    filtered = [chunk for chunk in hybrid_results if chunk["score"] > 0]

    if not filtered:
        filtered = hybrid_results[:3]

    unique_chunks = []
    seen = set()

    for chunk in filtered:
        key = chunk["text"][:150]
        if key not in seen:
            unique_chunks.append(chunk)
            seen.add(key)

    # -----------------------------
    # MMR
    # -----------------------------
    text_to_index = {chunk["text"]: i for i, chunk in enumerate(chunks)}

    selected_embeddings = np.array([
        chunk_embeddings[text_to_index[item["text"]]]
        for item in unique_chunks
    ])

    query_embedding = model_loader.embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    faiss.normalize_L2(query_embedding)
    query_embedding = query_embedding[0]

    if not unique_chunks:
        return {
            "video_id": video_id,
            "answer": "No relevant information found in the lecture for your query.",
            "sources": [],
            "evaluation": {}
        }

    if len(unique_chunks) <= 4:
        top_chunks = unique_chunks
    else:
        top_chunks = mmr_selection(
            query_embedding,
            selected_embeddings,
            unique_chunks,
            top_k=4
        )

    # -----------------------------
    # LLM Answer
    # -----------------------------
    answer = generate_answer_with_llm(query, top_chunks)

    precision = evaluate_retrieval(query, top_chunks)
    faithfulness = evaluate_faithfulness(answer, top_chunks)
    relevance = evaluate_answer_relevance(query, answer)

    total_time = time.time() - start_time

    logger.info(f"Query completed in {total_time:.4f}s")

    return {
        "video_id": video_id,
        "answer": answer,
        "sources": top_chunks,
        "evaluation": {
            "precision_at_k": precision,
            "faithfulness_score": faithfulness,
            "answer_relevance_score": relevance
        }
    }