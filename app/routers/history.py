from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.anime_schemas import (
    HistoryListResponse,
    CacheStatsResponse,
    ClearCacheResponse
)
from app.services.anime_avatar_service import get_anime_avatar_service


router = APIRouter(
    prefix="/api/v1",
    tags=["历史记录与缓存"]
)


@router.get(
    "/history",
    response_model=HistoryListResponse,
    summary="获取生成历史记录",
    description="查询用户的动漫头像生成历史记录，支持分页和用户筛选"
)
async def get_generation_history(
    user_id: Optional[str] = Query(
        default=None,
        description="用户ID，不传则返回所有用户记录"
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="每页返回的记录数量"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="偏移量，用于分页"
    )
) -> HistoryListResponse:
    try:
        service = get_anime_avatar_service()
        result = service.get_generation_history(
            user_id=user_id or "all",
            limit=limit,
            offset=offset
        )
        return HistoryListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.delete(
    "/history",
    summary="清除历史记录",
    description="清除指定用户或所有用户的生成历史记录"
)
async def clear_history(
    user_id: Optional[str] = Query(
        default=None,
        description="要清除的用户ID，不传则清除所有记录"
    )
) -> dict:
    try:
        service = get_anime_avatar_service()
        removed_count = service.clear_history(user_id=user_id)
        return {
            "success": True,
            "cleared_count": removed_count,
            "message": f"已成功清除 {removed_count} 条历史记录"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除历史记录失败: {str(e)}")


@router.get(
    "/cache/stats",
    response_model=CacheStatsResponse,
    summary="获取缓存统计信息",
    description="查看当前缓存和历史记录的使用情况"
)
async def get_cache_stats() -> CacheStatsResponse:
    try:
        service = get_anime_avatar_service()
        return CacheStatsResponse(
            cache_size=len(service._cache),
            cache_max_size=service._cache_max_size,
            history_size=len(service._generation_history),
            history_max_size=service._history_max_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")


@router.delete(
    "/cache",
    response_model=ClearCacheResponse,
    summary="清除缓存",
    description="清除所有缓存的生成结果，释放内存空间"
)
async def clear_cache() -> ClearCacheResponse:
    try:
        service = get_anime_avatar_service()
        cleared_count = service.clear_cache()
        return ClearCacheResponse(
            success=True,
            cleared_count=cleared_count,
            message=f"已成功清除 {cleared_count} 条缓存记录"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")