from fastapi import APIRouter, HTTPException
from app.schemas.query_schema import QueryRequest, QueryResponse
from app.services.retrieval_service import retrieve

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("/", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        results = retrieve(
            video_id=request.video_id,
            query=request.query,
            top_k=request.top_k
        )

        return {
            "video_id": request.video_id,
            "results": results
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))