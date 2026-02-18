from sentence_transformers import SentenceTransformer  
import faiss
import numpy as np
import re
import warnings
import os


# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN_USAGE'] = '1'

transcript = """
[00:00:02] Machine learning is a field of artificial intelligence.
[00:00:10] Supervised learning uses labeled data to train models.
[00:00:18] Unsupervised learning finds hidden patterns in data.
[00:00:25] Neural networks are inspired by the human brain.
[00:00:32] Backpropagation is used to train neural networks.
"""

def parse_transcript(text):
    pattern = r"\[(.*?)\]\s(.+)"
    matches = re.findall(pattern,text.strip())

    data = []
    for timestamp, sentence in matches:
        data.append({
            "timestamp" : timestamp,
            "text" : sentence
        })

    return data

def chunk_data(data, chunk_size = 2):
    chunks = []

    for i in range(0, len(data), chunk_size):
        chunk_text = " ".join([item["text"] for item in data[i:i+chunk_size]])
        start_time = data[i]["timestamp"]

        chunks.append({
            "timestamp" : start_time,
            "text" : chunk_text
        })

    return chunks  

# Step 1: Parse transcript
parsed_data = parse_transcript(transcript)

# Step 2: Chunk while preserving timestamp
chunks = chunk_data(parsed_data)

# Step 3: Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [chunk["text"] for chunk in chunks]

embeddings = model.encode(texts)
embeddings = np.array(embeddings).astype("float32")

faiss.normalize_L2(embeddings)

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

# Step 4: Query
query = "How are neural networks trained?"
query_embedding = model.encode([query]).astype("float32")
faiss.normalize_L2(query_embedding)

distances, indices = index.search(query_embedding, k=2)

print("User Query:", query)
print("\nTop Results:\n")

for idx in indices[0]:
    print(f"[{chunks[idx]['timestamp']}] {chunks[idx]['text']}")