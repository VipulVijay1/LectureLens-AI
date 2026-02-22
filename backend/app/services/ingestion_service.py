import os
import json
import numpy as np
import faiss

from youtube_transcript_api import YouTubeTranscriptApi
from app.core.model_loader import model_loader

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


def chunk_data(data):
    return [
        {
            "timestamp": item["timestamp"],
            "text": item["text"]
        }
        for item in data
    ]


def ingest_video(video_id: str):
    video_path = os.path.join(DATA_DIR, video_id)

    if os.path.exists(video_path):
        return {
            "message": "Video already ingested.",
            "video_id": video_id,
            "status": "cached"
        }

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

    return {
        "message": "Video ingested successfully.",
        "video_id": video_id,
        "status": "ingested"
    }