from fastapi import APIRouter

from app.services.document_service import search_service

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def get_metrics():

    coordinator = search_service.coordinator

    total_requests = (
        coordinator.cache_hits
        + coordinator.cache_misses
    )

    cache_hit_rate = (
        coordinator.cache_hits / total_requests
        if total_requests > 0
        else 0
    )

    return {
        "cache_hits": coordinator.cache_hits,
        "cache_misses": coordinator.cache_misses,
        "total_requests": total_requests,
        "cache_hit_rate": round(cache_hit_rate, 4),
    }