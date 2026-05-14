import os
import json
import shutil
import numpy as np
import faiss
import nltk

# Download NLTK data quietly if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

from nltk.tokenize import sent_tokenize
from youtube_transcript_api import YouTubeTranscriptApi

from app.core.config import DATA_DIR
from app.core.logger import logger
from app.core.model_loader import model_loader


transcript_cache = {}
chunk_cache = {}

def seconds_to_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def fetch_transcript(video_id):
    """Fetch transcript with caching"""
    
    # ✅ CACHE CHECK
    if video_id in transcript_cache:
        logger.info(f"Transcript cache hit for {video_id}")
        return transcript_cache[video_id]

    try:
        logger.debug(f"Calling fetch with video_id={video_id}")
        
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                transcript = transcript_list.find_transcript(['en'])

        if not transcript:
            raise Exception("No transcript found")

        fetched_transcript = transcript.fetch()
        raw_data = fetched_transcript.to_raw_data()

        formatted_transcript = []
        for entry in raw_data:
            formatted_transcript.append({
                "timestamp": seconds_to_timestamp(entry['start']),
                "text": entry['text'],
                "start": entry['start'],
                "duration": entry['duration']
            })

        # ✅ STORE IN CACHE
        transcript_cache[video_id] = formatted_transcript

        logger.info(f"Fetched {len(formatted_transcript)} entries for {video_id}")
        return formatted_transcript

    except Exception as e:
        logger.error(f"Error fetching transcript: {str(e)}")
        raise

def semantic_chunk(transcript_data, video_id, max_sentences=5, overlap=2):
    """Chunk transcript into semantic segments with caching"""

    # ✅ CACHE CHECK
    if video_id in chunk_cache:
        logger.info(f"Chunk cache hit for {video_id}")
        return chunk_cache[video_id]

    if not transcript_data:
        raise Exception("No transcript data")

    sentences = []

    for entry in transcript_data:
        if not entry.get("text"):
            continue

        split_sentences = sent_tokenize(entry["text"])
        for sent in split_sentences:
            if sent.strip():
                sentences.append({
                    "text": sent.strip(),
                    "timestamp": entry["timestamp"]
                })

    chunks = []
    i = 0

    while i < len(sentences):
        chunk_sentences = sentences[i:i + max_sentences]

        if chunk_sentences:
            chunk_text = " ".join([s["text"] for s in chunk_sentences])
            chunk_timestamp = chunk_sentences[0]["timestamp"]

            chunks.append({
                "text": chunk_text,
                "timestamp": chunk_timestamp,
                "video_id": video_id
            })

        i += max_sentences - overlap

    # ✅ STORE IN CACHE
    chunk_cache[video_id] = chunks

    logger.info(f"Created {len(chunks)} chunks")
    return chunks


def get_chunks_for_video(video_id):
    """
    Used by fallback pipeline.
    Avoids recomputation.
    """

    transcript = fetch_transcript(video_id)
    chunks = semantic_chunk(transcript, video_id)

    return chunks



def artifacts_valid(video_path):
    """Check if all required artifacts exist"""
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
    """Main ingestion function with comprehensive error handling"""
    video_path = os.path.join(DATA_DIR, video_id)
    logger.info(f"Ingestion started for video {video_id}")

    try:
        # Check cache
        if os.path.exists(video_path):
            if artifacts_valid(video_path):
                logger.info(f"Video {video_id} already ingested.")
                return {
                    "message": "Video already ingested.",
                    "video_id": video_id,
                    "status": "cached"
                }
            else:
                logger.warning(f"Corrupted data. Rebuilding {video_id}")
                shutil.rmtree(video_path)

        os.makedirs(video_path, exist_ok=True)

        # -----------------------------
        # Fetch Transcript
        # -----------------------------
        logger.info(f"Fetching transcript for {video_id}")
        transcript_data = fetch_transcript(video_id)
        
        if not transcript_data:
            raise Exception("No transcript data received")
        
        logger.info(f"Retrieved {len(transcript_data)} transcript entries")

        # -----------------------------
        # Chunking
        # -----------------------------
        logger.info(f"Chunking transcript for {video_id}")
        chunks = semantic_chunk(transcript_data, video_id)
        
        if not chunks:
            raise Exception("No chunks created")
        
        texts = [chunk["text"] for chunk in chunks]
        logger.info(f"Created {len(chunks)} chunks")

        # -----------------------------
        # Generate Embeddings
        # -----------------------------
        logger.info(f"Generating embeddings for {video_id}")
        try:
            embeddings = model_loader.embedding_model.encode(texts)
            embeddings = np.array(embeddings).astype("float32")
            faiss.normalize_L2(embeddings)

            # ✅ ADD THIS BLOCK (CRITICAL FOR MMR)
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i].tolist()

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")
        # -----------------------------
        # Create FAISS Index
        # -----------------------------
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        logger.info(f"Created FAISS index with dimension {dimension}")

        # -----------------------------
        # Save artifacts
        # -----------------------------
        try:
            np.save(os.path.join(video_path, "embeddings.npy"), embeddings)
            faiss.write_index(index, os.path.join(video_path, "index.faiss"))
            
            with open(os.path.join(video_path, "chunks.json"), "w", encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved artifacts to {video_path}")
        except Exception as e:
            logger.error(f"Error saving artifacts: {str(e)}")
            raise Exception(f"Failed to save artifacts: {str(e)}")

        logger.info(f"Ingestion successful for video {video_id}")
        
        return {
            "message": "Video ingested successfully.",
            "video_id": video_id,
            "status": "ingested",
            "chunks_count": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Ingestion failed for video {video_id}: {str(e)}")
        
        # Clean up failed ingestion
        if os.path.exists(video_path):
            try:
                shutil.rmtree(video_path)
                logger.info(f"Cleaned up failed ingestion for {video_id}")
            except:
                pass
        
        # Re-raise the exception so the API returns a 500 error
        raise