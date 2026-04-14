# AI动漫头像生成服务 API文档

## 概述

AI动漫头像生成服务是基于FastAPI框架开发的后端服务，专门用于生成高质量的动漫风格头像图片。该服务支持多种动漫风格、角色特征自定义、智能缓存和生成历史记录功能。

**基础URL**: `http://localhost:8000`  
**API版本**: v1  
**认证方式**: 无需认证（可扩展添加）

---

## 目录

1. [通用说明](#通用说明)
2. [核心接口](#核心接口)
3. [查询接口](#查询接口)
4. [历史记录接口](#历史记录接口)
5. [缓存管理接口](#缓存管理接口)
6. [错误码说明](#错误码说明)
7. [使用示例](#使用示例)

---

## 通用说明

### 请求格式

- **Content-Type**: `application/json`
- **字符编码**: `UTF-8`

### 响应格式

所有响应均采用JSON格式：

```json
{
  "success": true/false,
  "data": {...},
  "error": "错误信息（仅失败时）"
}
```

### 时间戳格式

所有时间戳均采用ISO 8601格式：`YYYY-MM-DDTHH:MM:SS.ssssss`

---

## 核心接口

### 1. 生成动漫头像

**POST** `/api/v1/avatar/generate`

根据指定的风格、角色特征和参数生成动漫风格的头像图片。

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| description | string | 是 | - | 角色描述（1-1000字符） |
| style | string | 否 | japanese | 动漫风格ID（见风格列表） |
| character_features | object | 否 | null | 角色特征自定义 |
| resolution | string | 否 | medium | 分辨率预设 |
| quality_mode | string | 否 | balanced | 质量模式 |
| seed | integer | 否 | -1 | 随机种子（-1为随机） |
| reference_image | string | 否 | null | 参考图片Base64编码 |
| user_id | string | 否 | anonymous | 用户标识 |

#### character_features 对象结构

| 字段名 | 类型 | 可选值 | 说明 |
|--------|------|--------|------|
| hair_style | string | long_hair, short_hair, twin_tails, ponytail, bob_cut, spiky | 发型 |
| hair_color | string | black, blonde, brown, red, blue, pink, silver, purple, gradient | 发色 |
| eye_color | string | blue, green, brown, red, gold, purple, heterochromia | 眼睛颜色 |
| clothing_style | string | school_uniform, casual, formal, fantasy_armor, kimono, maid_outfit, gothic_lolita, sporty | 服装风格 |
| expression | string | happy, serious, shy, angry, sad, mysterious, cool | 表情 |

#### resolution 可选值

| 值 | 尺寸 | 说明 |
|----|------|------|
| low | 256×256 | 低分辨率，快速预览 |
| medium | 512×512 | 中等分辨率，平衡质量和速度 |
| high | 768×768 | 高分辨率，较高质量 |
| ultra | 1024×1024 | 超高分辨率，最高质量 |

#### quality_mode 可选值

| 值 | 推理步数 | 引导系数 | 采样器 | 说明 |
|----|----------|----------|--------|------|
| fast | 15 | 7.0 | euler_a | 快速模式，适合预览 |
| balanced | 20 | 7.5 | euler | 平衡模式，推荐使用 |
| quality | 30 | 8.0 | dpm++2m_karras | 质量模式，最佳效果 |

#### 响应示例

**成功响应 (200)**:

```json
{
  "success": true,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "image_url": "/images/avatar_20240115_143022_12345.png",
  "seed": 42,
  "style_used": "japanese",
  "character_features_applied": {
    "hair_style": "long_hair",
    "hair_color": "silver",
    "eye_color": "blue",
    "clothing_style": "fantasy_armor",
    "expression": "serious"
  },
  "resolution": {
    "width": 512,
    "height": 512,
    "preset": "medium"
  },
  "parameters": {
    "positive_prompt": "anime style, Japanese anime, detailed anime art, long hair, silver hair, blue eyes, fantasy armor, serious expression, 一位勇敢的女骑士，手持发光的剑, high quality, masterpiece...",
    "negative_prompt": "low quality, bad anatomy, blurry, realistic, 3d render, photo",
    "width": 512,
    "height": 512,
    "num_inference_steps": 20,
    "guidance_scale": 7.5
  },
  "generation_time": 8.52,
  "cached": false,
  "timestamp": "2024-01-15T14:30:22.123456",
  "user_id": "test_user"
}
```

**错误响应 (400)**:

```json
{
  "detail": "未知的风格ID: invalid_style"
}
```

**错误响应 (500)**:

```json
{
  "detail": "动漫头像生成失败: 模型加载失败"
}
```

---

## 查询接口

### 2. 获取可用动漫风格列表

**GET** `/api/v1/avatar/styles`

获取系统支持的所有动漫风格及其详细信息。

#### 响应示例

```json
{
  "styles": [
    {
      "id": "japanese",
      "name": "日系动漫",
      "description": "经典日式动漫风格，细腻的线条和柔和的色彩",
      "quality_tags": ["masterpiece", "best quality", "ultra-detailed", "illustration"],
      "style_strength": 1.0
    },
    {
      "id": "american_comic",
      "name": "美漫风格",
      "description": "美式漫画风格，粗犷的线条和强烈的对比",
      "quality_tags": ["comic book", "graphic novel", "bold outlines", "dynamic"],
      "style_strength": 0.9
    }
  ],
  "total": 6
}
```

---

### 3. 获取角色特征选项

**GET** `/api/v1/avatar/features`

获取可自定义的角色特征分类及各选项列表。

#### 响应示例

```json
{
  "features": {
    "hair_style": [
      {"value": "long_hair", "label": "长发"},
      {"value": "short_hair", "label": "短发"},
      {"value": "twin_tails", "label": "双马尾"},
      {"value": "ponytail", "label": "马尾辫"},
      {"value": "bob_cut", "label": "波波头"},
      {"value": "spiky", "label": "刺猬头"}
    ],
    "hair_color": [
      {"value": "black", "label": "黑色"},
      {"value": "blonde", "label": "金色"},
      {"value": "brown", "label": "棕色"}
    ]
  }
}
```

---

### 4. 获取分辨率预设列表

**GET** `/api/v1/avatar/resolutions`

获取支持的分辨率预设选项及其详细配置。

#### 响应示例

```json
{
  "presets": [
    {
      "id": "low",
      "width": 256,
      "height": 256,
      "label": "低分辨率 (256x256)",
      "description": "快速生成，适合预览"
    },
    {
      "id": "medium",
      "width": 512,
      "height": 512,
      "label": "中等分辨率 (512x512)",
      "description": "平衡质量和速度"
    },
    {
      "id": "high",
      "width": 768,
      "height": 768,
      "label": "高分辨率 (768x768)",
      "description": "较高质量，需要更多时间"
    },
    {
      "id": "ultra",
      "width": 1024,
      "height": 1024,
      "label": "超高分辨率 (1024x1024)",
      "description": "最高质量，生成时间较长"
    }
  ],
  "total": 4
}
```

---

## 历史记录接口

### 5. 获取生成历史记录

**GET** `/api/v1/history`

查询用户的动漫头像生成历史记录，支持分页和用户筛选。

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| user_id | string | 否 | null | 用户ID（不传返回所有） |
| limit | integer | 否 | 20 | 每页数量(1-100) |
| offset | integer | 否 | 0 | 偏移量 |

#### 响应示例

```json
{
  "total": 25,
  "limit": 10,
  "offset": 0,
  "has_more": true,
  "records": [
    {
      "id": 25,
      "timestamp": "2024-01-15T14:30:22.123456",
      "user_id": "test_user",
      "style": "japanese",
      "resolution": "medium",
      "generation_time": 8.52,
      "seed": 42
    },
    {
      "id": 24,
      "timestamp": "2024-01-15T14:28:15.654321",
      "user_id": "test_user",
      "style": "chibi_q",
      "resolution": "medium",
      "generation_time": 6.23,
      "seed": 123
    }
  ]
}
```

---

### 6. 清除历史记录

**DELETE** `/api/v1/history`

清除指定用户或所有用户的生成历史记录。

#### 查询参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | string | 否 | 要清除的用户ID（不传则清除全部） |

#### 响应示例

```json
{
  "success": true,
  "cleared_count": 15,
  "message": "已成功清除 15 条历史记录"
}
```

---

## 缓存管理接口

### 7. 获取缓存统计信息

**GET** `/api/v1/cache/stats`

查看当前缓存和历史记录的使用情况。

#### 响应示例

```json
{
  "cache_size": 45,
  "cache_max_size": 100,
  "history_size": 150,
  "history_max_size": 1000
}
```

---

### 8. 清除缓存

**DELETE** `/api/v1/cache`

清除所有缓存的生成结果，释放内存空间。

#### 响应示例

```json
{
  "success": true,
  "cleared_count": 45,
  "message": "已成功清除 45 条缓存记录"
}
```

---

## 错误码说明

| HTTP状态码 | 错误类型 | 说明 |
|------------|----------|------|
| 400 | Bad Request | 请求参数错误或无效 |
| 404 | Not Found | 请求的资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

### 常见错误信息

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| 未知的风格ID: xxx | 风格ID不存在 | 使用 /avatar/styles 获取有效风格列表 |
| 未知的分辨率预设: xxx | 分辨率预设不存在 | 使用 /avatar/resolutions 获取有效预设列表 |
| 描述不能为空 | description字段为空 | 提供有效的角色描述 |
| 动漫头像生成失败: xxx | SD模型生成失败 | 检查日志文件，确认模型已正确加载 |
| 生成时间超过限制 | 单次生成超过10秒 | 降低分辨率或使用fast质量模式 |

---

## 使用示例

### Python示例

```python
import requests
import base64

BASE_URL = "http://localhost:8000"

def generate_anime_avatar():
    payload = {
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
        "user_id": "my_app_user"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/avatar/generate",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if data["success"]:
            image_data = base64.b64decode(data["image_base64"])
            
            with output_file.open("avatar.png", "wb") as f:
                f.write(image_data)
            
            print(f"✓ 头像生成成功!")
            print(f"  - 生成时间: {data['generation_time']}秒")
            print(f"  - 使用风格: {data['style_used']}")
            print(f"  - 分辨率: {data['resolution']['width']}x{data['resolution']['height']}")
            print(f"  - 图片已保存到: avatar.png")
        else:
            print(f"✗ 生成失败: {data.get('error', '未知错误')}")
    else:
        print(f"✗ 请求失败: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    generate_anime_avatar()
```

### cURL示例

```bash
curl -X POST "http://localhost:8000/api/v1/avatar/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "可爱的魔法少女",
    "style": "chibi_q",
    "character_features": {
      "hair_style": "twin_tails",
      "hair_color": "pink",
      "expression": "happy"
    },
    "resolution": "medium",
    "quality_mode": "fast",
    "seed": 123
  }'
```

### JavaScript/Node.js示例

```javascript
const axios = require('axios');
const fs = require('fs');

async function generateAvatar() {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/avatar/generate', {
      description: "赛博朋克黑客",
      style: "cyberpunk",
      character_features: {
        hair_style: "short_hair",
        hair_color: "gradient",
        eye_color: "red",
        clothing_style: "casual",
        expression: "cool"
      },
      resolution: "high",
      quality_mode: "quality",
      user_id: "web_user_001"
    });
    
    const data = response.data;
    
    if (data.success) {
      const imageData = Buffer.from(data.image_base64, 'base64');
      fs.writeFileSync('cyberpunk_avatar.png', imageData);
      
      console.log(`✓ 头像生成成功!`);
      console.log(`  - 生成时间: ${data.generation_time}秒`);
      console.log(`  - 图片已保存到: cyberpunk_avatar.png`);
    } else {
      console.log(`✗ 生成失败: ${data.error}`);
    }
    
  } catch (error) {
    console.error('✗ 请求失败:', error.message);
  }
}

generateAvatar();
```

---

## 性能优化建议

### 1. 选择合适的质量模式

- **预览和批量生成**: 使用 `fast` 模式 + `low` 分辨率
- **常规使用**: 使用 `balanced` 模式 + `medium` 分辨率（推荐）
- **高质量输出**: 使用 `quality` 模式 + `high` 或 `ultra` 分辨率

### 2. 利用缓存机制

相同参数的重复请求会自动命中缓存，显著提升响应速度。建议：
- 固定常用的风格和特征组合
- 对于相同描述的角色复用相同的seed值

### 3. 分辨率选择建议

| 使用场景 | 推荐分辨率 | 理由 |
|----------|------------|------|
| 头像图标 | 256×256 | 快速生成，足够清晰 |
| 社交媒体 | 512×512 | 标准头像尺寸 |
| 打印输出 | 768×768 或更高 | 保证打印质量 |

---

## 支持的动漫风格详情

### 1. 日系动漫 (japanese)

- **特点**: 经典日式动漫风格，细腻的线条和柔和的色彩
- **适用场景**: 通用型，适合大多数动漫角色设计
- **风格强度**: 1.0

### 2. 美漫风格 (american_comic)

- **特点**: 美式漫画风格，粗犷的线条和强烈的对比
- **适用场景**: 英雄角色、动作场景
- **风格强度**: 0.9

### 3. Q版萌系 (chibi_q)

- **特点**: 可爱Q版风格，夸张的比例和大眼睛设计
- **适用场景**: 可爱角色、吉祥物、表情包
- **风格强度**: 1.1

### 4. 水彩风 (watercolor)

- **特点**: 水彩画风格的动漫艺术，柔和的色彩过渡
- **适用场景**: 文艺风格、梦幻场景
- **风格强度**: 0.95

### 5. 赛博朋克 (cyberpunk)

- **特点**: 未来科技感的赛博朋克风格，霓虹色彩和机械元素
- **适用场景**: 科幻角色、游戏概念图
- **风格强度**: 1.0

### 6. 像素艺术 (pixel_art)

- **特点**: 复古像素风格，8位/16位游戏美术风格
- **适用场景**: 复古游戏、像素艺术爱好者
- **风格强度**: 1.05

---

## 扩展性说明

### 添加新动漫风格

编辑 `config/styles.yaml` 文件，在 `styles` 部分添加新的风格配置：

```yaml
styles:
  new_style:
    name: "新风格名称"
    description: "风格描述"
    prompt_prefix: "风格特定的提示词前缀, "
    prompt_suffix: ", 风格特定的提示词后缀"
    negative_suffix: ", 要排除的风格元素"
    quality_tags:
      - "tag1"
      - "tag2"
    style_strength: 1.0
```

### 添加新角色特征

在 `config/styles.yaml` 的 `character_features` 部分添加新的特征类别：

```yaml
character_features:
  new_feature:
    options:
      - value: "option1"
        label: "选项1"
        prompt_addition: "对应的提示词, "
      - value: "option2"
        label: "选项2"
        prompt_addition: "对应的提示词, "
```

### 添加新分辨率预设

在 `config/styles.yaml` 的 `resolution_presets` 部分添加：

```yaml
resolution_presets:
  custom:
    width: 640
    height: 640
    label: "自定义分辨率 (640x640)"
    description: "自定义分辨率说明"
```

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 2.0.0 | 2024-01-15 | 初始版本，支持6种动漫风格、角色自定义、缓存和历史记录 |

---

## 联系与支持

如有问题或建议，请通过以下方式联系：
- GitHub Issues: [项目地址]/issues
- Email: support@example.com