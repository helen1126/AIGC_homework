from fastapi import APIRouter, Query
from typing import Optional

from app.services.anime_avatar_service import get_anime_avatar_service

router = APIRouter(prefix="/api/v1/history", tags=["历史记录"])


@router.get("")
async def get_history(
    user_id: Optional[str] = Query(None, description="用户ID筛选"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
):
    service = get_anime_avatar_service()
    return service.get_generation_history(user_id=user_id, limit=limit, offset=offset)


@router.delete("")
async def clear_history(
    user_id: Optional[str] = Query(None, description="用户ID，不指定则清除全部"),
):
    service = get_anime_avatar_service()
    cleared_count = service.clear_history(user_id=user_id)
    return {
        "success": True,
        "message": f"已清除 {cleared_count} 条历史记录",
        "cleared_count": cleared_count,
    }
