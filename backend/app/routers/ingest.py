from fastapi import APIRouter, HTTPException
from app.schemas.ingest_schema import IngestRequest, IngestResponse
from app.tasks.ingestion import process_video_task
from app.core.db import db

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/", response_model=IngestResponse)
def ingest(request: IngestRequest):

    video_id = request.video_id

    try:
        existing = db.find_one({"video_id": video_id})

        # already running/completed
        if existing and existing.get("status") in ["queued", "processing", "completed"]:
            return {
                "message": "Video already queued or processed.",
                "video_id": video_id,
                "status": existing["status"]
            }

        # insert/update status
        db.update_one(
            {"video_id": video_id},
            {"$set": {"status": "queued"}},
            upsert=True
        )

        # celery trigger
        print("TASK DISPATCH STARTED")
        process_video_task.delay(video_id)
        print("TASK SENT TO REDIS")
        
        return {
            "message": "Ingestion started.",
            "video_id": video_id,
            "status": "queued"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/status/{video_id}")
def get_ingestion_status(video_id: str):

    video = db.find_one({"video_id": video_id})

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Video not found"
        )

    return {
        "video_id": video_id,
        "status": video.get("status", "unknown")
    }