import requests
import json
import base64
from PIL import Image
from io import BytesIO
import os
import time

# API配置
API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1"

def generate_scene_only(prompt, size="1920x1920"):
    """生成纯场景（没有人物）"""
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

    print("步骤1：生成纯场景...")
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and len(result['data']) > 0:
            scene_url = result['data'][0]['url']
            print(f"场景生成成功: {scene_url}")
            return scene_url
    else:
        print(f"错误: {response.status_code} - {response.text}")
    return None

def merge_character_scene(character_img, scene_img, prompt, size="1920x1920", fidelity="high"):
    """将人物与场景融合（增强版，支持面容保真度控制）"""
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 读取人物图片
    with open(character_img, "rb") as f:
        char_data = base64.b64encode(f.read()).decode('utf-8')

    data = {
        "prompt": prompt,
        "image": [
            f"data:image/png;base64,{char_data}",
            scene_img
        ],
        "model": "doubao-seedream-4-5-251128",
        "sequential_image_generation": "disabled",
        "size": size,
        "response_format": "url",
        "watermark": False,
        "input_fidelity": fidelity,
        "quality": "hd"
    }

    print("步骤2：融合人物与场景...")
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and len(result['data']) > 0:
            final_url = result['data'][0]['url']
            print(f"融合成功: {final_url}")
            return final_url
    else:
        print(f"错误: {response.status_code} - {response.text}")
    return None

def save_image_from_url(url, filename):
    """从URL保存图片"""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"图片已保存: {filename}")
        return filename
    else:
        print(f"下载失败: {response.status_code}")
        return None

if __name__ == "__main__":
    # 测试两步生成流程
    # 步骤1：生成场景
    scene_prompt = "中国动画电影风格，天庭斩仙台全景，黑色石质平台悬浮在云海中，十八根盘龙玉柱环绕，金色符文在平台边缘闪烁，天空阴沉云层厚重，远处是天宫建筑群，电影级光照，手绘质感，宏大场景，没有人"

    scene_url = generate_scene_only(scene_prompt)

    if scene_url:
        # 保存场景图
        scene_path = "Scene-Platform.png"
        save_image_from_url(scene_url, scene_path)

        # 步骤2：融合人物
        merge_prompt = "将图1的人物（林玄）放入图2的场景中，跪在斩仙台中央，被铁链束缚，保持人物面容特征不变，融入场景氛围，中国动画电影风格"

        final_url = merge_character_scene(
            character_img="character_images/linxuan.png",
            scene_img=scene_url,
            prompt=merge_prompt
        )

        if final_url:
            save_image_from_url(final_url, "Episode-01-Shot-001-Final.png")