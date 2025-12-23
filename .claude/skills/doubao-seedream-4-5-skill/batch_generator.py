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

def generate_scene_sequence(character_images, scene_description, num_scenes=5):
    """
    使用豆包API生成一组相关场景（图生组图）

    Args:
        character_images: 角色参考图片列表
        scene_description: 场景描述，可以包含多个变化
        num_scenes: 需要生成的场景数量
    """
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 准备图片数据
    image_list = []
    for img_path in character_images:
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            image_list.append(f"data:image/png;base64,{img_data}")
        else:
            image_list.append(img_path)

    data = {
        "prompt": f"生成{num_scenes}张图片：{scene_description}。保持人物特征一致，展现不同的情绪和动作。",
        "image": image_list,
        "model": "doubao-seedream-4-0-250828",
        "sequential_image_generation": "auto",
        "sequential_image_generation_options": {
            "max_images": num_scenes
        },
        "size": "1024x1024",
        "response_format": "url",
        "watermark": False
    }

    print(f"开始生成{num_scenes}张场景图...")
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"成功生成{len(result['data'])}张图片")

        urls = []
        for i, img_data in enumerate(result['data']):
            if 'url' in img_data:
                urls.append(img_data['url'])
                print(f"场景{i+1}: {img_data['url']}")

        return urls
    else:
        print(f"错误: {response.status_code} - {response.text}")
        return None

def enhance_character_with_scene(character_img, scene_img, scene_description):
    """
    将角色与场景融合，增强细节

    Args:
        character_img: 角色图片路径
        scene_img: 场景图片URL
        scene_description: 最终场景描述
    """
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 读取角色图片
    with open(character_img, "rb") as f:
        char_data = base64.b64encode(f.read()).decode('utf-8')

    data = {
        "prompt": f"图1的人物与图2的场景融合：{scene_description}。保持图1人物的面容和服装特征，融入图2的环境氛围。中国动画电影风格，手绘质感，电影级光照。",
        "image": [
            f"data:image/png;base64,{char_data}",
            scene_img
        ],
        "model": "doubao-seedream-4-0-250828",
        "sequential_image_generation": "disabled",
        "size": "1024x1024",
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

# 使用示例：生成斩仙台场景序列
if __name__ == "__main__":
    # 角色参考图片
    character_images = [
        "character_images/linxuan.png",
        "character_images/huijue.png"
    ]

    # 场景描述
    scene_description = """
    林玄在斩仙台上：
    1. 林玄跪在台上，铁链束缚，表情痛苦但坚毅
    2. 林玄抬头怒视天庭众神，嘴角带血
    3. 林玄喷血反击，动态瞬间
    4. 林玄与慧觉对峙，紧张气氛
    5. 天庭众神震惊的反应
    """

    # 生成场景序列
    scene_urls = generate_scene_sequence(
        character_images=character_images,
        scene_description=scene_description,
        num_scenes=5
    )

    # 如果需要进一步融合增强
    if scene_urls:
        for i, scene_url in enumerate(scene_urls):
            enhanced_url = enhance_character_with_scene(
                character_img="character_images/linxuan.png",
                scene_img=scene_url,
                scene_description=f"斩仙台场景{i+1}"
            )
            if enhanced_url:
                print(f"增强后的场景{i+1}: {enhanced_url}")