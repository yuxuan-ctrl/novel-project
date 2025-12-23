# Gemini Nano Banana Skill

Gemini 2.5 Flash Image Preview (俗称 Nano Banana) - 支持文本生图和图片编辑

## 功能概述

- **文本生图**: 根据文本描述生成高质量图片
- **图片编辑**: 基于现有图片进行AI编辑和修改
- **特点**: 理解力强，擅长创意和艺术风格，英文提示词效果更好

## API信息

- **模型**: gemini-2.5-flash-image-preview
- **API端点**: https://aigc-backend-stage.skyengine.com.cn/eliza/v1beta/
- **认证**: Bearer promptt-dev:promptt-dev

## 使用方法

### 1. 文本生图

```bash
python text_to_image.py <提示词> [输出路径]
```

**参数说明:**
- `提示词`: 图片描述文本，英文效果更好（必填）
- `输出路径`: 保存路径，不指定则自动生成（可选）

**示例:**
```bash
# 基础用法
python text_to_image.py "Create a picture of a nano banana dish in a fancy restaurant"

# 指定输出路径
python text_to_image.py "A white-robed cultivator standing on a mountain peak" linxuan.png

# 创意场景
python text_to_image.py "A mystical temple under the Gemini constellation with ethereal lighting"
```

### 2. 图片编辑

```bash
python image_to_image.py <输入图片> <提示词> [输出路径]
```

**参数说明:**
- `输入图片`: 本地图片路径或URL（必填）
- `提示词`: 编辑描述文本，英文效果更好（必填）
- `输出路径`: 保存路径，不指定则自动生成（可选）

**示例:**
```bash
# 基础用法
python image_to_image.py input.png "Add rainbow and clouds to the sky"

# 完整路径
python image_to_image.py linxuan.png "Change background to bamboo forest with morning mist" output.png

# 使用URL作为输入
python image_to_image.py https://example.com/image.png "Add golden halo effect around the character"
```

## Python调用示例

### 文本生图

```python
from text_to_image import generate_image

# 生成图片
generate_image(
    "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme",
    "nano_banana.png"
)

# 角色生成
generate_image(
    "A white-robed cultivator with long black hair standing on a mountain peak at sunset",
    "character.png"
)
```

### 图片编辑

```python
from image_to_image import image_to_image

# 编辑本地图片
image_to_image(
    "input.png",
    "Create a picture of my cat eating a nano-banana in a fancy restaurant under the Gemini constellation",
    "output.png"
)

# 使用URL
image_to_image(
    "https://example.com/character.png",
    "Add mystical energy aura and floating particles around the character",
    "enhanced.png"
)
```

## 特性说明

### 文本生图
- **创意理解**: 擅长理解复杂的创意描述
- **艺术风格**: 生成具有艺术感的图片
- **场景构建**: 能够理解复杂的场景组合

### 图片编辑
- **智能编辑**: 基于原图进行智能修改
- **风格融合**: 可以添加新元素同时保持原图风格
- **灵活输入**: 支持本地文件和URL
- **格式支持**: JPEG, PNG, WebP, GIF

## 提示词技巧

### 推荐使用英文
虽然支持中文，但英文提示词通常能获得更好的结果。

### 文本生图提示词结构
```
[主体] + [动作/状态] + [环境/背景] + [风格/氛围]
```

**示例:**
```
A white-robed cultivator (主体)
standing with arms crossed (动作)
on a misty mountain peak at dawn (环境)
in semi-realistic anime style with dramatic lighting (风格)
```

### 图片编辑提示词结构
```
[动作] + [要添加/修改的元素] + [位置] + [效果描述]
```

**示例:**
```
Add golden mystical energy particles
around the character
with soft glowing effect and warm color tone
```

## 常见应用场景

### 角色设计
```bash
python text_to_image.py "A monk in golden robes with serene expression, holding a staff, Buddhist temple background, semi-realistic anime style" monk.png
```

### 场景生成
```bash
python text_to_image.py "Ancient Chinese temple on mountain top, surrounded by clouds, golden hour lighting, mystical atmosphere" temple.png
```

### 图片增强
```bash
python image_to_image.py character.png "Add magical aura and energy particles, enhance lighting and depth" enhanced.png
```

### 风格转换
```bash
python image_to_image.py photo.png "Transform into anime art style with vibrant colors and soft shading" anime_style.png
```

## 注意事项

1. **依赖库**: 确保安装 `requests`
2. **API密钥**: 已内置 `promptt-dev:promptt-dev`
3. **提示词语言**: 英文提示词效果通常更好
4. **输出格式**: 默认保存为PNG格式
5. **图片编辑**: 会智能理解原图内容并进行相应修改
6. **创意生成**: 特别适合需要创意和艺术感的图片生成

## 与Seedream的对比

| 特性 | Gemini Nano Banana | Doubao Seedream |
|------|-------------------|-----------------|
| 创意理解 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 艺术风格 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 写实效果 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中文支持 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 批量生成 | ❌ | ✅ |
| 保真度控制 | ❌ | ✅ |

## 使用建议

- **角色设计**: 适合创意角色和艺术风格
- **场景构建**: 擅长氛围和意境表达
- **图片编辑**: 适合添加创意元素和效果
- **提示词**: 使用详细的英文描述获得最佳效果
