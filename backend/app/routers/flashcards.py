from fastapi import APIRouter
from app.services.learning_service import generate_flashcards
import json
import os
from app.core.config import DATA_DIR

router = APIRouter()

@router.post("/flashcards")
def get_flashcards(video_id: str):
    video_path = os.path.join(DATA_DIR, video_id)
    chunks_path = os.path.join(video_path, "chunks.json")

    if not os.path.exists(chunks_path):
        return {"error": "Video not ingested"}

    with open(chunks_path, "r") as f:
        chunks = json.load(f)

    flashcards = generate_flashcards(chunks)

    return {
        "video_id": video_id,
        "flashcards": flashcards
    }