# Doubao Seedream Skill

豆包即梦 4.0 图像生成能力 - 支持文本生图和图片编辑

## 功能概述

- **文本生图**: 根据文本描述生成高质量图片
- **图片编辑**: 基于现有图片进行AI编辑和修改

## API信息

- **模型**: doubao-seedream-4-0-250828
- **API端点**: https://aigc-backend.skyengine.com.cn/eliza/v1/
- **认证**: Bearer promptt-dev:promptt-dev

## 使用方法

### 1. 文本生图

```bash
python text_to_image.py <提示词> [输出路径] [尺寸] [数量]
```

**参数说明:**
- `提示词`: 图片描述文本（必填）
- `输出路径`: 保存路径，不指定则自动生成（可选）
- `尺寸`: 图片尺寸，默认 1024x1024（可选）
- `数量`: 生成图片数量，默认 1（可选）

**示例:**
```bash
# 基础用法
python text_to_image.py "一个美丽的日落场景"

# 指定输出路径
python text_to_image.py "白衣修仙者站在山峰" linxuan.png

# 指定尺寸和数量
python text_to_image.py "游乐园过山车" rides.png 1024x1024 3
```

### 2. 图片编辑

```bash
python image_to_image.py <输入图片> <提示词> [输出路径] [保真度] [质量] [尺寸]
```

**参数说明:**
- `输入图片`: 本地图片路径或URL（必填）
- `提示词`: 编辑描述文本（必填）
- `输出路径`: 保存路径，不指定则自动生成（可选）
- `保真度`: low/medium/high，默认 high（可选）
- `质量`: standard/hd，默认 hd（可选）
- `尺寸`: 输出尺寸，默认 1024x1024（可选）

**示例:**
```bash
# 基础用法
python image_to_image.py input.png "添加彩虹和云朵到天空中"

# 完整参数
python image_to_image.py linxuan.png "改变背景为竹林" output.png high hd 1024x1024

# 使用URL作为输入
python image_to_image.py https://example.com/image.png "添加光环效果"
```

## Python调用示例

### 文本生图

```python
from text_to_image import generate_image

# 生成单张图片
generate_image("一个美丽的日落场景", "sunset.png")

# 生成多张图片
generate_image("不同时间的游乐园", "park.png", num_images=3)
```

### 图片编辑

```python
from image_to_image import image_to_image

# 编辑本地图片
image_to_image("input.png", "添加彩虹", "output.png")

# 使用URL
image_to_image(
    "https://example.com/image.png",
    "改变天空颜色为金色",
    "golden_sky.png",
    input_fidelity="high",
    quality="hd"
)
```

## 特性说明

### 文本生图
- **sequential_image_generation**: 自动模式，智能理解提示词中的数量需求
- **尺寸支持**: 灵活的图片尺寸配置
- **批量生成**: 支持一次生成多张图片

### 图片编辑
- **input_fidelity**: 控制对原图的保留程度
  - `low`: 较大变化，AI创作自由度高
  - `medium`: 中等变化，平衡原图和创作
  - `high`: 保留原图特征，精细编辑
- **quality**: 输出质量控制
  - `standard`: 标准质量
  - `hd`: 高清质量
- **输入支持**: 本地文件或URL

## 注意事项

1. 确保安装依赖: `requests`
2. API密钥已内置: `promptt-dev:promptt-dev`
3. 生成的图片默认保存在当前目录
4. 支持中文提示词
5. 图片编辑会根据提示词智能修改原图

## 常见应用场景

- **角色设计**: 生成小说角色的视觉形象
- **场景构建**: 创建故事场景图片
- **图片优化**: 为现有图片添加元素或效果
- **批量生成**: 快速生成多个变体图片
