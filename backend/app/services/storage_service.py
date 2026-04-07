from app.core.db import notes_collection
from datetime import datetime


def save_content(data):
    document = {
        "video_id": data.video_id,
        "type": data.type,
        "content": data.content,
        "created_at": datetime.utcnow()
    }

    notes_collection.insert_one(document)

    return {"message": "Saved successfully"}


def get_saved_content(video_id: str, content_type: str):
    results = notes_collection.find(
        {"video_id": video_id, "type": content_type},
        {"_id": 0}
    )

    return list(results)