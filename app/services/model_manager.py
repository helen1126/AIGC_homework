import os
from pathlib import Path
from typing import Optional

from app.config import get_config
from app.utils.logger import get_logger
from app.utils.exceptions import ModelNotFoundError, NoModelAvailableError


class ModelManager:
    def __init__(self):
        self._config = get_config()
        self._logger = get_logger()
        self._default_sd_model: Optional[str] = None
        self._default_lora_model: Optional[str] = None
        self._init_defaults()

    def _init_defaults(self) -> None:
        if self._config.models.default_sd_model:
            self._default_sd_model = self._config.models.default_sd_model
        else:
            sd_models = self.list_sd_models()
            if sd_models:
                self._default_sd_model = sd_models[0]["name"]
                self._logger.info(f"未指定默认SD模型，自动选择第一个模型: {self._default_sd_model}")

        if self._config.models.default_lora_model:
            self._default_lora_model = self._config.models.default_lora_model
        else:
            self._default_lora_model = None

    def list_sd_models(self) -> list[dict]:
        sd_path = Path(self._config.models.sd_base_path)
        if not sd_path.exists():
            self._logger.warning(f"SD模型目录不存在: {sd_path}")
            return []

        models = []
        for item in sorted(sd_path.iterdir()):
            if self._is_valid_sd_model(item):
                models.append({
                    "name": item.name,
                    "path": str(item.resolve()),
                    "is_default": item.name == self._default_sd_model,
                })
        return models

    def list_lora_models(self) -> list[dict]:
        lora_path = Path(self._config.models.lora_base_path)
        if not lora_path.exists():
            self._logger.warning(f"LoRA模型目录不存在: {lora_path}")
            return []

        models = []
        for item in sorted(lora_path.iterdir()):
            if self._is_valid_lora_model(item):
                models.append({
                    "name": item.name,
                    "path": str(item.resolve()),
                    "is_default": item.name == self._default_lora_model,
                })
        return models

    def get_sd_model_path(self, model_name: Optional[str] = None) -> str:
        if model_name is None:
            if self._default_sd_model is None:
                raise NoModelAvailableError()
            model_name = self._default_sd_model

        sd_path = Path(self._config.models.sd_base_path) / model_name
        if not sd_path.exists():
            raise ModelNotFoundError(model_name, "SD")
        return str(sd_path.resolve())

    def get_lora_model_path(self, lora_name: Optional[str] = None) -> Optional[str]:
        if lora_name is None:
            if self._default_lora_model is None:
                return None
            lora_name = self._default_lora_model

        lora_path = Path(self._config.models.lora_base_path) / lora_name
        if not lora_path.exists():
            from app.utils.exceptions import LoRANotFoundError
            raise LoRANotFoundError(lora_name)
        return str(lora_path.resolve())

    def get_default_sd_model(self) -> Optional[str]:
        return self._default_sd_model

    def get_default_lora_model(self) -> Optional[str]:
        return self._default_lora_model

    def _is_valid_sd_model(self, path: Path) -> bool:
        if path.is_dir():
            config_file = path / "config.json"
            model_index = path / "model_index.json"
            if config_file.exists() or model_index.exists():
                return True
            safetensors = list(path.glob("*.safetensors"))
            bin_files = list(path.glob("*.bin"))
            if safetensors or bin_files:
                return True
        elif path.is_file():
            if path.suffix in (".safetensors", ".bin", ".ckpt"):
                return True
        return False

    def _is_valid_lora_model(self, path: Path) -> bool:
        if path.is_dir():
            adapter_config = path / "adapter_config.json"
            if adapter_config.exists():
                return True
            safetensors = list(path.glob("*.safetensors"))
            bin_files = list(path.glob("*.bin"))
            if safetensors or bin_files:
                return True
        elif path.is_file():
            if path.suffix in (".safetensors", ".bin", ".pt"):
                return True
        return False

    def refresh(self) -> None:
        self._config = get_config()
        self._default_sd_model = None
        self._default_lora_model = None
        self._init_defaults()
        self._logger.info("模型列表已刷新")


_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
