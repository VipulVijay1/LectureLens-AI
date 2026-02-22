from fastapi import APIRouter, HTTPException
from app.schemas.ingest_schema import IngestRequest, IngestResponse
from app.services.ingestion_service import ingest_video

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/", response_model=IngestResponse)
def ingest(request: IngestRequest):
    try:
        result = ingest_video(request.video_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))