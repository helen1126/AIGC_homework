from typing import Optional

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, description="正向提示词")
    negative_prompt: str = Field(default="", max_length=2000, description="反向提示词")
    width: Optional[int] = Field(default=None, ge=64, le=2048, description="图片宽度")
    height: Optional[int] = Field(default=None, ge=64, le=2048, description="图片高度")
    num_inference_steps: Optional[int] = Field(default=None, ge=1, le=150, description="推理步数")
    guidance_scale: Optional[float] = Field(default=None, ge=1.0, le=30.0, description="引导系数")
    seed: Optional[int] = Field(default=None, description="随机种子，-1为随机")
    sd_model: Optional[str] = Field(default=None, description="SD基础模型名称")
    lora_model: Optional[str] = Field(default=None, description="LoRA模型名称")
    lora_weight: float = Field(default=1.0, ge=0.0, le=2.0, description="LoRA权重")
    scheduler: Optional[str] = Field(default=None, description="采样器名称")


class GenerationResponse(BaseModel):
    success: bool = Field(description="是否生成成功")
    image_base64: str = Field(default="", description="Base64编码的图片数据")
    image_url: Optional[str] = Field(default=None, description="图片访问URL（启用存储时）")
    seed: int = Field(description="实际使用的随机种子")
    parameters: dict = Field(default_factory=dict, description="实际使用的生成参数")


class ModelInfo(BaseModel):
    name: str = Field(description="模型名称")
    path: str = Field(description="模型路径")
    is_default: bool = Field(default=False, description="是否为默认模型")


class SDModelListResponse(BaseModel):
    models: list[ModelInfo] = Field(description="SD基础模型列表")
    default_model: Optional[str] = Field(default=None, description="默认模型名称")
    total: int = Field(description="模型总数")


class LoRAModelListResponse(BaseModel):
    models: list[ModelInfo] = Field(description="LoRA模型列表")
    default_model: Optional[str] = Field(default=None, description="默认LoRA模型名称")
    total: int = Field(description="模型总数")


class SystemConfigResponse(BaseModel):
    generation_defaults: dict = Field(description="默认生成参数")
    storage_enabled: bool = Field(description="是否启用本地暂存")
    storage_path: str = Field(description="暂存路径")
    sd_models_path: str = Field(description="SD模型目录")
    lora_models_path: str = Field(description="LoRA模型目录")


class HealthResponse(BaseModel):
    status: str = Field(description="服务状态")
    version: str = Field(default="1.0.0", description="服务版本")
