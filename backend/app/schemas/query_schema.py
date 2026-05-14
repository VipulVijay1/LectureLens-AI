from pydantic import BaseModel
from typing import List
from typing import Optional


class QueryRequest(BaseModel):
    video_id: str
    query: str
    top_k: int = 5


class Confidence(BaseModel):
    label: str
    badge: str
    score: int


class QueryResult(BaseModel):
    timestamp: str
    text: str
    score: float


class QueryResponse(BaseModel):
    video_id: str
    answer: str
    sources: List[QueryResult]
    confidence: Optional[Confidence] = None
    mode: Optional[str] = None