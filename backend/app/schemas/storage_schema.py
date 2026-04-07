from pydantic import BaseModel

class SaveContentRequest(BaseModel):
    video_id: str
    type: str   # "notes" or "flashcard"
    content: str