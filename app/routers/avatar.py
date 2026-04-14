from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.anime_schemas import (
    AvatarGenerationRequest,
    AvatarGenerationResponse,
    StyleListResponse,
    CharacterFeaturesResponse,
    ResolutionPresetsResponse
)
from app.services.anime_avatar_service import get_anime_avatar_service
from app.utils.exceptions import SDAPIException, GenerationError


router = APIRouter(
    prefix="/api/v1",
    tags=["动漫头像生成"]
)


@router.post(
    "/avatar/generate",
    response_model=AvatarGenerationResponse,
    summary="生成动漫头像",
    description="根据指定的风格、角色特征和参数生成动漫风格的头像图片"
)
async def generate_avatar(request: AvatarGenerationRequest) -> AvatarGenerationResponse:
    try:
        service = get_anime_avatar_service()
        
        params = {
            "description": request.description,
            "style": request.style,
            "resolution": request.resolution,
            "quality_mode": request.quality_mode,
            "seed": request.seed if request.seed is not None else -1,
            "user_id": request.user_id or "anonymous",
            "model": request.model,
            "lora": request.lora,
            "lora_weight": request.lora_weight,
        }
        
        if request.character_features:
            params["character_features"] = {
                k: v for k, v in request.character_features.dict().items() 
                if v is not None
            }
        
        if request.reference_image:
            params["reference_image"] = request.reference_image
        
        result = service.generate_avatar(params)
        
        return AvatarGenerationResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get(
    "/avatar/styles",
    response_model=StyleListResponse,
    summary="获取可用动漫风格列表",
    description="获取系统支持的所有动漫风格及其详细信息"
)
async def get_available_styles() -> StyleListResponse:
    try:
        service = get_anime_avatar_service()
        styles = service.get_available_styles()
        return StyleListResponse(styles=styles, total=len(styles))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取风格列表失败: {str(e)}")


@router.get(
    "/avatar/features",
    response_model=CharacterFeaturesResponse,
    summary="获取角色特征选项",
    description="获取可自定义的角色特征分类及各选项列表"
)
async def get_character_features() -> CharacterFeaturesResponse:
    try:
        service = get_anime_avatar_service()
        features = service.get_character_feature_options()
        return CharacterFeaturesResponse(features=features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色特征失败: {str(e)}")


@router.get(
    "/avatar/resolutions",
    response_model=ResolutionPresetsResponse,
    summary="获取分辨率预设列表",
    description="获取支持的分辨率预设选项及其详细配置"
)
async def get_resolution_presets() -> ResolutionPresetsResponse:
    try:
        service = get_anime_avatar_service()
        presets = service.get_resolution_presets()
        return ResolutionPresetsResponse(presets=presets, total=len(presets))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分辨率预设失败: {str(e)}")