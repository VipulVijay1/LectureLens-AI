from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

transcript = """
Machine learning is a field of artificial intelligence that focuses on learning from data.
Supervised learning uses labeled data to train models.
Unsupervised learning finds hidden patterns in data.
Neural networks are inspired by the human brain.
Backpropagation is used to train neural networks.
"""

def chunk_text(text , chunk_size = 2):
    sentences = text.strip().split("\n")
    chunks = []

    for i in range(0, len(sentences), chunk_size):
        chunk = " ".join(sentences[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

chunks = chunk_text(transcript)

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(chunks)
embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]

# Normalize embeddings for cosine similarity
faiss.normalize_L2(embeddings)

index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

query = "How are neural networks trained?"

query_embedding = model.encode([query]).astype("float32")
faiss.normalize_L2(query_embedding)

distance,indices = index.search(query_embedding, k = 2)

print("User Query : " , query)
print("\n Top Matching Chunks : \n")

for idx in indices[0]:
    print("-",chunks[idx])
