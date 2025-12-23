# Doubao Seedream 4.5 图像生成技能

## 概述
使用豆包Seedream 4.5模型进行高质量图像生成，支持文生图和图生图功能。

## API配置
- API_KEY: "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
- BASE_URL: "https://model-api.skyengine.com.cn/v1"
- 模型: doubao-seedream-4-0-250828

## 核心功能
1. **文生图生成**：根据文本描述生成图像
2. **图生图编辑**：基于参考图片生成新图片
3. **多图融合**：将多张图片元素组合
4. **组图生成**：生成多张相关场景

## 使用方法

### 基础文生图
```python
def generate_image(prompt, model="doubao-seeddream-4-0-250828", size="1024x1024"):
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "response_format": "url",
        "watermark": False  # 可以根据需要设置
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

### 图生图
```python
def image_to_image(prompt, image_url, model="doubao-seeddream-4-0-250828", size="1024x1024"):
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "prompt": prompt,
        "image": image_url,
        "model": model,
        "size": size,
        "response_format": "url",
        "watermark": False
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

## 参数说明
- prompt: 图片描述文本（必需）
- model: 模型名称，默认doubao-seedream-4-0-250828
- size: 图片尺寸（支持256x256, 512x512, 1024x1024等）
- response_format: 返回格式（url 或 b64_json）
- watermark: 是否添加水印（默认true）
- image: 基础图片URL（图生图时使用）
- sequential_image_generation: 组图功能（enabled/disabled/auto）

## 注意事项
1. guidance_scale参数不支持
2. seed参数可以传入但不生效
3. 图片URL有效期为24小时
4. 图生图时保持人物特征，可使用"from input image"强调

## 风格建议
对于中国动画电影风格，建议使用：
- "Chinese animation movie style"
- "hand-painted texture"
- "cinematic lighting"
- 避免"3D rendered style"等过度3D的描述