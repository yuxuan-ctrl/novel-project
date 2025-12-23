#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包即梦 Seedream 4.0 - 文本生图
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import base64
import os
from datetime import datetime

API_URL = "https://aigc-backend.skyengine.com.cn/eliza/v1/images/generations"
API_KEY = "promptt-dev:promptt-dev"

def generate_image(prompt, output_path=None, size="1024x1024", num_images=1):
    """
    文本生成图片

    Args:
        prompt: 图片描述提示词
        output_path: 输出路径，不指定则自动生成
        size: 图片尺寸，默认1024x1024
        num_images: 生成图片数量
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": prompt,
        "sequential_image_generation": "auto",
        "sequential_image_generation_options": {
            "max_images": num_images
        },
        "size": size
    }

    print(f"正在生成图片...")
    print(f"提示词: {prompt}")
    print(f"尺寸: {size}")

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()

        if "data" in result:
            saved_files = []
            for idx, item in enumerate(result["data"], 1):
                if "url" in item:
                    # 下载图片
                    image_url = item["url"]
                    img_response = requests.get(image_url)

                    if img_response.status_code == 200:
                        # 生成输出路径
                        if output_path:
                            if num_images > 1:
                                base, ext = os.path.splitext(output_path)
                                file_path = f"{base}_{idx}{ext}"
                            else:
                                file_path = output_path
                        else:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            file_path = f"seedream_{timestamp}_{idx}.png"

                        # 保存图片
                        with open(file_path, 'wb') as f:
                            f.write(img_response.content)

                        saved_files.append(file_path)
                        print(f"✅ 图片 {idx} 已保存: {file_path}")

                elif "b64_json" in item:
                    # Base64格式
                    image_data = base64.b64decode(item["b64_json"])

                    if output_path:
                        if num_images > 1:
                            base, ext = os.path.splitext(output_path)
                            file_path = f"{base}_{idx}{ext}"
                        else:
                            file_path = output_path
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_path = f"seedream_{timestamp}_{idx}.png"

                    with open(file_path, 'wb') as f:
                        f.write(image_data)

                    saved_files.append(file_path)
                    print(f"✅ 图片 {idx} 已保存: {file_path}")

            return saved_files
        else:
            print(f"❌ 响应中未找到图片数据")
            print(f"响应内容: {result}")
            return None
    else:
        print(f"❌ API错误: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python text_to_image.py <提示词> [输出路径] [尺寸] [数量]")
        print("示例: python text_to_image.py '一个美丽的日落场景' output.png 1024x1024 1")
        sys.exit(1)

    prompt = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    size = sys.argv[3] if len(sys.argv) > 3 else "1024x1024"
    num_images = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    generate_image(prompt, output_path, size, num_images)
