from fastapi import APIRouter, HTTPException
import os
import json

from app.core.config import DATA_DIR
from app.services.learning_service import generate_lecture_notes

router = APIRouter()


@router.post("/notes")
def get_notes(video_id: str):
    try:
        # Path setup
        video_path = os.path.join(DATA_DIR, video_id)
        chunks_path = os.path.join(video_path, "chunks.json")

        # Check if video ingested
        if not os.path.exists(video_path):
            raise HTTPException(status_code=400, detail="Video not ingested")

        if not os.path.exists(chunks_path):
            raise HTTPException(status_code=400, detail="Chunks not found")

        # Load chunks
        with open(chunks_path, "r") as f:
            chunks = json.load(f)

        if not chunks:
            raise HTTPException(status_code=400, detail="No content available")

        # Generate notes
        notes = generate_lecture_notes(chunks)

        return {
            "video_id": video_id,
            "notes": notes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))