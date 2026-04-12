# API接口文档

## 概述

本文档描述了Stable Diffusion图片生成服务的所有API接口。服务基础路径为 `http://{host}:{port}`，所有API接口均以 `/api/v1` 为前缀。

---

## 1. 图片生成接口

### 1.1 文本生成图片（完整参数）

**接口地址：** `POST /api/v1/generation/text2img`

**接口说明：** 根据文本提示词生成图片，支持SD基础模型和LoRA扩展，可自定义所有生成参数。

**请求体（JSON）：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| prompt | string | 是 | - | 正向提示词，1-2000字符 |
| negative_prompt | string | 否 | "" | 反向提示词，最大2000字符 |
| width | integer | 否 | 512 | 图片宽度，64-2048 |
| height | integer | 否 | 512 | 图片高度，64-2048 |
| num_inference_steps | integer | 否 | 20 | 推理步数，1-150 |
| guidance_scale | float | 否 | 7.5 | 引导系数（CFG Scale），1.0-30.0 |
| seed | integer | 否 | -1 | 随机种子，-1表示随机 |
| sd_model | string | 否 | 默认模型 | SD基础模型名称 |
| lora_model | string | 否 | 无 | LoRA模型名称 |
| lora_weight | float | 否 | 1.0 | LoRA权重，0.0-2.0 |
| scheduler | string | 否 | "euler" | 采样器名称 |

**支持的采样器：**

| 采样器名称 | 说明 |
|------------|------|
| euler | Euler离散采样器 |
| euler_a | Euler祖先采样器 |
| dpm++2m | DPM++ 2M采样器 |
| dpm++2m_karras | DPM++ 2M Karras采样器 |
| ddim | DDIM采样器 |
| lms | LMS离散采样器 |
| pndm | PNDM采样器 |

**请求示例：**

```json
{
    "prompt": "a beautiful sunset over the ocean, highly detailed",
    "negative_prompt": "blurry, low quality",
    "width": 512,
    "height": 512,
    "num_inference_steps": 25,
    "guidance_scale": 7.5,
    "seed": 42,
    "sd_model": "stable-diffusion-v1-5",
    "lora_model": "my-lora-style",
    "lora_weight": 0.8,
    "scheduler": "euler_a"
}
```

**响应格式：**

```json
{
    "success": true,
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "image_url": "/images/stable-diffusion-v1-5_20240101_120000_42.png",
    "seed": 42,
    "parameters": {
        "prompt": "a beautiful sunset over the ocean, highly detailed",
        "negative_prompt": "blurry, low quality",
        "width": 512,
        "height": 512,
        "num_inference_steps": 25,
        "guidance_scale": 7.5,
        "seed": 42,
        "sd_model": "stable-diffusion-v1-5",
        "lora_model": "my-lora-style",
        "lora_weight": 0.8,
        "scheduler": "euler_a"
    }
}
```

---

### 1.2 简单文本生成图片

**接口地址：** `POST /api/v1/generation/text2img/simple`

**接口说明：** 仅需提供提示词即可生成图片，其余参数使用默认值。

**请求参数（Query）：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| prompt | string | 是 | - | 正向提示词，1-2000字符 |
| negative_prompt | string | 否 | "" | 反向提示词 |
| sd_model | string | 否 | 默认模型 | SD模型名称 |
| lora_model | string | 否 | 无 | LoRA模型名称 |

**请求示例：**

```
POST /api/v1/generation/text2img/simple?prompt=a%20beautiful%20sunset
```

**响应格式：** 同1.1

---

## 2. 模型管理接口

### 2.1 获取SD基础模型列表

**接口地址：** `GET /api/v1/models/sd`

**接口说明：** 返回系统中所有可用的Stable Diffusion基础模型。

**响应格式：**

```json
{
    "models": [
        {
            "name": "stable-diffusion-v1-5",
            "path": "/path/to/models/sd/stable-diffusion-v1-5",
            "is_default": true
        },
        {
            "name": "sd-xl-base-1.0",
            "path": "/path/to/models/sd/sd-xl-base-1.0",
            "is_default": false
        }
    ],
    "default_model": "stable-diffusion-v1-5",
    "total": 2
}
```

---

### 2.2 获取LoRA模型列表

**接口地址：** `GET /api/v1/models/lora`

**接口说明：** 返回系统中所有可用的LoRA扩展模型。

**响应格式：**

```json
{
    "models": [
        {
            "name": "my-lora-style",
            "path": "/path/to/models/lora/my-lora-style",
            "is_default": true
        }
    ],
    "default_model": "my-lora-style",
    "total": 1
}
```

---

### 2.3 刷新模型列表

**接口地址：** `POST /api/v1/models/refresh`

**接口说明：** 重新扫描模型目录，更新可用模型列表和默认模型。适用于添加新模型后使用。

**响应格式：**

```json
{
    "success": true,
    "message": "模型列表已刷新",
    "default_sd_model": "stable-diffusion-v1-5",
    "default_lora_model": "my-lora-style"
}
```

---

### 2.4 获取系统配置

**接口地址：** `GET /api/v1/models/config`

**接口说明：** 返回当前系统的配置信息，包括默认参数和存储设置。

**响应格式：**

```json
{
    "generation_defaults": {
        "width": 512,
        "height": 512,
        "num_inference_steps": 20,
        "guidance_scale": 7.5,
        "seed": -1,
        "scheduler": "euler"
    },
    "storage_enabled": true,
    "storage_path": "./output",
    "sd_models_path": "./models/sd",
    "lora_models_path": "./models/lora"
}
```

---

## 3. 系统接口

### 3.1 健康检查

**接口地址：** `GET /health`

**接口说明：** 检查服务是否正常运行。

**响应格式：**

```json
{
    "status": "ok",
    "version": "1.0.0"
}
```

---

## 4. 错误码说明

所有错误响应均遵循以下格式：

```json
{
    "success": false,
    "error_code": "ERROR_CODE",
    "message": "错误描述信息"
}
```

### 错误码列表

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| MODEL_NOT_FOUND | 404 | 指定的SD模型未找到 |
| LORA_NOT_FOUND | 404 | 指定的LoRA模型未找到 |
| NO_MODEL_AVAILABLE | 503 | 系统中没有可用的SD模型 |
| GENERATION_FAILED | 500 | 图片生成过程中发生错误 |
| INVALID_PARAMETER | 422 | 请求参数验证失败 |
| STORAGE_ERROR | 500 | 图片存储过程中发生错误 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 常见错误示例

**模型未找到：**

```json
{
    "success": false,
    "error_code": "MODEL_NOT_FOUND",
    "message": "SD模型 'nonexistent-model' 未找到"
}
```

**无可用模型：**

```json
{
    "success": false,
    "error_code": "NO_MODEL_AVAILABLE",
    "message": "系统中没有可用的SD模型，请先下载模型到模型目录"
}
```

**参数验证失败（FastAPI自动返回）：**

```json
{
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "prompt"],
            "msg": "String should have at least 1 character",
            "input": ""
        }
    ]
}
```
