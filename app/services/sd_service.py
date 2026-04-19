import base64
import io
import random
import time
from typing import Optional

from app.config import get_config
from app.services.model_manager import get_model_manager
from app.utils.logger import get_logger
from app.utils.exceptions import GenerationError, StorageError


SCHEDULER_MAP = {
    "euler": "EulerDiscreteScheduler",
    "euler_a": "EulerAncestralDiscreteScheduler",
    "dpm++2m": "DPMSolverMultistepScheduler",
    "dpm++2m_karras": "DPMSolverMultistepScheduler",
    "ddim": "DDIMScheduler",
    "lms": "LMSDiscreteScheduler",
    "pndm": "PNDMScheduler",
}


class SDService:
    def __init__(self):
        self._config = get_config()
        self._logger = get_logger()
        self._model_manager = get_model_manager()
        self._current_pipeline = None
        self._current_model_name: Optional[str] = None
        self._current_lora_name: Optional[str] = None
        self._device = self._detect_device()
        self._logger.info(f"SD服务初始化，设备: {self._device}")

    def _detect_device(self) -> str:
        try:
            import torch
            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                self._logger.info(f"检测到CUDA设备: {device_name}")
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self._logger.info("检测到Apple MPS设备")
                return "mps"
        except ImportError:
            pass
        self._logger.warning("未检测到GPU，将使用CPU运行（速度较慢）")
        return "cpu"

    def _get_torch_dtype(self):
        import torch
        if self._device == "cuda":
            return torch.float16
        return torch.float32

    def generate(self, params: dict) -> dict:
        prompt = params["prompt"]
        negative_prompt = params.get("negative_prompt", "")
        width = params.get("width") or self._config.generation.default_width
        height = params.get("height") or self._config.generation.default_height
        num_inference_steps = (
            params.get("num_inference_steps")
            or self._config.generation.default_num_inference_steps
        )
        guidance_scale = (
            params.get("guidance_scale")
            or self._config.generation.default_guidance_scale
        )
        seed = params.get("seed") if params.get("seed") is not None else self._config.generation.default_seed
        sd_model = params.get("sd_model")
        lora_model = params.get("lora_model")
        lora_weight = params.get("lora_weight", 1.0)
        scheduler = params.get("scheduler") or self._config.generation.default_scheduler

        if seed == -1 or seed is None:
            seed = random.randint(0, 2**32 - 1)

        sd_model_path = self._model_manager.get_sd_model_path(sd_model)
        actual_sd_model = sd_model or self._model_manager.get_default_sd_model()

        self._logger.info(
            f"开始生成图片 - 模型: {actual_sd_model}, "
            f"LoRA: {lora_model or '无'}, "
            f"提示词: {prompt[:50]}..., "
            f"尺寸: {width}x{height}, 步数: {num_inference_steps}, 种子: {seed}, "
            f"设备: {self._device}"
        )

        try:
            pipeline = self._load_pipeline(sd_model_path, actual_sd_model, lora_model, lora_weight)
            pipeline = self._apply_scheduler(pipeline, scheduler)

            import torch
            generator = torch.Generator(device=self._device).manual_seed(seed)

            start_time = time.time()
            image = pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
            ).images[0]
            elapsed = time.time() - start_time

            self._logger.info(f"图片生成完成，耗时: {elapsed:.2f}秒")

            image_base64 = self._image_to_base64(image)
            image_url = None

            if self._config.storage.enabled:
                image_url = self._save_image(image, seed, actual_sd_model)

            actual_params = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "seed": seed,
                "sd_model": actual_sd_model,
                "lora_model": lora_model,
                "lora_weight": lora_weight,
                "scheduler": scheduler,
            }

            return {
                "success": True,
                "image_base64": image_base64,
                "image_url": image_url,
                "seed": seed,
                "parameters": actual_params,
            }

        except (GenerationError, StorageError):
            raise
        except Exception as e:
            self._logger.error(f"图片生成失败: {str(e)}", exc_info=True)
            raise GenerationError(str(e))

    def _detect_model_type(self, model_path: str) -> str:
        import os
        model_name = os.path.basename(model_path).lower()
        if "sdxl" in model_name:
            return "sdxl"
        try:
            file_size = os.path.getsize(model_path) if os.path.isfile(model_path) else 0
            if file_size > 4 * 1024 * 1024 * 1024:
                return "sdxl"
        except OSError:
            pass
        return "sd"

    def _get_pipeline_class(self, model_type: str):
        if model_type == "sdxl":
            from diffusers import StableDiffusionXLPipeline
            return StableDiffusionXLPipeline
        from diffusers import StableDiffusionPipeline
        return StableDiffusionPipeline

    def _load_pipeline(self, model_path: str, model_name: str,
                       lora_name: Optional[str], lora_weight: float):
        self._patch_transformers_torch_check()
        import torch
        import os

        need_reload = (
            self._current_pipeline is None
            or self._current_model_name != model_name
            or self._current_lora_name != lora_name
        )

        if need_reload:
            self._logger.info(f"加载SD模型: {model_path}")
            try:
                is_single_file = os.path.isfile(model_path)
                model_type = self._detect_model_type(model_path)
                PipelineClass = self._get_pipeline_class(model_type)
                self._logger.info(f"检测到模型类型: {model_type}，使用 {PipelineClass.__name__}")

                torch_dtype = self._get_torch_dtype()

                if is_single_file:
                    self._current_pipeline = self._load_single_file_pipeline(
                        PipelineClass, model_path, model_type, torch_dtype
                    )
                else:
                    self._current_pipeline = PipelineClass.from_pretrained(
                        model_path,
                        torch_dtype=torch_dtype,
                    )

                self._current_pipeline = self._current_pipeline.to(self._device)
                self._logger.info(f"模型已加载到设备: {self._device}")

                if self._device == "cuda":
                    try:
                        self._current_pipeline.enable_attention_slicing()
                        self._logger.info("已启用注意力切片优化")
                    except Exception:
                        pass

            except Exception as e:
                self._logger.error(f"模型加载失败: {str(e)}")
                raise GenerationError(f"模型加载失败: {str(e)}")

            self._current_model_name = model_name
            self._current_lora_name = None

            if lora_name:
                self._load_lora(lora_name, lora_weight)

        elif lora_name and self._current_lora_name != lora_name:
            self._unload_lora()
            self._load_lora(lora_name, lora_weight)

        return self._current_pipeline

    def _load_single_file_pipeline(self, PipelineClass, model_path: str, model_type: str, torch_dtype):
        pipeline_config = self._config.models.pipeline_config
        offline_mode = self._config.models.offline_mode

        if pipeline_config:
            self._logger.info(f"使用指定配置源: {pipeline_config}")
            return PipelineClass.from_single_file(
                model_path,
                torch_dtype=torch_dtype,
                config=pipeline_config,
            )

        if offline_mode:
            self._logger.info("离线模式：仅使用本地缓存")
            return PipelineClass.from_single_file(
                model_path,
                torch_dtype=torch_dtype,
                local_files_only=True,
            )

        for attempt in range(3):
            try:
                self._logger.info(f"尝试加载模型（第{attempt + 1}次）...")
                return PipelineClass.from_single_file(
                    model_path,
                    torch_dtype=torch_dtype,
                )
            except Exception as e:
                if attempt < 2:
                    self._logger.warning(f"第{attempt + 1}次加载失败: {str(e)}，正在重试...")
                    time.sleep(2 * (attempt + 1))
                else:
                    self._logger.warning("在线加载失败，尝试使用本地缓存...")
                    try:
                        return PipelineClass.from_single_file(
                            model_path,
                            torch_dtype=torch_dtype,
                            local_files_only=True,
                        )
                    except Exception as fallback_err:
                        raise GenerationError(
                            f"模型加载失败（在线和离线均失败）。"
                            f"在线错误: {str(e)}；离线错误: {str(fallback_err)}。"
                            f"请在config.yaml中设置models.pipeline_config为对应的HuggingFace模型ID"
                            f"（如SDXL: 'stabilityai/stable-diffusion-xl-base-1.0'，"
                            f"SD1.5: 'runwayml/stable-diffusion-v1-5'），"
                            f"或确保网络连接正常后重试。"
                        )

    def _load_lora(self, lora_name: str, lora_weight: float) -> None:
        import os

        lora_path = self._model_manager.get_lora_model_path(lora_name)
        if lora_path is None:
            return

        self._logger.info(f"加载LoRA模型: {lora_path}, 权重: {lora_weight}")
        try:
            is_single_file = os.path.isfile(lora_path)
            if is_single_file:
                self._current_pipeline.load_lora_weights(lora_path, weight_name=os.path.basename(lora_path))
            else:
                self._current_pipeline.load_lora_weights(lora_path)
            self._current_lora_name = lora_name
            if lora_weight != 1.0:
                self._set_lora_scale(lora_weight)
        except Exception as e:
            self._logger.error(f"LoRA加载失败: {str(e)}")
            raise GenerationError(f"LoRA加载失败: {str(e)}")

    def _unload_lora(self) -> None:
        if self._current_lora_name and self._current_pipeline:
            self._logger.info("卸载当前LoRA模型")
            try:
                self._current_pipeline.unload_lora_weights()
            except Exception:
                pass
            self._current_lora_name = None

    def _set_lora_scale(self, scale: float) -> None:
        try:
            self._current_pipeline.fuse_lora(lora_scale=scale)
        except Exception:
            self._logger.warning("设置LoRA缩放失败，使用默认权重")

    def _apply_scheduler(self, pipeline, scheduler_name: str):
        scheduler_class_name = SCHEDULER_MAP.get(scheduler_name.lower())
        if scheduler_class_name is None:
            self._logger.warning(f"未知采样器: {scheduler_name}，使用默认采样器")
            return pipeline

        try:
            import importlib
            module = importlib.import_module("diffusers")
            scheduler_class = getattr(module, scheduler_class_name)

            if scheduler_name.lower() == "dpm++2m_karras":
                scheduler = scheduler_class.from_config(
                    pipeline.scheduler.config, use_karras_sigmas=True
                )
            else:
                scheduler = scheduler_class.from_config(pipeline.scheduler.config)

            pipeline.scheduler = scheduler
            self._logger.info(f"已切换采样器: {scheduler_name}")
        except Exception as e:
            self._logger.warning(f"采样器切换失败: {str(e)}，使用默认采样器")

        return pipeline

    def _image_to_base64(self, image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def _save_image(self, image, seed: int, model_name: str) -> str:
        import os
        from datetime import datetime

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{model_name}_{timestamp}_{seed}.png"
            filename = filename.replace("/", "_").replace("\\", "_")
            filepath = os.path.join(self._config.storage.path, filename)
            image.save(filepath, format="PNG")
            self._logger.info(f"图片已保存: {filepath}")
            return f"/images/{filename}"
        except Exception as e:
            self._logger.error(f"图片保存失败: {str(e)}")
            raise StorageError(str(e))

    def unload_current_model(self) -> None:
        if self._current_pipeline:
            self._logger.info("卸载当前模型")
            del self._current_pipeline
            self._current_pipeline = None
            self._current_model_name = None
            self._current_lora_name = None

            import gc
            gc.collect()

            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

    def _patch_transformers_torch_check(self) -> None:
        try:
            import transformers.utils.import_utils as tf_import_utils
            if not tf_import_utils.is_torch_available():
                tf_import_utils.is_torch_available.cache_clear()
                import functools

                @functools.lru_cache(maxsize=None)
                def _patched_is_torch_available() -> bool:
                    return True

                tf_import_utils.is_torch_available = _patched_is_torch_available
                self._logger.info("已修补transformers的PyTorch版本检测")
        except Exception as e:
            self._logger.warning(f"修补transformers版本检测失败: {str(e)}")


_sd_service: Optional[SDService] = None


def get_sd_service() -> SDService:
    global _sd_service
    if _sd_service is None:
        _sd_service = SDService()
    return _sd_service
