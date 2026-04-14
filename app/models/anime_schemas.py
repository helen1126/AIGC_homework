from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class CharacterFeatureRequest(BaseModel):
    hair_style: Optional[str] = Field(default=None, description="发型选项")
    hair_color: Optional[str] = Field(default=None, description="发色选项")
    eye_color: Optional[str] = Field(default=None, description="眼睛颜色")
    clothing_style: Optional[str] = Field(default=None, description="服装风格")
    expression: Optional[str] = Field(default=None, description="表情")


class AvatarGenerationRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=1000, 
                            description="角色描述，如'一位勇敢的骑士'")
    style: str = Field(default="japanese", description="动漫风格ID")
    character_features: Optional[CharacterFeatureRequest] = Field(
        default=None, description="角色特征自定义"
    )
    resolution: str = Field(default="medium", 
                           description="分辨率预设: low/medium/high/ultra")
    quality_mode: str = Field(default="balanced", 
                             description="质量模式: fast/balanced/quality")
    seed: Optional[int] = Field(default=-1, ge=-1, le=2**32-1,
                               description="随机种子，-1为随机")
    reference_image: Optional[str] = Field(default=None, 
                                          description="参考图片Base64编码")
    user_id: Optional[str] = Field(default="anonymous", max_length=100,
                                  description="用户标识")
    model: Optional[str] = Field(default=None, description="SD模型名称")
    lora: Optional[str] = Field(default=None, description="LoRA模型名称")
    lora_weight: Optional[float] = Field(default=1.0, ge=0.0, le=2.0,
                                         description="LoRA权重")


class AvatarGenerationResponse(BaseModel):
    success: bool = Field(description="是否生成成功")
    image_base64: str = Field(default="", description="Base64编码的图片数据")
    image_url: Optional[str] = Field(default=None, description="图片访问URL")
    seed: int = Field(description="实际使用的随机种子")
    style_used: str = Field(description="使用的动漫风格")
    character_features_applied: Dict[str, Any] = Field(
        default_factory=dict, description="应用的角色特征"
    )
    resolution: Dict[str, Any] = Field(
        default_factory=dict, description="生成的分辨率信息"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="实际使用的生成参数"
    )
    generation_time: float = Field(description="生成耗时(秒)")
    cached: bool = Field(description="是否使用缓存结果")
    timestamp: str = Field(description="生成时间戳")


class StyleInfo(BaseModel):
    id: str = Field(description="风格ID")
    name: str = Field(description="风格名称")
    description: str = Field(description="风格描述")
    quality_tags: List[str] = Field(default_factory=list, description="质量标签")
    style_strength: float = Field(description="风格强度")


class StyleListResponse(BaseModel):
    styles: List[StyleInfo] = Field(description="可用风格列表")
    total: int = Field(description="风格总数")


class CharacterFeatureOption(BaseModel):
    value: str = Field(description="选项值")
    label: str = Field(description="显示标签")


class CharacterFeaturesResponse(BaseModel):
    features: Dict[str, List[CharacterFeatureOption]] = Field(
        description="角色特征分类及选项"
    )


class ResolutionPresetInfo(BaseModel):
    id: str = Field(description="预设ID")
    width: int = Field(description="宽度")
    height: int = Field(description="高度")
    label: str = Field(description="预设名称")
    description: str = Field(description="预设描述")


class ResolutionPresetsResponse(BaseModel):
    presets: List[ResolutionPresetInfo] = Field(description="分辨率预设列表")
    total: int = Field(description="预设总数")


class GenerationHistoryRecord(BaseModel):
    id: int = Field(description="记录ID")
    timestamp: str = Field(description="生成时间")
    user_id: str = Field(description="用户ID")
    style: str = Field(description="使用的风格")
    resolution: str = Field(description="分辨率预设")
    generation_time: float = Field(description="生成耗时")
    seed: int = Field(description="随机种子")


class HistoryListResponse(BaseModel):
    total: int = Field(description="总记录数")
    limit: int = Field(description="每页数量")
    offset: int = Field(description="偏移量")
    has_more: bool = Field(description="是否有更多记录")
    records: List[GenerationHistoryRecord] = Field(description="历史记录列表")


class CacheStatsResponse(BaseModel):
    cache_size: int = Field(description="当前缓存条目数")
    cache_max_size: int = Field(description="最大缓存容量")
    history_size: int = Field(description="历史记录数")
    history_max_size: int = Field(description="历史记录最大容量")


class ClearCacheResponse(BaseModel):
    success: bool = Field(description="是否清除成功")
    cleared_count: int = Field(description="清除的条目数")
    message: str = Field(description="操作消息")