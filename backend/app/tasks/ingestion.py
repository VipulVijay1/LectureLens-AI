from app.core.celery_app import celery_app
from app.services.ingestion_service import ingest_video
from app.core.db import db


@celery_app.task(name="app.tasks.ingestion.process_video_task")
def process_video_task(video_id: str):

    try:
        db.update_one(
            {"video_id": video_id},
            {"$set": {"status": "processing"}},
            upsert=True
        )

        ingest_video(video_id)

        db.update_one(
            {"video_id": video_id},
            {"$set": {"status": "completed"}}
        )

    except Exception as e:

        db.update_one(
            {"video_id": video_id},
            {"$set": {"status": "failed"}}
        )

        raise e