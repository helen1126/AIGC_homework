from fastapi import HTTPException


class SDAPIException(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(status_code=status_code, detail={
            "error_code": error_code,
            "message": message,
        })


class ModelNotFoundError(SDAPIException):
    def __init__(self, model_name: str, model_type: str = "SD"):
        super().__init__(
            status_code=404,
            error_code="MODEL_NOT_FOUND",
            message=f"{model_type}模型 '{model_name}' 未找到",
        )


class LoRANotFoundError(SDAPIException):
    def __init__(self, lora_name: str):
        super().__init__(
            status_code=404,
            error_code="LORA_NOT_FOUND",
            message=f"LoRA模型 '{lora_name}' 未找到",
        )


class NoModelAvailableError(SDAPIException):
    def __init__(self):
        super().__init__(
            status_code=503,
            error_code="NO_MODEL_AVAILABLE",
            message="系统中没有可用的SD模型，请先下载模型到模型目录",
        )


class GenerationError(SDAPIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            error_code="GENERATION_FAILED",
            message=f"图片生成失败: {detail}",
        )


class InvalidParameterError(SDAPIException):
    def __init__(self, param_name: str, reason: str):
        super().__init__(
            status_code=422,
            error_code="INVALID_PARAMETER",
            message=f"参数 '{param_name}' 无效: {reason}",
        )


class StorageError(SDAPIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            error_code="STORAGE_ERROR",
            message=f"存储错误: {detail}",
        )


ERROR_CODES = {
    "MODEL_NOT_FOUND": "模型未找到",
    "LORA_NOT_FOUND": "LoRA模型未找到",
    "NO_MODEL_AVAILABLE": "无可用模型",
    "GENERATION_FAILED": "图片生成失败",
    "INVALID_PARAMETER": "参数无效",
    "STORAGE_ERROR": "存储错误",
    "INTERNAL_ERROR": "内部服务器错误",
}
