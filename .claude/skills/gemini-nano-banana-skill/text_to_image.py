#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 2.5 Flash Image (Nano Banana) - 文本生图
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

def generate_image(prompt, output_path=None):
    """
    文本生成图片

    Args:
        prompt: 图片描述提示词（英文效果更好）
        output_path: 输出路径，不指定则自动生成
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    print(f"正在生成图片...")
    print(f"提示词: {prompt}")

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
                        output_path = f"gemini_{timestamp}.png"

                    # 保存图片
                    with open(output_path, 'wb') as f:
                        f.write(image_data)

                    print(f"✅ 图片已保存: {output_path}")
                    return output_path

        print(f"❌ 响应中未找到图片数据")
        print(f"响应内容: {result}")
        return None
    else:
        print(f"❌ API错误: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python text_to_image.py <提示词> [输出路径]")
        print("示例: python text_to_image.py 'Create a picture of a nano banana dish in a fancy restaurant' output.png")
        print("注意: 英文提示词效果更好")
        sys.exit(1)

    prompt = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    generate_image(prompt, output_path)
