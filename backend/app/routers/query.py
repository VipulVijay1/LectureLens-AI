from fastapi import APIRouter, HTTPException

from app.schemas.query_schema import QueryRequest, QueryResponse
from app.services.retrieval_service import retrieve
from app.services.rag_service import fallback_answer
from app.tasks.ingestion import process_video_task
from app.core.db import db

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
def query(request: QueryRequest):

    video_id = request.video_id

    try:
        video = db.find_one({"video_id": video_id})

        # ✅ CASE 1: Fully processed → Full RAG
        if video and video.get("status") == "completed":

            rag_output = retrieve(
                video_id=video_id,
                query=request.query,
                top_k=request.top_k
            )

            return {
                "video_id": video_id,
                "answer": rag_output["answer"],
                "sources": rag_output["sources"],
                "confidence": rag_output.get("confidence"),
                "mode": "full_rag"
            }

        # ✅ CASE 2: Not processed / processing / failed
        else:

            # trigger ingestion ONLY first time
            if not video:

                db.insert_one({
                    "video_id": video_id,
                    "status": "queued"
                })

                process_video_task.delay(video_id)

            # ✅ fallback answer always
            fallback_output = fallback_answer(
                video_id=video_id,
                query=request.query
            )

            return {
                "video_id": video_id,
                "answer": fallback_output["answer"],
                "sources": fallback_output.get("sources", []),
                "confidence": None,
                "mode": "fallback_processing"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))