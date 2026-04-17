import os
from contextlib import asynccontextmanager

import app.utils.compat
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import load_config, get_config
from app.utils.logger import setup_logger, get_logger
from app.utils.exceptions import SDAPIException, ERROR_CODES
from app.routers import generation, model_management
from app.routers import avatar, history
from app.models.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    logger = setup_logger()
    logger.info("AI动漫头像生成服务启动中...")
    logger.info(f"SD模型目录: {config.models.sd_base_path}")
    logger.info(f"LoRA模型目录: {config.models.lora_base_path}")
    logger.info(f"本地暂存: {'启用' if config.storage.enabled else '禁用'}")
    if config.storage.enabled:
        logger.info(f"暂存路径: {config.storage.path}")

    from app.services.model_manager import get_model_manager
    mm = get_model_manager()
    logger.info(f"默认SD模型: {mm.get_default_sd_model() or '无'}")
    logger.info(f"默认LoRA模型: {mm.get_default_lora_model() or '无'}")

    from app.services.style_manager import get_style_manager
    sm = get_style_manager()
    available_styles = sm.get_style_ids()
    logger.info(f"可用动漫风格: {', '.join(available_styles)}")

    from app.services.anime_avatar_service import get_anime_avatar_service
    avatar_service = get_anime_avatar_service()
    logger.info("AI动漫头像生成服务启动完成")

    yield

    logger.info("AI动漫头像生成服务关闭中...")
    from app.services.sd_service import get_sd_service
    sd_service = get_sd_service()
    sd_service.unload_current_model()
    logger.info("AI动漫头像生成服务已关闭")


app = FastAPI(
    title="AI动漫头像生成服务",
    description="基于FastAPI的AI动漫头像生成后端服务，支持多种动漫风格、角色自定义和智能缓存",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation.router)
app.include_router(model_management.router)
app.include_router(avatar.router)
app.include_router(history.router)


@app.exception_handler(SDAPIException)
async def sd_api_exception_handler(request: Request, exc: SDAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger = get_logger()
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": f"服务器内部错误: {str(exc)}",
        },
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务是否正常运行",
    tags=["系统"],
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="2.0.0")


config = get_config()
if config.storage.enabled and os.path.exists(config.storage.path):
    app.mount("/images", StaticFiles(directory=config.storage.path), name="images")

_demo_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo")
if os.path.isdir(_demo_dir):
    app.mount("/demo", StaticFiles(directory=_demo_dir, html=True), name="demo")

_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/frontend", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
