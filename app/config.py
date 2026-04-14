import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ModelsConfig(BaseModel):
    sd_base_path: str = "./models/sd"
    lora_base_path: str = "./models/lora"
    default_sd_model: str = ""
    default_lora_model: str = ""
    pipeline_config: str = ""
    offline_mode: bool = False


class GenerationConfig(BaseModel):
    default_width: int = Field(default=512, ge=64, le=2048)
    default_height: int = Field(default=512, ge=64, le=2048)
    default_num_inference_steps: int = Field(default=20, ge=1, le=150)
    default_guidance_scale: float = Field(default=7.5, ge=1.0, le=30.0)
    default_seed: int = Field(default=-1, description="-1表示随机种子")
    default_scheduler: str = "euler"


class AnimeAvatarConfig(BaseModel):
    default_style: str = Field(default="japanese")
    default_resolution: str = Field(default="medium")
    default_quality_mode: str = Field(default="balanced")
    cache_enabled: bool = Field(default=True)
    cache_max_size: int = Field(default=100, ge=10, le=1000)
    history_max_size: int = Field(default=1000, ge=100, le=10000)
    max_generation_time: float = Field(default=10.0, ge=5.0, le=30.0)


class StorageConfig(BaseModel):
    enabled: bool = True
    path: str = "./output"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "./logs/app.log"


class AppConfig(BaseModel):
    server: ServerConfig = ServerConfig()
    models: ModelsConfig = ModelsConfig()
    generation: GenerationConfig = GenerationConfig()
    anime_avatar: AnimeAvatarConfig = AnimeAvatarConfig()
    storage: StorageConfig = StorageConfig()
    logging: LoggingConfig = LoggingConfig()


_config_instance: Optional[AppConfig] = None


def load_config(config_path: str = "config.yaml") -> AppConfig:
    global _config_instance
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        _config_instance = AppConfig(**raw)
    else:
        _config_instance = AppConfig()
    _ensure_directories(_config_instance)
    return _config_instance


def get_config() -> AppConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance


def reload_config(config_path: str = "config.yaml") -> AppConfig:
    return load_config(config_path)


def _ensure_directories(config: AppConfig) -> None:
    os.makedirs(config.models.sd_base_path, exist_ok=True)
    os.makedirs(config.models.lora_base_path, exist_ok=True)
    if config.storage.enabled:
        os.makedirs(config.storage.path, exist_ok=True)
    log_dir = os.path.dirname(config.logging.file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
