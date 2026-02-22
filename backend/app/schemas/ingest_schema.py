from pydantic import BaseModel

class IngestRequest(BaseModel):
    video_id: str

class IngestResponse(BaseModel):
    message: str
    video_id: str
    status: str