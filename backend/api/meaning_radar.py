from fastapi import APIRouter, Query

from api.upload import search_service
from services.meaning_radar_service import MeaningRadarService


router = APIRouter(
    prefix="/meaning-radar",
    tags=["Meaning Radar"]
)

meaning_radar_service = MeaningRadarService()


@router.get("")
async def get_meaning_radar(
    query: str | None = Query(
        default=None,
        max_length=1000
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100
    )
):
    return meaning_radar_service.build_radar(
        chunks=search_service.chunks,
        query=query,
        limit=limit
    )
