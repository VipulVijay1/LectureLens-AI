import os
import json
import numpy as np
import faiss
import time

from rank_bm25 import BM25Okapi
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

            diversity = max(
                np.dot(chunk_embeddings[i], chunk_embeddings[j])
                for j in selected_indices
            )

            mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity
            mmr_scores.append((i, mmr_score))

        idx = max(mmr_scores, key=lambda x: x[1])[0]
        selected.append(chunks[idx])
        selected_indices.append(idx)

    return selected

def tokenize(text):
    return text.lower().split()

def normalize_scores(scores):
    min_s = min(scores)
    max_s = max(scores)
    
    if max_s - min_s == 0:
        return [1.0 for _ in scores]
    
    return [(s - min_s) / (max_s - min_s) for s in scores]

def retrieve(video_id: str, query: str, top_k: int = 20):

    video_path = os.path.join(DATA_DIR, video_id)
    start_time = time.time()

    if not os.path.exists(video_path):
        raise ValueError("Video not ingested.")

    # Load FAISS index
    index = index_manager.get_index(video_id)

    chunks_path = os.path.join(video_path, "chunks.json")
    if not os.path.exists(chunks_path):
        raise ValueError("Video artifacts incomplete.")

    with open(chunks_path, "r") as f:
        chunks = json.load(f)
    chunk_embeddings = np.array([chunk["embedding"] for chunk in chunks])
    # -----------------------------
    # BM25 Setup
    # -----------------------------
    corpus = [chunk["text"] for chunk in chunks]
    tokenized_corpus = [tokenize(doc) for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)

    # -----------------------------
    # Query Embedding
    # -----------------------------
    query_embedding = model_loader.embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    faiss.normalize_L2(query_embedding)

    query_embedding = query_embedding[0]  # IMPORTANT for MMR

    # -----------------------------
    # FAISS Search
    # -----------------------------
    faiss_start = time.time()
    faiss_scores, faiss_indices = index.search(query_embedding.reshape(1, -1), top_k)
    faiss_time = time.time() - faiss_start

    faiss_results = []
    for score, idx in zip(faiss_scores[0], faiss_indices[0]):
        if idx < len(chunks):
            chunk = chunks[idx]
            faiss_results.append({
                "timestamp": chunk["timestamp"],
                "text": chunk["text"],
                "score": float(score),
                "source": "faiss"
            })

    # -----------------------------
    # BM25 Search
    # -----------------------------
    bm25_start = time.time()
    tokenized_query = tokenize(query)
    bm25_scores = bm25.get_scores(tokenized_query)

    bm25_indices = np.argsort(bm25_scores)[::-1][:top_k]
    bm25_time = time.time() - bm25_start

    bm25_results = []
    for idx in bm25_indices:
        if idx < len(chunks):
            chunk = chunks[idx]
            bm25_results.append({
                "timestamp": chunk["timestamp"],
                "text": chunk["text"],
                "score": float(bm25_scores[idx]),
                "source": "bm25"
            })
    
    # Extract scores
    faiss_scores_list = [item["score"] for item in faiss_results]
    bm25_scores_list = [item["score"] for item in bm25_results]

    # Normalize
    faiss_norm = normalize_scores(faiss_scores_list)
    bm25_norm = normalize_scores(bm25_scores_list)

    # Assign normalized scores back
    for i in range(len(faiss_results)):
        faiss_results[i]["norm_score"] = faiss_norm[i]

    for i in range(len(bm25_results)):
        bm25_results[i]["norm_score"] = bm25_norm[i]


    # -----------------------------
    # Score Fusion (Weighted Hybrid)
    # -----------------------------
    alpha = 0.7  # FAISS weight
    beta = 0.3   # BM25 weight

    combined = []

    for item in faiss_results:
        item["final_score"] = alpha * item["norm_score"]
        combined.append(item)

    for item in bm25_results:
        item["final_score"] = beta * item["norm_score"]
        combined.append(item)


    score_map = {}

    for item in combined:
        key = item["text"][:200]
        
        if key not in score_map:
            score_map[key] = item
        else:
            # keep higher score
            if item["final_score"] > score_map[key]["final_score"]:
                score_map[key] = item

    hybrid_results = list(score_map.values())

    hybrid_results.sort(key=lambda x: x["final_score"], reverse=True)
    
    # -----------------------------
    # Cross-Encoder Re-ranking
    # -----------------------------
    rerank_inputs = [(query, item["text"]) for item in hybrid_results]

    rerank_start = time.time()
    rerank_scores = model_loader.reranker.predict(rerank_inputs)
    rerank_time = time.time() - rerank_start

    for i, score in enumerate(rerank_scores):
        hybrid_results[i]["score"] = float(score)

    hybrid_results.sort(key=lambda x: x["score"], reverse=True)

    # -----------------------------
    # LLM Generation (Top 4)
    # -----------------------------
    filtered = [chunk for chunk in hybrid_results if chunk["score"] > 0]

    if not filtered:
        filtered = hybrid_results[:3]

    unique_chunks = []
    seen_texts = set()

    for chunk in filtered:
        text_key = chunk["text"][:150]
        if text_key not in seen_texts:
            unique_chunks.append(chunk)
            seen_texts.add(text_key)

    text_to_index = {chunk["text"]: i for i, chunk in enumerate(chunks)}

    # Extract embeddings only for hybrid_results
    selected_embeddings = np.array([
        chunk_embeddings[text_to_index[item["text"]]]
        for item in unique_chunks
    ])

    top_chunks = mmr_selection(
        query_embedding,
        selected_embeddings,
        unique_chunks,
        top_k=4
    )

    answer = generate_answer_with_llm(query, top_chunks)

    precision = evaluate_retrieval(query, top_chunks)
    faithfulness = evaluate_faithfulness(answer, top_chunks)
    relevance = evaluate_answer_relevance(query, answer)

    total_time = time.time() - start_time

    logger.info(
        f"Query completed for video {video_id} | "
        f"FAISS time: {faiss_time:.4f}s | "
        f"BM25 time: {bm25_time:.4f}s | "
        f"Rerank time: {rerank_time:.4f}s | "
        f"Total time: {total_time:.4f}s"
    )

    if len(answer.strip()) < 20:
        answer = "The system could not generate a sufficient answer from the available context."

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