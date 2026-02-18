import os
import json
import numpy as np
import faiss

from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder



DATA_DIR = "data"


def seconds_to_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def fetch_transcript(video_id):
    transcript = YouTubeTranscriptApi().fetch(video_id)

    data = []
    for entry in transcript:
        data.append({
            "timestamp": seconds_to_timestamp(entry.start),
            "text": entry.text
        })

    return data


def chunk_data(data, chunk_size=1):
    chunks = []

    for i in range(0, len(data), chunk_size):
        chunk_text = " ".join([item["text"] for item in data[i:i+chunk_size]])
        start_time = data[i]["timestamp"]

        chunks.append({
            "timestamp": start_time,
            "text": chunk_text
        })

    return chunks


def ingest_video(video_id, model):
    print("Ingesting video...")

    video_path = os.path.join(DATA_DIR, video_id)
    os.makedirs(video_path, exist_ok=True)

    transcript_data = fetch_transcript(video_id)
    chunks = chunk_data(transcript_data)

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Save embeddings
    np.save(os.path.join(video_path, "embeddings.npy"), embeddings)

    # Save index
    faiss.write_index(index, os.path.join(video_path, "index.faiss"))

    # Save chunks
    with open(os.path.join(video_path, "chunks.json"), "w") as f:
        json.dump(chunks, f)

    print("Ingestion complete and cached.")

    return index, chunks


def load_cached(video_id):
    video_path = os.path.join(DATA_DIR, video_id)

    embeddings = np.load(os.path.join(video_path, "embeddings.npy"))
    index = faiss.read_index(os.path.join(video_path, "index.faiss"))

    with open(os.path.join(video_path, "chunks.json"), "r") as f:
        chunks = json.load(f)

    print("Loaded cached data.")

    return index, chunks


def search(index, chunks, model, reranker, query, top_k=5):
    query_embedding = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_embedding)

    distances, indices = index.search(query_embedding, top_k)

    # Get candidate chunks
    candidate_chunks = [chunks[idx] for idx in indices[0]]

    # Prepare pairs for cross-encoder
    pairs = [[query, chunk["text"]] for chunk in candidate_chunks]

    # Get cross-encoder scores
    scores = reranker.predict(pairs)

    # Combine chunks with scores
    scored_chunks = list(zip(candidate_chunks, scores))

    # Sort by score descending
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    print("\nRe-ranked Results:\n")

    for chunk, score in scored_chunks:
        print(f"Score: {score:.4f}")
        print(f"[{chunk['timestamp']}] {chunk['text'][:150]}...\n")


def main():
    video_id = "i_LwzRVP7bg"  # change if needed
    model = SentenceTransformer("all-MiniLM-L6-v2")
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    video_path = os.path.join(DATA_DIR, video_id)

    if os.path.exists(video_path):
        index, chunks = load_cached(video_id)
    else:
        index, chunks = ingest_video(video_id, model)

    test_queries = [
        "What is supervised learning?",
        "Difference between regression and classification?",
        "What is gradient descent?",
        "What is overfitting?",
        "What is a neural network?"
    ]

    for query in test_queries:
        print("\n==============================")
        print("Query:", query)
        search(index, chunks, model, reranker, query, top_k=10)




if __name__ == "__main__":
    main()
