from fastapi import APIRouter, HTTPException
import os
import json

from app.core.config import DATA_DIR
from app.services.retrieval_service import retrieve
from app.services.learning_service import structure_summary

router = APIRouter()


@router.post("/notes")
def get_notes(video_id: str, query: str):
    try:
        video_path = os.path.join(DATA_DIR, video_id)

        if not os.path.exists(video_path):
            raise HTTPException(status_code=400, detail="Video not ingested")

        # 🔥 Step 1: Retrieve answer (summary)
        result = retrieve(video_id, query)
        summary = result["answer"]

        if not summary:
            raise HTTPException(status_code=400, detail="No summary generated")

        # 🔥 Step 2: Structure summary
        notes = structure_summary(summary)

        return {
            "video_id": video_id,
            "notes": notes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))