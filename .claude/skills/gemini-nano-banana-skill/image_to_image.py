#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 2.5 Flash Image (Nano Banana) - 图片编辑（图生图）
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import base64
import os
from datetime import datetime

API_URL = "https://aigc-backend.skyengine.com.cn/eliza/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
API_KEY = "promptt-dev:promptt-dev"

def url_to_base64(url):
    """URL图片转base64"""
    response = requests.get(url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')

def local_image_to_base64(image_path):
    """本地图片转base64"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_mime_type(image_path):
    """根据文件扩展名获取MIME类型"""
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.gif': 'image/gif'
    }
    return mime_types.get(ext, 'image/jpeg')

def image_to_image(image_path, prompt, output_path=None):
    """
    图片编辑（图生图）

    Args:
        image_path: 输入图片路径（本地路径或URL）
        prompt: 编辑描述提示词（英文效果更好）
        output_path: 输出路径，不指定则自动生成
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 判断是URL还是本地路径，并转换为base64
    if image_path.startswith("http://") or image_path.startswith("https://"):
        print(f"从URL加载图片: {image_path}")
        image_base64 = url_to_base64(image_path)
        mime_type = "image/jpeg"  # URL默认使用jpeg
    else:
        print(f"从本地加载图片: {image_path}")
        image_base64 = local_image_to_base64(image_path)
        mime_type = get_mime_type(image_path)

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    },
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": image_base64
                        }
                    }
                ],
                "role": "user"
            }
        ]
    }

    print(f"正在编辑图片...")
    print(f"编辑提示词: {prompt}")

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()

        # 提取生成的图片
        for candidate in result.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    # 解码base64图片
                    image_data = base64.b64decode(part['inlineData']['data'])

                    # 生成输出路径
                    if not output_path:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_path = f"gemini_edited_{timestamp}.png"

                    # 保存图片
                    with open(output_path, 'wb') as f:
                        f.write(image_data)

                    print(f"✅ 编辑后图片已保存: {output_path}")
                    return output_path

        print(f"❌ 响应中未找到图片数据")
        print(f"响应内容: {result}")
        return None
    else:
        print(f"❌ API错误: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python image_to_image.py <输入图片> <提示词> [输出路径]")
        print("示例: python image_to_image.py input.png 'Add rainbow and clouds to the sky' output.png")
        print("注意: 英文提示词效果更好")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None

    image_to_image(image_path, prompt, output_path)
