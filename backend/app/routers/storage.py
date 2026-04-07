from fastapi import APIRouter
from app.schemas.storage_schema import SaveContentRequest
from app.services.storage_service import save_content, get_saved_content

router = APIRouter()

@router.post("/save")
def save(data: SaveContentRequest):
    return save_content(data)


@router.get("/saved")
def get_saved(video_id: str, type: str):
    return get_saved_content(video_id, type)