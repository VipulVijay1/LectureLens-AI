from fastapi import APIRouter
import json
import os
from app.core.config import DATA_DIR
from app.services.retrieval_service import retrieve
from app.services.learning_service import generate_flashcards_from_chunks

router = APIRouter()

@router.post("/flashcards")
def get_flashcards(video_id: str, query: str):
    try:
        result = retrieve(video_id, query, top_k=10)
        top_chunks = result["sources"]

        if not top_chunks or len(top_chunks) < 2:
            return {
                "flashcards": "Not enough relevant content for this topic."
            }

        flashcards = generate_flashcards_from_chunks(top_chunks)

        return {
            "video_id": video_id,
            "flashcards": flashcards
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))