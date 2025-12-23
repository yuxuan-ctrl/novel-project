#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用参考图批量生成镜头 - 最终版
使用正确的seedream 4.5图生图API
"""

import requests
import json
import base64
import os
import time

# API配置
API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1"

def encode_image(image_path):
    """将图片编码为base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_with_reference(prompt, character_img_path, style_img_path=None, size="2560x1440"):
    """
    使用参考图生成图像（方法4：image数组）
    """
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 编码图片
    char_b64 = encode_image(character_img_path)
    images = [f"data:image/png;base64,{char_b64}"]

    # 如果有风格图，加入数组
    if style_img_path and os.path.exists(style_img_path):
        style_b64 = encode_image(style_img_path)
        images.append(f"data:image/png;base64,{style_b64}")

    data = {
        "prompt": prompt,
        "model": "doubao-seedream-4-5-251128",
        "image": images,
        "size": size,
        "response_format": "url",
        "watermark": False
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and len(result['data']) > 0:
            return result['data'][0]['url']
    else:
        print(f"错误: {response.status_code} - {response.text}")
    return None

def generate_scene_only(prompt, size="2560x1440"):
    """生成无人物场景"""
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "prompt": prompt,
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
    else:
        print(f"错误: {response.status_code} - {response.text}")
    return None

def download_image(url, filepath):
    """下载并保存图片"""
    response = requests.get(url)
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"已保存: {filepath}")

# 前几个镜头的详细提示词（使用新的六要素格式）
SHOTS_CONFIG = [
    {
        "num": "003",
        "has_character": True,
        "character": "林玄",
        "prompt": "将人物放入斩仙台场景：林玄跪在台中央，身穿灰色囚服，身体虚弱但眼神坚韧。阴天的自然光，光线惨淡，从上方照下。氛围痛苦、坚韧、不屈。电影级特写镜头，保持人物面容特征与参考图一致。"
    },
    {
        "num": "004",
        "has_character": True,
        "character": "林玄",
        "prompt": "将人物放入斩仙台全景：林玄跪在画面中央，周围是肃立的天兵天将。俯视角度，展现审判的压迫感。仙雾缭绕，云层低垂。氛围肃杀、威严、压迫。电影级全景镜头，人物形象保持与参考图一致。"
    },
    {
        "num": "005",
        "has_character": True,
        "character": "林玄",
        "prompt": "将人物放入斩仙台：林玄跪着抬头，眼神锐利，嘴角挂着嘲讽的笑。侧光突出面部表情，勾勒出坚毅的轮廓。氛围讽刺、愤怒、控诉。电影级特写镜头，保持人物面部特征不变。"
    },
    {
        "num": "006",
        "has_character": False,
        "prompt": "斩仙台众仙区域，天庭仙气缭绕，庄严神圣。众仙佛坐于云台之上，神情严肃。仙气如轻纱般环绕，瑞气千条。氛围庄严、审判、神圣。电影级中景镜头，无人物，只有环境。"
    },
    {
        "num": "007",
        "has_character": True,
        "character": "林玄",
        "prompt": "将人物放入温馨房间：林玄跪在地上，师父站在面前，慈祥地手放在他头顶。温暖的金色阳光从窗户洒入，形成丁达尔效应。氛围温馨而神圣，充满师徒情深。电影级中景镜头，保持人物形象。"
    }
]

def main():
    """主函数"""
    print("开始批量生成镜头（使用参考图）...")

    # 输出目录
    output_dir = "outputs/run_20250213_163000_anime/05_generated_images"
    os.makedirs(output_dir, exist_ok=True)

    # 风格参考图
    style_ref = "character_images/风格图.png"

    # 角色图映射
    character_refs = {
        "林玄": "character_images/linxuan.png",
        "慧觉": "character_images/huijue.png",
        "观音菩萨": "character_images/guanyin_pusa.png",
        "菩提祖师": "character_images/puti_zushi.png"
    }

    for shot in SHOTS_CONFIG:
        print(f"\n生成镜头 {shot['num']}...")

        output_path = os.path.join(output_dir, f"Episode-01-Shot-{shot['num']}-Anime-Ref.png")

        if shot["has_character"]:
            # 有人物：使用参考图生成
            char_ref = character_refs.get(shot["character"])
            if char_ref and os.path.exists(char_ref):
                print(f"使用角色参考图: {char_ref}")
                url = generate_with_reference(
                    prompt=shot["prompt"],
                    character_img_path=char_ref,
                    style_img_path=style_ref
                )
            else:
                print(f"警告：未找到角色参考图 {char_ref}")
                url = generate_scene_only(shot["prompt"])
        else:
            # 无人物：直接生成场景
            print("无人物场景，直接生成")
            url = generate_scene_only(shot["prompt"])

        if url:
            download_image(url, output_path)
        else:
            print(f"镜头 {shot['num']} 生成失败")

        # 避免请求过快
        time.sleep(3)

    print("\n批量生成完成！")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    main()