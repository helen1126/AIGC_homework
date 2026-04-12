from fastapi import APIRouter, Query

from app.models.schemas import (
    GenerationRequest,
    GenerationResponse,
)
from app.services.sd_service import get_sd_service
from app.services.model_manager import get_model_manager
from app.config import get_config
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/v1/generation", tags=["图片生成"])


@router.post(
    "/text2img",
    response_model=GenerationResponse,
    summary="文本生成图片",
    description="根据文本提示词生成图片，支持SD基础模型和LoRA扩展",
)
async def text_to_image(request: GenerationRequest) -> GenerationResponse:
    logger = get_logger()
    logger.info(f"收到图片生成请求: {request.prompt[:50]}...")

    sd_service = get_sd_service()
    params = request.model_dump(exclude_none=False)

    result = sd_service.generate(params)

    return GenerationResponse(**result)


@router.post(
    "/text2img/simple",
    response_model=GenerationResponse,
    summary="简单文本生成图片",
    description="仅需提供提示词即可生成图片，其余参数使用默认值",
)
async def simple_text_to_image(
    prompt: str = Query(..., min_length=1, max_length=2000, description="正向提示词"),
    negative_prompt: str = Query(default="", max_length=2000, description="反向提示词"),
    sd_model: str = Query(default=None, description="SD模型名称"),
    lora_model: str = Query(default=None, description="LoRA模型名称"),
) -> GenerationResponse:
    logger = get_logger()
    logger.info(f"收到简单图片生成请求: {prompt[:50]}...")

    sd_service = get_sd_service()
    params = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
    }
    if sd_model:
        params["sd_model"] = sd_model
    if lora_model:
        params["lora_model"] = lora_model

    result = sd_service.generate(params)

    return GenerationResponse(**result)
