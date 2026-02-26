import os
import json
import shutil
import numpy as np
import faiss

from youtube_transcript_api import YouTubeTranscriptApi
from app.core.model_loader import model_loader
from app.core.config import DATA_DIR
from app.core.logger import logger

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


def chunk_data(data):
    window_size = 8
    overlap = 2
    chunks = []
    for i in range(0, len(transcript), window_size - overlap):
        window = transcript[i:i+window_size]
        combined_text = " ".join([x["text"] for x in window])
        chunks.append({
            "text": combined_text,
            "timestamp": window[0]["timestamp"]
        })
    return chunks

def artifacts_valid(video_path):
    required_files = [
        "embeddings.npy",
        "index.faiss",
        "chunks.json"
    ]

    for file in required_files:
        if not os.path.exists(os.path.join(video_path, file)):
            return False

    return True


def ingest_video(video_id: str):
    video_path = os.path.join(DATA_DIR, video_id)
    logger.info(f"Ingestion started for video {video_id}")
    # If folder exists, validate artifacts
    if os.path.exists(video_path):
        if artifacts_valid(video_path):
            logger.info(f"Video {video_id} already ingested. Using cached artifacts.")
            return {
                "message": "Video already ingested.",
                "video_id": video_id,
                "status": "cached"
            }
        else:
            # Corrupted or partial ingestion → clean up
            logger.warning(f"Artifacts corrupted for video {video_id}. Cleaning up.")
            shutil.rmtree(video_path)

    os.makedirs(video_path, exist_ok=True)

    transcript_data = fetch_transcript(video_id)
    chunks = chunk_data(transcript_data)

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model_loader.embedding_model.encode(texts)
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    np.save(os.path.join(video_path, "embeddings.npy"), embeddings)
    faiss.write_index(index, os.path.join(video_path, "index.faiss"))

    with open(os.path.join(video_path, "chunks.json"), "w") as f:
        json.dump(chunks, f)
    logger.info(f"Ingestion successful for video {video_id}")
    return {
        "message": "Video ingested successfully.",
        "video_id": video_id,
        "status": "ingested"
    }