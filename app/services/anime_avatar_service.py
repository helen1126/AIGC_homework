import base64
import hashlib
import io
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.config import get_config
from app.services.style_manager import get_style_manager
from app.services.sd_service import get_sd_service
from app.utils.logger import get_logger
from app.utils.exceptions import GenerationError


class AnimeAvatarService:
    def __init__(self):
        self._config = get_config()
        self._logger = get_logger()
        self._style_manager = get_style_manager()
        self._sd_service = get_sd_service()
        self._generation_history: List[Dict[str, Any]] = []
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_max_size: int = 100
        self._history_max_size: int = 1000

    def generate_avatar(self, params: dict) -> dict:
        start_time = time.time()
        
        base_description = params.get("description", "anime character portrait")
        style_id = params.get("style", "japanese")
        character_features = params.get("character_features", {})
        resolution = params.get("resolution", "medium")
        quality_mode = params.get("quality_mode", "balanced")
        reference_image_base64 = params.get("reference_image", None)
        user_id = params.get("user_id", "anonymous")
        model = params.get("model", None)
        lora = params.get("lora", None)
        lora_weight = params.get("lora_weight", 1.0)

        cache_key = self._generate_cache_key(params)
        
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            self._logger.info(f"使用缓存结果，跳过生成")
            return {
                **cached_result,
                "cached": True,
                "generation_time": time.time() - start_time
            }

        try:
            positive_prompt, negative_prompt = self._style_manager.build_prompt(
                base_description=base_description,
                style_id=style_id,
                character_features=character_features
            )

            resolution_preset = self._style_manager.get_resolution_preset(resolution)
            if not resolution_preset:
                raise ValueError(f"未知的分辨率预设: {resolution}")

            generation_params = self._optimize_for_speed(
                width=resolution_preset.width,
                height=resolution_preset.height,
                quality_mode=quality_mode
            )

            sd_params = {
                "prompt": positive_prompt,
                "negative_prompt": negative_prompt,
                "width": generation_params["width"],
                "height": generation_params["height"],
                "num_inference_steps": generation_params["steps"],
                "guidance_scale": generation_params["guidance_scale"],
                "seed": params.get("seed", -1),
                "scheduler": generation_params["scheduler"],
                "sd_model": model,
                "lora_model": lora,
                "lora_weight": lora_weight
            }

            if reference_image_base64:
                sd_params["reference_image"] = reference_image_base64

            result = self._sd_service.generate(sd_params)

            elapsed_time = time.time() - start_time
            
            if elapsed_time > 10:
                self._logger.warning(f"生成时间超过10秒限制: {elapsed_time:.2f}秒")

            avatar_data = {
                "success": result["success"],
                "image_base64": result["image_base64"],
                "image_url": result.get("image_url"),
                "seed": result["seed"],
                "style_used": style_id,
                "character_features_applied": character_features,
                "resolution": {
                    "width": resolution_preset.width,
                    "height": resolution_preset.height,
                    "preset": resolution
                },
                "parameters": {
                    "positive_prompt": positive_prompt[:200] + "..." if len(positive_prompt) > 200 else positive_prompt,
                    "negative_prompt": negative_prompt[:200] + "..." if len(negative_prompt) > 200 else negative_prompt,
                    **result.get("parameters", {})
                },
                "generation_time": round(elapsed_time, 2),
                "cached": False,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }

            self._add_to_cache(cache_key, avatar_data)
            self._add_to_history(avatar_data)

            return avatar_data

        except Exception as e:
            self._logger.error(f"动漫头像生成失败: {str(e)}", exc_info=True)
            raise GenerationError(f"动漫头像生成失败: {str(e)}")

    def _generate_cache_key(self, params: dict) -> str:
        cache_data = {
            "description": params.get("description"),
            "style": params.get("style"),
            "character_features": params.get("character_features"),
            "resolution": params.get("resolution"),
            "quality_mode": params.get("quality_mode"),
            "seed": params.get("seed", -1),
            "model": params.get("model"),
            "lora": params.get("lora"),
            "lora_weight": params.get("lora_weight", 1.0)
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[dict]:
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            entry["last_accessed"] = time.time()
            return entry["data"]
        return None

    def _add_to_cache(self, cache_key: str, data: dict) -> None:
        if len(self._cache) >= self._cache_max_size:
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k].get("last_accessed", 0))
            del self._cache[oldest_key]

        self._cache[cache_key] = {
            "data": data,
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        self._logger.debug(f"已添加到缓存: {cache_key}")

    def _add_to_history(self, data: dict) -> None:
        history_entry = {
            "id": len(self._generation_history) + 1,
            "timestamp": data["timestamp"],
            "user_id": data["user_id"],
            "style": data["style_used"],
            "resolution": data["resolution"]["preset"],
            "generation_time": data["generation_time"],
            "seed": data["seed"]
        }

        self._generation_history.append(history_entry)

        if len(self._generation_history) > self._history_max_size:
            self._generation_history = self._generation_history[-self._history_max_size:]

        self._logger.debug(f"已添加到历史记录: #{history_entry['id']}")

    def _optimize_for_speed(self, width: int, height: int, 
                           quality_mode: str) -> dict:
        optimizations = {
            "fast": {
                "steps": 15,
                "guidance_scale": 7.0,
                "scheduler": "euler_a",
                "width": min(width, 512),
                "height": min(height, 512)
            },
            "balanced": {
                "steps": 20,
                "guidance_scale": 7.5,
                "scheduler": "euler",
                "width": width,
                "height": height
            },
            "quality": {
                "steps": 30,
                "guidance_scale": 8.0,
                "scheduler": "dpm++2m_karras",
                "width": width,
                "height": height
            }
        }

        mode_config = optimizations.get(quality_mode, optimizations["balanced"])
        
        max_dimension = 1024
        if mode_config["width"] > max_dimension or mode_config["height"] > max_dimension:
            scale = max_dimension / max(mode_config["width"], mode_config["height"])
            mode_config["width"] = int(mode_config["width"] * scale)
            mode_config["height"] = int(mode_config["height"] * scale)

        return mode_config

    def get_generation_history(self, user_id: Optional[str] = None, 
                               limit: int = 20, offset: int = 0) -> dict:
        history = self._generation_history
        
        if user_id and user_id != "all":
            history = [h for h in history if h.get("user_id") == user_id]

        total = len(history)
        paginated_history = history[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
            "records": paginated_history
        }

    def get_available_styles(self) -> List[dict]:
        styles = self._style_manager.get_all_styles()
        return [style.to_dict() for style in styles]

    def get_character_feature_options(self) -> Dict[str, List[dict]]:
        features = self._style_manager.get_all_character_features()
        result = {}
        for feature_type, feature in features.items():
            result[feature_type] = feature.to_dict()["options"]
        return result

    def get_resolution_presets(self) -> List[dict]:
        presets = self._style_manager.get_all_resolution_presets()
        return [preset.to_dict() for preset in presets]

    def clear_cache(self) -> int:
        cache_size = len(self._cache)
        self._cache.clear()
        self._logger.info(f"已清除缓存，共 {cache_size} 条记录")
        return cache_size

    def clear_history(self, user_id: Optional[str] = None) -> int:
        if user_id and user_id != "all":
            before_count = len(self._generation_history)
            self._generation_history = [
                h for h in self._generation_history 
                if h.get("user_id") != user_id
            ]
            removed_count = before_count - len(self._generation_history)
        else:
            removed_count = len(self._generation_history)
            self._generation_history.clear()

        self._logger.info(f"已清除历史记录，共 {removed_count} 条记录")
        return removed_count


_anime_avatar_service: Optional[AnimeAvatarService] = None


def get_anime_avatar_service() -> AnimeAvatarService:
    global _anime_avatar_service
    if _anime_avatar_service is None:
        _anime_avatar_service = AnimeAvatarService()
    return _anime_avatar_service