import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
from app.utils.logger import get_logger


class StyleConfig:
    def __init__(self, style_id: str, name: str, description: str,
                 prompt_prefix: str, prompt_suffix: str, negative_suffix: str,
                 quality_tags: List[str], style_strength: float):
        self.style_id = style_id
        self.name = name
        self.description = description
        self.prompt_prefix = prompt_prefix
        self.prompt_suffix = prompt_suffix
        self.negative_suffix = negative_suffix
        self.quality_tags = quality_tags
        self.style_strength = style_strength

    def to_dict(self) -> dict:
        return {
            "id": self.style_id,
            "name": self.name,
            "description": self.description,
            "quality_tags": self.quality_tags,
            "style_strength": self.style_strength
        }


class CharacterFeature:
    def __init__(self, feature_type: str, options: List[Dict[str, str]]):
        self.feature_type = feature_type
        self.options = options

    def get_option(self, value: str) -> Optional[Dict[str, str]]:
        for option in self.options:
            if option["value"] == value:
                return option
        return None

    def to_dict(self) -> dict:
        return {
            "type": self.feature_type,
            "options": [
                {"value": opt["value"], "label": opt["label"]}
                for opt in self.options
            ]
        }


class ResolutionPreset:
    def __init__(self, preset_id: str, width: int, height: int,
                 label: str, description: str):
        self.preset_id = preset_id
        self.width = width
        self.height = height
        self.label = label
        self.description = description

    def to_dict(self) -> dict:
        return {
            "id": self.preset_id,
            "width": self.width,
            "height": self.height,
            "label": self.label,
            "description": self.description
        }


class StyleManager:
    _instance: Optional['StyleManager'] = None
    _styles: Dict[str, StyleConfig] = {}
    _character_features: Dict[str, CharacterFeature] = {}
    _resolution_presets: Dict[str, ResolutionPreset] = {}

    def __new__(cls) -> 'StyleManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not getattr(self, '_initialized', False):
            self._logger = get_logger()
            self._load_styles_config()
            self._initialized = True

    def _load_styles_config(self) -> None:
        config_path = Path(__file__).parent.parent.parent / "config" / "styles.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            self._styles.clear()
            self._character_features.clear()
            self._resolution_presets.clear()

            if 'styles' in config:
                for style_id, style_data in config['styles'].items():
                    self._styles[style_id] = StyleConfig(
                        style_id=style_id,
                        name=style_data.get('name', style_id),
                        description=style_data.get('description', ''),
                        prompt_prefix=style_data.get('prompt_prefix', ''),
                        prompt_suffix=style_data.get('prompt_suffix', ''),
                        negative_suffix=style_data.get('negative_suffix', ''),
                        quality_tags=style_data.get('quality_tags', []),
                        style_strength=style_data.get('style_strength', 1.0)
                    )
                    self._logger.info(f"已加载动漫风格: {style_id} - {self._styles[style_id].name}")

            if 'character_features' in config:
                for feature_type, feature_data in config['character_features'].items():
                    self._character_features[feature_type] = CharacterFeature(
                        feature_type=feature_type,
                        options=feature_data.get('options', [])
                    )

            if 'resolution_presets' in config:
                for preset_id, preset_data in config['resolution_presets'].items():
                    self._resolution_presets[preset_id] = ResolutionPreset(
                        preset_id=preset_id,
                        width=preset_data.get('width', 512),
                        height=preset_data.get('height', 512),
                        label=preset_data.get('label', ''),
                        description=preset_data.get('description', '')
                    )

            self._logger.info(f"已加载 {len(self._styles)} 种动漫风格")
            self._logger.info(f"已加载 {len(self._character_features)} 类角色特征")
            self._logger.info(f"已加载 {len(self._resolution_presets)} 个分辨率预设")

        except Exception as e:
            self._logger.error(f"加载风格配置失败: {str(e)}", exc_info=True)
            raise

    def get_style(self, style_id: str) -> Optional[StyleConfig]:
        return self._styles.get(style_id)

    def get_all_styles(self) -> List[StyleConfig]:
        return list(self._styles.values())

    def get_style_ids(self) -> List[str]:
        return list(self._styles.keys())

    def get_character_feature(self, feature_type: str) -> Optional[CharacterFeature]:
        return self._character_features.get(feature_type)

    def get_all_character_features(self) -> Dict[str, CharacterFeature]:
        return self._character_features.copy()

    def get_resolution_preset(self, preset_id: str) -> Optional[ResolutionPreset]:
        return self._resolution_presets.get(preset_id)

    def get_all_resolution_presets(self) -> List[ResolutionPreset]:
        return list(self._resolution_presets.values())

    def build_prompt(self, base_description: str, style_id: str,
                     character_features: Optional[Dict[str, str]] = None) -> tuple:
        style = self.get_style(style_id)
        if not style:
            raise ValueError(f"未知的风格ID: {style_id}")

        prompt_parts = [style.prompt_prefix]

        if character_features:
            for feature_type, feature_value in character_features.items():
                feature = self.get_character_feature(feature_type)
                if feature:
                    option = feature.get_option(feature_value)
                    if option:
                        prompt_parts.append(option.get("prompt_addition", ""))

        prompt_parts.append(base_description)
        prompt_parts.append(style.prompt_suffix)

        positive_prompt = "".join(prompt_parts)
        negative_prompt = f"low quality, bad anatomy, blurry{style.negative_suffix}"

        return positive_prompt, negative_prompt

    def reload_styles(self) -> None:
        self._load_styles_config()


def get_style_manager() -> StyleManager:
    return StyleManager()