#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用nano-banana API生成指定图像
"""

import requests
import base64
import os
from PIL import Image
from io import BytesIO
import sys

API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1beta"

def edit_image_direct(character_image_path, scene_prompt, output_path):
    """使用 Gemini 图生图 API 生成场景图像"""
    url = f"{BASE_URL}/models/gemini-2.5-flash-image:generateContent"

    # 读取并编码角色形象图
    with open(character_image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # 确定 MIME 类型
    mime_type = "image/png"
    if character_image_path.lower().endswith(('.jpg', '.jpeg')):
        mime_type = "image/jpeg"
    elif character_image_path.lower().endswith('.webp'):
        mime_type = "image/webp"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 构建完整的图生图提示词
    full_prompt = f"""
请基于提供的角色形象，生成以下场景的图像。
务必保持角色的外貌、服装、气质与参考图像完全一致。

场景描述：
{scene_prompt}

要求：
1. 角色外貌、服装必须与参考图像完全一致
2. 场景环境按照描述生成
3. 中国动画电影风格，手绘质感
4. 细腻光影层次，丰富质感细节
"""

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    },
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": image_data
                        }
                    }
                ]
            }
        ]
    }

    print(f"正在生成场景图像...")
    print(f"角色参考: {character_image_path}")
    print(f"场景描述: {scene_prompt[:100]}...")

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()

        # 提取并保存编辑后的图像
        for candidate in result.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    image_data = base64.b64decode(part['inlineData']['data'])
                    image = Image.open(BytesIO(image_data))

                    # 创建输出目录
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    image.save(output_path)
                    print(f"图像已保存: {output_path}")
                    return True

        print("响应中未找到图像数据")
        return False
    else:
        print(f"API 错误: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    # 参数设置
    character_image = "D:/AI/novel-claude-project/character_images/huijue.png"
    scene_prompt = "Chinese animation movie style, medium shot of monk Huijue (from huijue.png) standing before execution platform, hands in prayer, wearing magnificent golden robes, merciful face but cunning eyes, background shows Lin Xuan kneeling on dark stone platform, bright golden light from above, cinematic lighting, hand-painted texture"
    output_path = "D:/AI/novel-claude-project/outputs/run_20250213_153000_anime/05_generated_images/Episode-01/Episode-01-Shot-004-Fixed.png"

    # 生成图像
    if edit_image_direct(character_image, scene_prompt, output_path):
        print("生成成功！")
    else:
        print("生成失败！")