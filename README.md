# Stable Diffusion 后端服务

这是一个基于Python和FastAPI框架开发的后端服务，集成了Stable Diffusion模型及LoRA扩展，提供图片生成API接口和模型管理功能。

## 功能特性

- **图片生成API**：支持接收前端传递的生成参数并返回生成的图片数据
- **模型管理接口**：允许查询当前系统中可用的SD基础模型及LoRA模型列表
- **系统配置功能**：
  - 当未指定模型时，自动选择模型文件夹中的第一个模型作为默认模型
  - 提供生成参数的默认配置方案
  - 支持配置生成图片是否在本地进行暂存及暂存路径设置
- **错误处理**：完善的错误处理机制，提供清晰的错误信息
- **日志记录**：详细的日志记录，便于问题排查
- **可扩展性**：模块化设计，便于后续添加新的模型或功能

## 目录结构

```
AIGC_homework/
├── app/
│   ├── config.py          # 配置管理
│   ├── models/
│   │   └── schemas.py     # API请求/响应模型
│   ├── routers/
│   │   ├── generation.py  # 图片生成API
│   │   └── model_management.py  # 模型管理API
│   ├── services/
│   │   ├── model_manager.py  # 模型管理服务
│   │   └── sd_service.py     # Stable Diffusion服务
│   └── utils/
│       ├── compat.py      # 兼容性补丁
│       ├── exceptions.py  # 自定义异常
│       └── logger.py      # 日志配置
├── config.yaml            # 配置文件
├── docs/
│   ├── api_doc.md         # API接口文档
│   ├── deployment_guide.md  # 部署指南
│   └── user_manual.md     # 用户手册
├── models/
│   ├── sd/               # SD基础模型目录
│   └── lora/             # LoRA模型目录
├── output/                # 生成图片输出目录
├── requirements.txt       # 项目依赖
├── run.py                 # 应用启动脚本
└── README.md              # 项目说明文档
```

## 环境要求

- Python 3.8+
- PyTorch 2.1.0+
- CUDA 11.7+ (推荐，用于GPU加速)

## 安装步骤

1. 克隆项目代码：

```bash
git clone <项目仓库地址>
cd AIGC_homework
```

1. 安装依赖：

```bash
pip install -r requirements.txt
```

1. 配置模型目录：

在 `config.yaml` 文件中配置模型路径：

```yaml
models:
  sd_base_path: "./models/sd"      # SD基础模型目录
  lora_base_path: "./models/lora"  # LoRA模型目录
  default_sd_model: ""              # 默认SD模型（留空自动选择）
  default_lora_model: ""            # 默认LoRA模型（留空不使用）
  pipeline_config: ""               # 模型配置源（可选）
  offline_mode: false               # 离线模式
```

1. 准备模型：

将SD基础模型和LoRA模型分别放入 `models/sd` 和 `models/lora` 目录。

## 启动服务

```bash
python run.py
```

服务默认运行在 `http://0.0.0.0:8000`，可以在 `config.yaml` 中修改端口配置。

## API文档

启动服务后，可以访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

详细的API接口文档请参考 `docs/api_doc.md`。

## 示例调用

### 生成图片

```python
import requests
import base64

url = "http://localhost:8000/api/generate"
data = {
    "prompt": "一只可爱的小猫",
    "negative_prompt": "模糊, 丑陋, 变形",
    "width": 512,
    "height": 512,
    "num_inference_steps": 20,
    "guidance_scale": 7.5,
    "seed": -1,
    "sd_model": "",  # 留空使用默认模型
    "lora_model": "",  # 留空不使用LoRA
    "lora_weight": 0.7
}

response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
    image_data = base64.b64decode(result["image"])
    with open("output.jpg", "wb") as f:
        f.write(image_data)
    print(f"图片已保存到: output.jpg")
else:
    print(f"请求失败: {response.status_code}")
    print(response.json())
```

### 获取模型列表

```python
import requests

# 获取SD基础模型列表
url = "http://localhost:8000/api/models/sd"
response = requests.get(url)
if response.status_code == 200:
    models = response.json()["models"]
    print("SD基础模型列表:")
    for model in models:
        print(f"- {model}")

# 获取LoRA模型列表
url = "http://localhost:8000/api/models/lora"
response = requests.get(url)
if response.status_code == 200:
    models = response.json()["models"]
    print("\nLoRA模型列表:")
    for model in models:
        print(f"- {model}")
```

## 故障排除

### 模型加载失败

如果遇到模型加载失败的情况，可以尝试以下解决方案：

1. 确保网络连接正常，模型配置文件需要从Hugging Face下载
2. 在 `config.yaml` 中设置 `pipeline_config` 为对应的Hugging Face模型ID，例如：
   - SDXL: `stabilityai/stable-diffusion-xl-base-1.0`
   - SD1.5: `runwayml/stable-diffusion-v1-5`
3. 启用离线模式：将 `offline_mode` 设置为 `true`，使用本地缓存

### CUDA内存不足

如果遇到CUDA内存不足的问题，可以尝试：

1. 减小生成图片的尺寸
2. 减少推理步数
3. 使用较小的模型

