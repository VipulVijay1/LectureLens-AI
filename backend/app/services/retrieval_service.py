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

    # -----------------------------
    # Query Embedding
    # -----------------------------
    query_embedding = model_loader.embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    faiss.normalize_L2(query_embedding)

    # -----------------------------
    # FAISS Search
    # -----------------------------
    faiss_start = time.time()
    scores, indices = index.search(query_embedding, top_k)
    faiss_time = time.time() - faiss_start

    retrieved = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(chunks):
            chunk = chunks[idx]
            retrieved.append({
                "timestamp": chunk["timestamp"],
                "text": chunk["text"],
                "score": float(score)
            })

    # -----------------------------
    # Cross-Encoder Re-ranking
    # -----------------------------
    rerank_inputs = [(query, item["text"]) for item in retrieved]

    rerank_start = time.time()
    rerank_scores = model_loader.reranker.predict(rerank_inputs)
    rerank_time = time.time() - rerank_start

    for i, score in enumerate(rerank_scores):
        retrieved[i]["score"] = float(score)

    # Sort by rerank score (descending)
    retrieved.sort(key=lambda x: x["score"], reverse=True)

    # -----------------------------
    # LLM Generation (Top 4)
    # -----------------------------
    # Keep only reasonably relevant chunks
    filtered = [chunk for chunk in retrieved if chunk["score"] > 0]

    # Fallback if all scores are low
    if not filtered:
        filtered = retrieved[:3]

    # Remove near-duplicate texts
    unique_chunks = []
    seen_texts = set()

    for chunk in filtered:
        text_key = chunk["text"][:150]
        if text_key not in seen_texts:
            unique_chunks.append(chunk)
            seen_texts.add(text_key)

    top_chunks = unique_chunks[:4]

    answer = generate_answer_with_llm(query, top_chunks)

    total_time = time.time() - start_time

    logger.info(
        f"Query completed for video {video_id} | "
        f"FAISS time: {faiss_time:.4f}s | "
        f"Rerank time: {rerank_time:.4f}s | "
        f"Total time: {total_time:.4f}s"
    )
    if len(answer.strip()) < 20:
        answer = "The system could not generate a sufficient answer from the available context."
    return {
        "video_id": video_id,
        "answer": answer,
        "sources": top_chunks
    }