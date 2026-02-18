from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


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


def chunk_data(data, chunk_size=5):
    chunks = []
    
    for i in range(0, len(data), chunk_size):
        chunk_text = " ".join([item["text"] for item in data[i:i+chunk_size]])
        start_time = data[i]["timestamp"]
        
        chunks.append({
            "timestamp": start_time,
            "text": chunk_text
        })
    
    return chunks


# Replace with any YouTube lecture video ID
video_id = "rfscVS0vtbw"  # change this to real lecture

print("Fetching transcript...")
data = fetch_transcript(video_id)

print("Chunking transcript...")
chunks = chunk_data(data)

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [chunk["text"] for chunk in chunks]
embeddings = model.encode(texts)
embeddings = np.array(embeddings).astype("float32")

faiss.normalize_L2(embeddings)

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

query = "What is Python?"
query_embedding = model.encode([query]).astype("float32")
faiss.normalize_L2(query_embedding)

distances, indices = index.search(query_embedding, k=3)

print("\nTop Results:\n")

for idx in indices[0]:
    print(f"[{chunks[idx]['timestamp']}] {chunks[idx]['text'][:150]}...\n")
