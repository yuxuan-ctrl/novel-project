#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试seedream 4.5的各种图生图API参数组合
"""

import requests
import json
import base64
import os

# API配置
API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1"

def encode_image(image_path):
    """将图片编码为base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_method_1():
    """方法1：使用input_image参数"""
    print("\n=== 测试方法1：input_image ===")

    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 编码人物图片
    char_b64 = encode_image("character_images/linxuan.png")

    data = {
        "prompt": "将人物放入斩仙台场景，跪在平台中央，身穿囚服，神情坚毅。中国动画电影风格，电影级渲染。",
        "model": "doubao-seedream-4-5-251128",
        "input_image": f"data:image/png;base64,{char_b64}",
        "size": "2560x1440",
        "response_format": "url",
        "watermark": False,
        "strength": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")

def test_method_2():
    """方法2：使用image参数（数组）"""
    print("\n=== 测试方法2：image数组 ===")

    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 编码人物图片和风格图片
    char_b64 = encode_image("character_images/linxuan.png")
    style_b64 = encode_image("character_images/风格图.png")

    data = {
        "prompt": "将人物放入斩仙台场景，跪在平台中央，身穿囚服，神情坚毅。使用风格图的国风动画风格。",
        "model": "doubao-seedream-4-5-251128",
        "image": [
            f"data:image/png;base64,{char_b64}",
            f"data:image/png;base64,{style_b64}"
        ],
        "size": "2560x1440",
        "response_format": "url",
        "watermark": False
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")

def test_method_3():
    """方法3：使用reference_image参数"""
    print("\n=== 测试方法3：reference_image ===")

    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 编码人物图片
    char_b64 = encode_image("character_images/linxuan.png")

    data = {
        "prompt": "林玄跪在斩仙台中央，身穿囚服，神情坚毅。阴天的斩仙台，光线惨淡，气氛庄严肃穆。保持人物的面容特征不变。",
        "model": "doubao-seedream-4-5-251128",
        "reference_image": f"data:image/png;base64,{char_b64}",
        "size": "2560x1440",
        "response_format": "url",
        "watermark": False,
        "ref_strength": 0.8
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")

def test_method_4():
    """方法4：多图片输入"""
    print("\n=== 测试方法4：多图片输入 ===")

    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 编码人物图片和风格图片
    char_b64 = encode_image("character_images/linxuan.png")
    style_b64 = encode_image("character_images/风格图.png")

    data = {
        "prompt": "林玄在斩仙台上，保持人物形象，使用风格图的美术风格。",
        "model": "doubao-seedream-4-5-251128",
        "input_images": [
            {"image": f"data:image/png;base64,{char_b64}", "type": "character"},
            {"image": f"data:image/png;base64,{style_b64}", "type": "style"}
        ],
        "size": "2560x1440",
        "response_format": "url",
        "watermark": False
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")

def main():
    """运行所有测试"""
    print("开始测试seedream 4.5的图生图API...")

    # 检查文件是否存在
    if not os.path.exists("character_images/linxuan.png"):
        print("错误：找不到 linxuan.png")
        return

    if not os.path.exists("character_images/风格图.png"):
        print("错误：找不到 风格图.png")
        return

    # 逐一测试各种方法
    test_method_1()
    test_method_2()
    test_method_3()
    test_method_4()

    print("\n测试完成！")

if __name__ == "__main__":
    main()