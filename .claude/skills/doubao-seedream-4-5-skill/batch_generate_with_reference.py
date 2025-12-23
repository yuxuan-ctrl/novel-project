#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成镜头 - 使用参考图（真正实现两步生成）
"""

import requests
import json
import base64
import os
import time

# API配置
API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1"

# 编码图片为base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 第一步：生成场景
def generate_scene(prompt, size="2560x1440"):
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "prompt": prompt + " 空镜头，无人物，只有场景和建筑。",
        "model": "doubao-seedream-4-5-251128",
        "size": size,
        "response_format": "url",
        "watermark": False
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and len(result['data']) > 0:
            return result['data'][0]['url']
    return None

# 第二步：使用参考图生成最终图像
def generate_with_reference(prompt, style_ref_path=None, character_ref_path=None, size="2560x1440"):
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 构建请求
    data = {
        "prompt": prompt,
        "model": "doubao-seedream-4-5-251128",
        "size": size,
        "response_format": "url",
        "watermark": False
    }

    # 添加参考图
    if style_ref_path and os.path.exists(style_ref_path):
        style_base64 = encode_image(style_ref_path)
        data["ref_image"] = style_base64
        data["ref_strength"] = 0.8  # 参考图强度

    # 如果有人物参考图，将其也加入提示词
    if character_ref_path and os.path.exists(character_ref_path):
        # 注意：seedream 4.5可能只支持一张参考图
        # 这里我们优先使用人物参考图
        character_base64 = encode_image(character_ref_path)
        data["ref_image"] = character_base64
        data["ref_strength"] = 0.7

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and len(result['data']) > 0:
            return result['data'][0]['url']
    else:
        print(f"API错误: {response.status_code} - {response.text}")
    return None

# 下载图片
def download_image(url, filepath):
    response = requests.get(url)
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"已保存: {filepath}")

def main():
    # 输出目录
    output_dir = "outputs/run_20250213_163000_anime/05_generated_images"
    os.makedirs(output_dir, exist_ok=True)

    # 风格参考图
    style_ref = "character_images/风格图.png"
    if not os.path.exists(style_ref):
        print(f"风格图不存在: {style_ref}")
        return

    # 角色参考图
    character_refs = {
        "林玄": "character_images/linxuan.png"
    }

    # 简化的提示词（前3个镜头作为测试）
    shots = [
        {
            "num": "003",
            "has_character": True,
            "character": "林玄",
            "prompt": "斩仙台中央，林玄跪在地上，身穿灰色囚服，神情坚毅。阴天的自然光，光线惨淡。林玄虽然身陷困境，但眼神中透出不屈的意志。中景镜头，展现人物的坚韧气质。"
        },
        {
            "num": "004",
            "has_character": True,
            "character": "林玄",
            "prompt": "斩仙台全景，林玄跪在中央，周围是肃立的天兵。从高处俯视，展现整个审判场景的庄严和压迫感。林玄虽然渺小，但身影挺拔。全景镜头，氛围肃穆。"
        },
        {
            "num": "005",
            "has_character": True,
            "character": "林玄",
            "prompt": "林玄的特写镜头，他抬头仰望着天空，脸上带着复杂的表情。侧光勾勒出他的轮廓，眼神坚定而有神。特写镜头，捕捉人物的情感变化。"
        }
    ]

    print("开始生成镜头（使用参考图）...")

    for shot in shots:
        print(f"\n生成镜头 {shot['num']}...")

        output_path = os.path.join(output_dir, f"Episode-01-Shot-{shot['num']}-Anime-Ref.png")

        if shot["has_character"]:
            # 有人物：使用参考图
            character_ref = character_refs.get(shot["character"])
            if character_ref and os.path.exists(character_ref):
                print(f"使用参考图: {character_ref}")
                url = generate_with_reference(
                    prompt=shot["prompt"],
                    style_ref_path=style_ref,
                    character_ref_path=character_ref
                )
            else:
                print(f"警告：未找到角色参考图 {character_ref}")
                url = generate_scene(shot["prompt"])
        else:
            # 无人物：直接生成场景
            url = generate_scene(shot["prompt"])

        if url:
            download_image(url, output_path)
        else:
            print(f"镜头 {shot['num']} 生成失败")

        time.sleep(3)  # 避免请求过快

    print("\n生成完成！")

if __name__ == "__main__":
    main()