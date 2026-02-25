from pydantic import BaseModel
from typing import List


class QueryRequest(BaseModel):
    video_id: str
    query: str
    top_k: int = 5


class QueryResult(BaseModel):
    timestamp: str
    text: str
    score: float


class QueryResponse(BaseModel):
    video_id: str
    results: List[QueryResult]