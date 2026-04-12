# 用户使用手册

## 1. 快速开始

### 1.1 启动服务

确保已完成部署（参考《系统部署文档》），然后启动服务：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动成功后，访问 `http://localhost:8000/docs` 可查看交互式API文档。

---

## 2. 接口调用示例

以下示例使用 `curl` 命令，也可使用Postman或其他HTTP客户端。

### 2.1 健康检查

```bash
curl http://localhost:8000/health
```

**响应：**

```json
{
    "status": "ok",
    "version": "1.0.0"
}
```

### 2.2 查看可用模型

**查看SD基础模型：**

```bash
curl http://localhost:8000/api/v1/models/sd
```

**查看LoRA模型：**

```bash
curl http://localhost:8000/api/v1/models/lora
```

### 2.3 生成图片

#### 最简方式（仅提供提示词）

```bash
curl -X POST "http://localhost:8000/api/v1/generation/text2img/simple?prompt=a%20beautiful%20sunset%20over%20the%20ocean"
```

#### 完整参数方式

```bash
curl -X POST http://localhost:8000/api/v1/generation/text2img \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful sunset over the ocean, highly detailed, 4k",
    "negative_prompt": "blurry, low quality, distorted",
    "width": 512,
    "height": 512,
    "num_inference_steps": 25,
    "guidance_scale": 7.5,
    "seed": 42,
    "sd_model": "stable-diffusion-v1-5",
    "lora_model": "my-lora-style",
    "lora_weight": 0.8,
    "scheduler": "euler_a"
  }'
```

### 2.4 刷新模型列表

添加新模型到模型目录后，调用此接口刷新：

```bash
curl -X POST http://localhost:8000/api/v1/models/refresh
```

### 2.5 查看系统配置

```bash
curl http://localhost:8000/api/v1/models/config
```

---

## 3. Python调用示例

### 3.1 使用requests库

```python
import requests
import base64
from pathlib import Path

BASE_URL = "http://localhost:8000"


def check_health():
    """健康检查"""
    resp = requests.get(f"{BASE_URL}/health")
    print(resp.json())


def list_models():
    """查看可用模型"""
    # SD模型
    resp = requests.get(f"{BASE_URL}/api/v1/models/sd")
    print("SD模型列表:", resp.json())

    # LoRA模型
    resp = requests.get(f"{BASE_URL}/api/v1/models/lora")
    print("LoRA模型列表:", resp.json())


def generate_image(prompt, sd_model=None, lora_model=None, seed=-1):
    """生成图片"""
    payload = {
        "prompt": prompt,
        "negative_prompt": "blurry, low quality",
        "width": 512,
        "height": 512,
        "num_inference_steps": 20,
        "guidance_scale": 7.5,
        "seed": seed,
    }
    if sd_model:
        payload["sd_model"] = sd_model
    if lora_model:
        payload["lora_model"] = lora_model

    resp = requests.post(
        f"{BASE_URL}/api/v1/generation/text2img",
        json=payload,
    )
    result = resp.json()

    if result["success"]:
        # 保存Base64图片到文件
        image_data = base64.b64decode(result["image_base64"])
        output_path = Path(f"generated_{result['seed']}.png")
        output_path.write_bytes(image_data)
        print(f"图片已保存: {output_path}")
        print(f"使用种子: {result['seed']}")
        if result.get("image_url"):
            print(f"图片URL: {BASE_URL}{result['image_url']}")
    else:
        print(f"生成失败: {result.get('message')}")


if __name__ == "__main__":
    check_health()
    list_models()
    generate_image("a beautiful sunset over the ocean, highly detailed")
```

---

## 4. 参数详细说明

### 4.1 生成参数

| 参数 | 说明 | 建议值 |
|------|------|--------|
| prompt | 正向提示词，描述你想要生成的图片内容 | 尽量详细，使用英文逗号分隔关键词 |
| negative_prompt | 反向提示词，描述你不想出现的内容 | 常用: "blurry, low quality, distorted" |
| width | 图片宽度（像素） | 512（SD1.x），1024（SDXL） |
| height | 图片高度（像素） | 512（SD1.x），1024（SDXL） |
| num_inference_steps | 推理步数，步数越多细节越丰富但速度越慢 | 20-30（质量与速度平衡） |
| guidance_scale | 引导系数，值越大越贴近提示词但可能过饱和 | 7-12 |
| seed | 随机种子，相同种子+相同参数=相同图片 | -1（随机）或固定值（复现） |
| sd_model | SD基础模型名称 | 从模型列表中选择 |
| lora_model | LoRA模型名称 | 从模型列表中选择 |
| lora_weight | LoRA权重，控制LoRA风格的影响程度 | 0.5-1.0 |
| scheduler | 采样器 | euler_a（通用），dpm++2m（高质量） |

### 4.2 采样器选择建议

| 采样器 | 特点 | 适用场景 |
|--------|------|---------|
| euler | 速度快，质量中等 | 快速预览 |
| euler_a | 速度快，质量较好，有创意性 | 通用场景（推荐） |
| dpm++2m | 质量高，细节丰富 | 高质量生成 |
| dpm++2m_karras | 高质量，色彩更丰富 | 艺术风格图片 |
| ddim | 确定性采样 | 需要精确复现 |

---

## 5. 常见问题

### 5.1 模型未找到

**问题：** 调用生成接口返回 `MODEL_NOT_FOUND` 错误。

**解决：**
1. 确认模型文件已放置到正确目录（默认 `./models/sd/`）
2. 调用 `POST /api/v1/models/refresh` 刷新模型列表
3. 调用 `GET /api/v1/models/sd` 查看可用模型名称

### 5.2 生成速度慢

**问题：** 图片生成耗时过长。

**解决：**
1. 使用GPU加速（安装CUDA版本的PyTorch）
2. 降低 `num_inference_steps`（如从30降到20）
3. 降低图片分辨率（如从512x512降到256x256）

### 5.3 显存不足

**问题：** GPU显存不足导致生成失败。

**解决：**
1. 降低图片分辨率
2. 使用SD1.5而非SDXL模型
3. 在代码中启用CPU offload（需修改sd_service.py）

### 5.4 图片质量不佳

**问题：** 生成的图片质量不理想。

**解决：**
1. 优化提示词，使用更详细的描述
2. 增加推理步数（如从20增加到30）
3. 调整引导系数（尝试7.5-12之间）
4. 更换采样器（推荐 `euler_a` 或 `dpm++2m`）
5. 使用LoRA模型添加特定风格

### 5.5 如何复现相同的图片

**解决：** 使用固定的 `seed` 值，并保持其他所有参数一致，即可生成相同的图片。

```json
{
    "prompt": "a beautiful sunset",
    "seed": 42,
    "sd_model": "stable-diffusion-v1-5"
}
```
