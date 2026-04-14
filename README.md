# AI动漫头像生成服务

这是一个基于Python和FastAPI框架开发的AI动漫头像生成后端服务，集成了Stable Diffusion模型，支持多种动漫风格、角色特征自定义、智能缓存和生成历史记录功能。

## 功能特性

### 核心功能

- **🎨 多种动漫风格**：支持6种不同的动漫风格（日系、美漫、Q版、水彩风、赛博朋克、像素艺术）
- **👤 角色自定义**：支持5类角色特征自定义（发型、发色、眼色、服装、表情）
- **⚡ 快速生成**：优化的生成流程，确保单次生成响应时间≤10秒
- **📐 多分辨率支持**：4种分辨率预设（256x256到1024x1024）
- **💾 智能缓存**：自动缓存重复请求，显著提升响应速度
- **📊 历史记录**：完整的生成历史查询和管理功能
- **🔧 高度可扩展**：模块化设计，易于添加新风格和功能

### 基础功能（继承自原SD服务）

- **图片生成API**：基于Stable Diffusion的图片生成能力
- **模型管理接口**：支持查询和管理SD基础模型及LoRA模型
- **系统配置功能**：
  - 自动默认模型选择
  - 灵活的生成参数配置
  - 本地图片存储与路径设置
- **错误处理**：完善的异常处理机制
- **日志记录**：详细的日志系统

## 目录结构

```
AIGC_homework/
├── app/
│   ├── config.py                    # 配置管理
│   ├── main.py                      # FastAPI应用主文件
│   ├── models/
│   │   ├── schemas.py               # 原始API请求/响应模型
│   │   └── anime_schemas.py         # 动漫头像相关数据模型
│   ├── routers/
│   │   ├── generation.py            # 原始图片生成API
│   │   ├── model_management.py      # 模型管理API
│   │   ├── avatar.py                # 动漫头像生成API ⭐新增
│   │   └── history.py               # 历史记录与缓存API ⭐新增
│   ├── services/
│   │   ├── model_manager.py         # 模型管理服务
│   │   ├── sd_service.py            # Stable Diffusion核心服务
│   │   ├── style_manager.py         # 动漫风格管理服务 ⭐新增
│   │   └── anime_avatar_service.py  # 动漫头像生成核心服务 ⭐新增
│   └── utils/
│       ├── compat.py                # 兼容性补丁
│       ├── exceptions.py            # 自定义异常
│       └── logger.py                # 日志配置
├── config/
│   └── styles.yaml                  # 动漫风格配置文件 ⭐新增
├── config.yaml                      # 主配置文件
├── docs/
│   ├── api_doc.md                   # 原始API文档
│   ├── anime_api_doc.md             # 动漫头像API文档 ⭐新增
│   ├── deployment_guide.md          # 部署指南
│   └── user_manual.md               # 用户手册
├── models/
│   ├── sd/                          # SD基础模型目录
│   └── lora/                        # LoRA模型目录
├── output/                          # 生成图片输出目录
├── test_anime_api.py                # 动漫API测试脚本 ⭐新增
├── requirements.txt                 # 项目依赖
├── run.py                           # 应用启动脚本
├── README.md                        # 项目说明文档
└── .gitignore                       # Git忽略规则
```

## 环境要求

- Python 3.8+
- PyTorch 2.1.0+
- CUDA 11.7+ (推荐，用于GPU加速)
- PyYAML >= 6.0.1

## 安装步骤

1. 克隆项目代码：

```bash
git clone <项目仓库地址>
cd AIGC_homework
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置模型目录：

在 `config.yaml` 文件中配置模型路径：

```yaml
models:
  sd_base_path: "./models/sd"      # SD基础模型目录
  lora_base_path: "./models/lora"  # LoRA模型目录
  default_sd_model: ""              # 默认SD模型（留空自动选择）
  default_lora_model: ""            # 默认LoRA模型（留空不使用）
  pipeline_config: ""               # 模型配置源（可选）
  offline_mode: false               # 离线模式

anime_avatar:
  default_style: "japanese"          # 默认动漫风格
  default_resolution: "medium"       # 默认分辨率
  default_quality_mode: "balanced"   # 默认质量模式
  cache_enabled: true                # 是否启用缓存
  cache_max_size: 100                # 缓存最大容量
  history_max_size: 1000             # 历史记录最大容量
  max_generation_time: 10.0          # 最大生成时间限制(秒)
```

4. 准备模型：

将SD基础模型和LoRA模型分别放入 `models/sd` 和 `models/lora` 目录。

## 启动服务

```bash
python run.py
```

服务默认运行在 `http://0.0.0.0:8000`，可以在 `config.yaml` 中修改端口配置。

## API文档

启动服务后，可以访问以下地址查看交互式API文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

详细的API文档：
- [原始SD API文档](docs/api_doc.md)
- [动漫头像API文档](docs/anime_api_doc.md) ⭐新增

## 支持的动漫风格

| 风格ID | 名称 | 特点 | 适用场景 |
|--------|------|------|----------|
| japanese | 日系动漫 | 细腻线条，柔和色彩 | 通用型 |
| american_comic | 美漫风格 | 粗犷线条，强烈对比 | 英雄角色 |
| chibi_q | Q版萌系 | 夸张比例，大眼睛 | 可爱角色 |
| watercolor | 水彩风 | 柔和色彩过渡 | 文艺风格 |
| cyberpunk | 赛博朋克 | 霓虹色彩，科技感 | 科幻角色 |
| pixel_art | 像素艺术 | 复古像素风格 | 游戏美术 |

## 角色特征选项

### 发型 (hair_style)
- long_hair (长发), short_hair (短发), twin_tails (双马尾), ponytail (马尾辫), bob_cut (波波头), spiky (刺猬头)

### 发色 (hair_color)
- black, blonde, brown, red, blue, pink, silver, purple, gradient (渐变色)

### 眼睛颜色 (eye_color)
- blue, green, brown, red, gold, purple, heterochromia (异色瞳)

### 服装风格 (clothing_style)
- school_uniform (校服), casual (休闲装), formal (正装), fantasy_armor (奇幻铠甲), kimono (和服), maid_outfit (女仆装), gothic_lolita (哥特萝莉), sporty (运动装)

### 表情 (expression)
- happy (开心), serious (严肃), shy (害羞), angry (生气), sad (悲伤), mysterious (神秘), cool (酷炫)

## 分辨率预设

| 预设ID | 尺寸 | 说明 |
|--------|------|------|
| low | 256×256 | 快速预览 |
| medium | 512×512 | 平衡质量和速度（推荐） |
| high | 768×768 | 较高质量 |
| ultra | 1024×1024 | 最高质量 |

## 示例调用

### 生成动漫头像

```python
import requests
import base64

url = "http://localhost:8000/api/v1/avatar/generate"
data = {
    "description": "一位勇敢的女骑士，手持发光的剑",
    "style": "japanese",
    "character_features": {
        "hair_style": "long_hair",
        "hair_color": "silver",
        "eye_color": "blue",
        "clothing_style": "fantasy_armor",
        "expression": "serious"
    },
    "resolution": "high",
    "quality_mode": "balanced",
    "seed": 42,
    "user_id": "my_app"
}

response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
    if result["success"]:
        image_data = base64.b64decode(result["image_base64"])
        with output_file.open("avatar.png", "wb") as f:
            f.write(image_data)
        print(f"✓ 头像生成成功!")
        print(f"  - 使用风格: {result['style_used']}")
        print(f"  - 生成时间: {result['generation_time']}秒")
        print(f"  - 是否缓存: {'是' if result['cached'] else '否'}")
else:
    print(f"请求失败: {response.status_code}")
```

### 查询可用风格和特征

```python
import requests

# 获取所有动漫风格
response = requests.get("http://localhost:8000/api/v1/avatar/styles")
styles = response.json()["styles"]
print(f"可用风格 ({len(styles)} 种):")
for style in styles:
    print(f"  - [{style['id']}] {style['name']}")

# 获取角色特征选项
response = requests.get("http://localhost:8000/api/v1/avatar/features")
features = response.json()["features"]
print("\n可自定义的角色特征:")
for feature_type, options in features.items():
    labels = [opt["label"] for opt in options]
    print(f"  - {feature_type}: {', '.join(labels)}")

# 获取分辨率预设
response = requests.get("http://localhost:8000/api/v1/avatar/resolutions")
presets = response.json()["presets"]
print("\n分辨率预设:")
for preset in presets:
    print(f"  - [{preset['id']}] {preset['label']} ({preset['width']}x{preset['height']})")
```

### 查询生成历史

```python
import requests

# 获取最近20条生成记录
response = requests.get("http://localhost:8000/api/v1/history?limit=20&offset=0")
history = response.json()
print(f"总记录数: {history['total']}")
for record in history["records"]:
    print(f"#{record['id']} | 用户: {record['user_id']} | "
          f"风格: {record['style']} | "
          f"耗时: {record['generation_time']}s | "
          f"时间: {record['timestamp']}")
```

### 运行完整测试套件

```bash
python test_anime_api.py
```

测试套件将自动测试以下功能：
1. ✓ 健康检查接口
2. ✓ 获取可用动漫风格列表
3. ✓ 获取角色特征选项
4. ✓ 获取分辨率预设
5. ✓ 生成日系动漫头像
6. ✓ 生成Q版萌系头像
7. ✓ 缓存机制验证
8. ✓ 历史记录查询
9. ✓ 缓存统计信息

## 性能优化建议

### 选择合适的质量模式

| 场景 | 推荐配置 | 预期时间 |
|------|----------|----------|
| 快速预览 | fast + low | 2-5秒 |
| 常规使用 | balanced + medium | 5-8秒（推荐） |
| 高质量输出 | quality + high/ultra | 8-15秒 |

### 利用缓存机制

相同参数的请求会自动命中缓存，响应时间<0.1秒。建议：
- 复用常用的风格和特征组合
- 对相同描述使用固定的seed值

### 分辨率选择

- **社交媒体头像**: medium (512×512) - 推荐
- **聊天应用图标**: low (256×256) - 快速
- **打印或展示**: high (768×768) 或 ultra (1024×1024)

## 扩展性

### 添加新动漫风格

编辑 `config/styles.yaml` 文件，在 `styles` 部分添加新配置即可，无需修改代码：

```yaml
styles:
  your_new_style:
    name: "你的新风格名称"
    description: "风格描述"
    prompt_prefix: "风格提示词前缀, "
    prompt_suffix: ", 风格提示词后缀"
    negative_suffix: ", 要排除的元素"
    quality_tags:
      - "tag1"
      - "tag2"
    style_strength: 1.0
```

### 添加新角色特征

在 `config/styles.yaml` 的 `character_features` 部分添加新的特征类别：

```yaml
character_features:
  new_feature_type:
    options:
      - value: "option1"
        label: "选项名称"
        prompt_addition: "对应的提示词, "
```

重启服务后新配置即可生效。

## 故障排除

### 模型加载失败

1. 确保网络连接正常（首次加载需下载配置文件）
2. 在 `config.yaml` 设置 `pipeline_config`：
   - SDXL: `stabilityai/stable-diffusion-xl-base-1.0`
   - SD1.5: `runwayml/stable-diffusion-v1-5`
3. 启用离线模式：`offline_mode: true`

### 生成超时

1. 降低分辨率（使用 medium 或 low）
2. 使用 fast 质量模式
3. 减少推理步数

### CUDA内存不足

1. 降低分辨率到 512×512 或更低
2. 使用 fast 模式减少内存占用
3. 关闭其他占用GPU的程序

### 缓存问题

如果遇到缓存相关问题：
- 查看缓存统计：GET `/api/v1/cache/stats`
- 手动清除缓存：DELETE `/api/v1/cache`
- 在配置中调整 `cache_max_size`

## 技术架构

```
┌─────────────────────────────────────────────┐
│                  客户端 (前端)                 │
└─────────────────────┬───────────────────────┘
                      │ HTTP REST API
┌─────────────────────▼───────────────────────┐
│           FastAPI 应用层 (app/main.py)        │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ avatar.py   │  │ history.py           │  │
│  │ (头像生成)   │  │ (历史&缓存)           │  │
│  └──────┬──────┘  └──────────┬───────────┘  │
└─────────┼────────────────────┼──────────────┘
          │                    │
┌─────────▼────────────────────▼──────────────┐
│              服务层 (services/)              │
│  ┌──────────────────┐  ┌─────────────────┐  │
│  │anime_avatar_service│  │ style_manager   │  │
│  │ (头像生成核心)     │  │ (风格管理)       │  │
│  └────────┬─────────┘  └─────────────────┘  │
│           │                                   │
│  ┌────────▼─────────┐                        │
│  │  sd_service.py   │  (Stable Diffusion)    │
│  └────────┬─────────┘                        │
└───────────┼──────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────┐
│              数据层                            │
│  ┌─────────────┐  ┌──────────┐  ┌─────────┐  │
│  │ styles.yaml │  │ 内存缓存  │  │历史记录  │  │
│  └─────────────┘  └──────────┘  └─────────┘  │
└──────────────────────────────────────────────┘
```

## 版本信息

- **当前版本**: 2.0.0
- **更新日期**: 2024-01-15
- **主要更新**: 
  - ✨ 新增AI动漫头像生成功能
  - 🎨 支持6种动漫风格
  - 👤 支持5类角色特征自定义
  - ⚡ 性能优化，确保≤10秒响应
  - 💾 智能缓存和历史记录功能
  - 📚 完整的API文档和测试套件

