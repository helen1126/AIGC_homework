# 系统部署文档

## 1. 环境要求

### 1.1 硬件要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 4核 | 8核及以上 |
| 内存 | 8GB | 16GB及以上 |
| GPU | 无（支持CPU运行） | NVIDIA GPU，显存6GB+ |
| 硬盘 | 20GB可用空间 | 50GB+ SSD |

### 1.2 软件要求

| 软件 | 版本要求 |
|------|---------|
| Python | 3.9 - 3.11 |
| pip | 最新版 |
| Git | 最新版（可选） |
| CUDA | 11.8+（GPU推理时需要） |

---

## 2. 安装步骤

### 2.1 克隆项目

```bash
git clone <项目仓库地址>
cd AIGC_homework
```

### 2.2 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2.3 安装依赖

```bash
pip install -r requirements.txt
```

如需GPU加速，请安装对应CUDA版本的PyTorch：

```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 2.4 准备模型文件

将SD基础模型放置到 `./models/sd/` 目录下，LoRA模型放置到 `./models/lora/` 目录下。

**支持的模型格式：**

- Hugging Face格式目录（包含 `config.json` 或 `model_index.json`）
- 单文件格式（`.safetensors`、`.bin`、`.ckpt`）

**目录结构示例：**

```
models/
├── sd/
│   ├── stable-diffusion-v1-5/
│   │   ├── config.json
│   │   ├── model_index.json
│   │   └── ...
│   └── sd-xl-base-1.0/
│       └── ...
└── lora/
    ├── my-lora-style/
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   └── ...
    └── another-lora/
        └── ...
```

### 2.5 配置系统

编辑 `config.yaml` 文件进行系统配置（详见第3节）。

---

## 3. 配置说明

配置文件路径：`config.yaml`

### 3.1 服务器配置

```yaml
server:
  host: "0.0.0.0"    # 监听地址，0.0.0.0表示所有网卡
  port: 8000          # 监听端口
```

### 3.2 模型配置

```yaml
models:
  sd_base_path: "./models/sd"       # SD基础模型目录
  lora_base_path: "./models/lora"   # LoRA模型目录
  default_sd_model: ""              # 默认SD模型名称，留空则自动选择第一个
  default_lora_model: ""            # 默认LoRA模型名称，留空则自动选择第一个
```

**自动选择逻辑：** 当 `default_sd_model` 或 `default_lora_model` 为空时，系统会自动扫描对应目录，选择按名称排序的第一个模型作为默认模型。

### 3.3 生成参数默认配置

```yaml
generation:
  default_width: 512                # 默认图片宽度
  default_height: 512               # 默认图片高度
  default_num_inference_steps: 20   # 默认推理步数
  default_guidance_scale: 7.5       # 默认引导系数
  default_seed: -1                  # 默认种子，-1表示随机
  default_scheduler: "euler"        # 默认采样器
```

### 3.4 存储配置

```yaml
storage:
  enabled: true       # 是否启用本地暂存
  path: "./output"    # 暂存路径
```

- `enabled: true` 时，生成的图片会保存到本地，并通过 `image_url` 返回访问路径
- `enabled: false` 时，仅返回Base64编码的图片数据

### 3.5 日志配置

```yaml
logging:
  level: "INFO"           # 日志级别：DEBUG/INFO/WARNING/ERROR/CRITICAL
  file: "./logs/app.log"  # 日志文件路径
```

---

## 4. 启动服务

### 4.1 开发模式启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4.2 生产模式启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

> **注意：** 由于SD模型占用大量显存/内存，建议 `workers` 设为1。

### 4.3 使用启动脚本

```bash
# Windows
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 或直接运行
python run.py
```

### 4.4 验证服务

服务启动后，访问以下地址验证：

- 健康检查：`http://localhost:8000/health`
- API文档（Swagger UI）：`http://localhost:8000/docs`
- API文档（ReDoc）：`http://localhost:8000/redoc`

---

## 5. 系统架构说明

### 5.1 项目结构

```
AIGC_homework/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口，FastAPI实例和中间件
│   ├── config.py            # 配置管理模块
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic数据模型（请求/响应）
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── generation.py    # 图片生成路由
│   │   └── model_management.py  # 模型管理路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── sd_service.py    # SD图片生成核心服务
│   │   └── model_manager.py # 模型管理服务
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # 日志工具
│       └── exceptions.py    # 自定义异常和错误码
├── config.yaml              # 系统配置文件
├── requirements.txt         # Python依赖
├── docs/                    # 文档目录
├── models/                  # 模型文件目录
│   ├── sd/                  # SD基础模型
│   └── lora/                # LoRA模型
├── output/                  # 图片输出目录
└── logs/                    # 日志目录
```

### 5.2 模块职责

| 模块 | 职责 |
|------|------|
| `config.py` | 加载和管理YAML配置文件，提供全局配置访问 |
| `schemas.py` | 定义API请求和响应的Pydantic数据模型，实现参数验证 |
| `model_manager.py` | 扫描模型目录、管理模型列表、自动选择默认模型 |
| `sd_service.py` | SD模型加载、LoRA加载、图片生成核心逻辑 |
| `generation.py` | 图片生成相关API路由 |
| `model_management.py` | 模型管理和系统配置相关API路由 |
| `logger.py` | 统一日志配置和管理 |
| `exceptions.py` | 自定义异常类和错误码定义 |

### 5.3 请求处理流程

```
客户端请求
    ↓
FastAPI路由层（参数验证）
    ↓
服务层（业务逻辑）
    ↓
模型管理器（模型加载/切换）
    ↓
SD服务（图片生成）
    ↓
响应返回（Base64 + URL）
```

### 5.4 可扩展性设计

- **新增模型类型：** 在 `model_manager.py` 中添加新的模型扫描和加载方法
- **新增生成功能：** 在 `sd_service.py` 中扩展生成方法，在 `generation.py` 中添加新路由
- **新增采样器：** 在 `sd_service.py` 的 `SCHEDULER_MAP` 中添加映射
- **新增API接口：** 在 `routers/` 目录下创建新路由文件，在 `main.py` 中注册
