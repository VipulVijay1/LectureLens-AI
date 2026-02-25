import os
import json
import numpy as np
import faiss
import time

from app.core.model_loader import model_loader
from app.core.index_manager import index_manager
from app.core.config import DATA_DIR
from app.core.logger import logger

def retrieve(video_id: str, query: str, top_k: int = 5):
    from app.core.logger import logger
    video_path = os.path.join(DATA_DIR, video_id)
    start_time = time.time()
    if not os.path.exists(video_path):
        raise ValueError("Video not ingested.")

    # Load FAISS index via IndexManager
    index = index_manager.get_index(video_id)

    chunks_path = os.path.join(video_path, "chunks.json")

    if not os.path.exists(chunks_path):
        raise ValueError("Video artifacts incomplete.")

    with open(chunks_path, "r") as f:
        chunks = json.load(f)

    # Generate query embedding
    query_embedding = model_loader.embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    faiss.normalize_L2(query_embedding)

    # Search FAISS
    faiss_start = time.time()
    scores, indices = index.search(query_embedding, top_k)
    faiss_time = time.time() - faiss_start

    retrieved = []
    for score, idx in zip(scores[0], indices[0]):
        chunk = chunks[idx]
        retrieved.append({
            "timestamp": chunk["timestamp"],
            "text": chunk["text"],
            "score": float(score)
        })

    # Cross-encoder re-ranking
    rerank_inputs = [(query, item["text"]) for item in retrieved]
    rerank_start = time.time()
    rerank_scores = model_loader.reranker.predict(rerank_inputs)
    rerank_time = time.time() - rerank_start

    for i, score in enumerate(rerank_scores):
        retrieved[i]["score"] = float(score)

    # Sort by rerank score descending
    retrieved.sort(key=lambda x: x["score"], reverse=True)

    total_time = time.time() - start_time

    logger.info(
        f"Query completed for video {video_id} | "
        f"FAISS time: {faiss_time:.4f}s | "
        f"Rerank time: {rerank_time:.4f}s | "
        f"Total time: {total_time:.4f}s"
    )

    return retrieved