from typing import Optional

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    chunk_id: str
    text: str
    source_file: str
    page: Optional[int] = None


class UploadResponse(BaseModel):
    filename: str
    status: str
    chunk_count: int
    chunks: list[Chunk]


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResult(BaseModel):
    chunk_id: str
    text: str
    source_file: str
    page: Optional[int] = None
    score: float
    semantic_score: float
    keyword_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]