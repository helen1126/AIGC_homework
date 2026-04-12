from fastapi import APIRouter

from app.models.schemas import (
    SDModelListResponse,
    LoRAModelListResponse,
    ModelInfo,
    SystemConfigResponse,
)
from app.services.model_manager import get_model_manager
from app.config import get_config
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/v1/models", tags=["模型管理"])


@router.get(
    "/sd",
    response_model=SDModelListResponse,
    summary="获取SD基础模型列表",
    description="返回系统中所有可用的Stable Diffusion基础模型",
)
async def list_sd_models() -> SDModelListResponse:
    model_manager = get_model_manager()
    models_data = model_manager.list_sd_models()
    models = [ModelInfo(**m) for m in models_data]
    default = model_manager.get_default_sd_model()

    return SDModelListResponse(
        models=models,
        default_model=default,
        total=len(models),
    )


@router.get(
    "/lora",
    response_model=LoRAModelListResponse,
    summary="获取LoRA模型列表",
    description="返回系统中所有可用的LoRA扩展模型",
)
async def list_lora_models() -> LoRAModelListResponse:
    model_manager = get_model_manager()
    models_data = model_manager.list_lora_models()
    models = [ModelInfo(**m) for m in models_data]
    default = model_manager.get_default_lora_model()

    return LoRAModelListResponse(
        models=models,
        default_model=default,
        total=len(models),
    )


@router.post(
    "/refresh",
    summary="刷新模型列表",
    description="重新扫描模型目录，更新可用模型列表和默认模型",
)
async def refresh_models() -> dict:
    logger = get_logger()
    logger.info("收到模型列表刷新请求")

    model_manager = get_model_manager()
    model_manager.refresh()

    return {
        "success": True,
        "message": "模型列表已刷新",
        "default_sd_model": model_manager.get_default_sd_model(),
        "default_lora_model": model_manager.get_default_lora_model(),
    }


@router.get(
    "/config",
    response_model=SystemConfigResponse,
    summary="获取系统配置",
    description="返回当前系统的配置信息，包括默认参数和存储设置",
)
async def get_system_config() -> SystemConfigResponse:
    config = get_config()
    gen_config = config.generation

    return SystemConfigResponse(
        generation_defaults={
            "width": gen_config.default_width,
            "height": gen_config.default_height,
            "num_inference_steps": gen_config.default_num_inference_steps,
            "guidance_scale": gen_config.default_guidance_scale,
            "seed": gen_config.default_seed,
            "scheduler": gen_config.default_scheduler,
        },
        storage_enabled=config.storage.enabled,
        storage_path=config.storage.path,
        sd_models_path=config.models.sd_base_path,
        lora_models_path=config.models.lora_base_path,
    )
