from fastapi import APIRouter

from models.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult
)

from api.upload import search_service


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.post("", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest
):
    results = search_service.search(
        query=request.query,
        top_k=request.top_k
    )

    return SearchResponse(
        query=request.query,
        results=[
            SearchResult(**result)
            for result in results
        ]
    )
