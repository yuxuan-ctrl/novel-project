#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包即梦 Seedream 4.0 - 图片编辑（图生图）
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import base64
import os
from datetime import datetime

API_URL = "https://aigc-backend.skyengine.com.cn/eliza/v1/images/edits"
API_KEY = "promptt-dev:promptt-dev"

def image_to_image(image_path, prompt, output_path=None, input_fidelity="high", quality="hd", size="1024x1024"):
    """
    图片编辑（图生图）

    Args:
        image_path: 输入图片路径（本地路径或URL）
        prompt: 编辑描述提示词
        output_path: 输出路径，不指定则自动生成
        input_fidelity: 输入保真度 (low/medium/high)
        quality: 输出质量 (standard/hd)
        size: 输出尺寸
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 判断是URL还是本地路径
    if image_path.startswith("http://") or image_path.startswith("https://"):
        image_input = image_path
    else:
        # 本地文件转base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        image_input = f"data:image/png;base64,{image_data}"

    payload = {
        "model": "doubao-seedream-4-0-250828",
        "image": image_input,
        "prompt": prompt,
        "input_fidelity": input_fidelity,
        "quality": quality,
        "size": size,
        "n": 1
    }

    print(f"正在编辑图片...")
    print(f"输入图片: {image_path}")
    print(f"编辑提示词: {prompt}")
    print(f"保真度: {input_fidelity}, 质量: {quality}")

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()

        if "data" in result and len(result["data"]) > 0:
            item = result["data"][0]

            if "url" in item:
                # 下载图片
                image_url = item["url"]
                img_response = requests.get(image_url)

                if img_response.status_code == 200:
                    if not output_path:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_path = f"seedream_edited_{timestamp}.png"

                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)

                    print(f"✅ 编辑后图片已保存: {output_path}")
                    return output_path

            elif "b64_json" in item:
                # Base64格式
                image_data = base64.b64decode(item["b64_json"])

                if not output_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = f"seedream_edited_{timestamp}.png"

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
        print("用法: python image_to_image.py <输入图片> <提示词> [输出路径] [保真度] [质量] [尺寸]")
        print("示例: python image_to_image.py input.png '添加彩虹到天空' output.png high hd 1024x1024")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    input_fidelity = sys.argv[4] if len(sys.argv) > 4 else "high"
    quality = sys.argv[5] if len(sys.argv) > 5 else "hd"
    size = sys.argv[6] if len(sys.argv) > 6 else "1024x1024"

    image_to_image(image_path, prompt, output_path, input_fidelity, quality, size)
