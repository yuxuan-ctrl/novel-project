#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用正确的seedream 4.5图生图API生成图像
"""

import requests
import json
import base64
import os
import time

# API配置
API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1"

def generate_with_img2img(prompt, input_image_path, size="2560x1440"):
    """
    使用图生图功能
    input_image_path: 输入图片路径
    prompt: 描述如何修改图片
    """
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 读取并编码输入图片
    with open(input_image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    data = {
        "prompt": prompt,
        "model": "doubao-seedream-4-5-251128",
        "input_image": f"data:image/png;base64,{image_data}",
        "size": size,
        "response_format": "url",
        "watermark": False,
        "strength": 0.7  # 控制变化程度
    }

    print(f"使用图生图: {input_image_path}")
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and len(result['data']) > 0:
            return result['data'][0]['url']
    else:
        print(f"错误: {response.status_code} - {response.text}")
    return None

def generate_two_step(shot_num, scene_prompt, character_ref, final_prompt):
    """
    两步生成：
    1. 生成场景
    2. 将人物参考图作为基础，通过图生图融入场景
    """
    output_dir = "outputs/run_20250213_163000_anime/05_generated_images"

    # 第一步：生成场景
    print(f"\n镜头{shot_num} - 步骤1：生成场景")
    scene_url = generate_scene(scene_prompt)

    if scene_url:
        # 下载场景图
        scene_path = f"temp_scene_{shot_num}.png"
        response = requests.get(scene_url)
        with open(scene_path, 'wb') as f:
            f.write(response.content)

        # 第二步：使用人物图作为基础，将场景融入
        print(f"镜头{shot_num} - 步骤2：融合场景")
        final_url = generate_with_img2img(
            prompt=final_prompt,
            input_image_path=character_ref
        )

        if final_url:
            output_path = os.path.join(output_dir, f"Episode-01-Shot-{shot_num}-Anime-2Step.png")
            # 保存最终图像
            response = requests.get(final_url)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"保存成功: {output_path}")

        # 清理临时文件
        if os.path.exists(scene_path):
            os.remove(scene_path)

def generate_scene(prompt, size="2560x1440"):
    """生成纯场景"""
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
    return None

def main():
    # 确保输出目录存在
    os.makedirs("outputs/run_20250213_163000_anime/05_generated_images", exist_ok=True)

    # 测试镜头003
    shot_num = "003"

    # 第一步：场景提示词
    scene_prompt = """中国动画电影风格，斩仙台场景
黑色巨石砌成的平台，悬浮在云海中
阴天，光线惨淡，气氛压抑
没有人物，只有建筑和环境
电影级渲染，高质量"""

    # 第二步：最终提示词（基于人物图）
    final_prompt = """将人物放入斩仙台场景：
人物跪在平台中央，身穿囚服
保持人物的面容特征和发型
环境是阴天的斩仙台，光线惨淡
整体氛围庄严肃穆
中国动画电影风格"""

    # 执行两步生成
    generate_two_step(
        shot_num=shot_num,
        scene_prompt=scene_prompt,
        character_ref="character_images/linxuan.png",
        final_prompt=final_prompt
    )

if __name__ == "__main__":
    main()