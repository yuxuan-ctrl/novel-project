#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Gemini 图生图 API 生成场景图像
基于角色基础形象 + 场景描述生成最终图像，保证角色一致性
"""

import requests
import base64
import os
import re
from PIL import Image
from io import BytesIO

API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1beta"

# 角色名称到文件名的映射
CHARACTER_MAPPING = {
    "猪八戒": "zhubajie.png",
    "孙悟空": "sunwukong_memory.png",
    "斗战胜佛": "douzhanshengfo.png"
}

def edit_image(character_image_path, scene_prompt, output_path):
    """使用 Gemini 图生图 API 生成场景图像"""
    url = f"{BASE_URL}/models/gemini-2.5-flash-image:generateContent"

    # 读取并编码角色形象图
    with open(character_image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # 确定 MIME 类型
    mime_type = "image/png"
    if character_image_path.lower().endswith(('.jpg', '.jpeg')):
        mime_type = "image/jpeg"
    elif character_image_path.lower().endswith('.webp'):
        mime_type = "image/webp"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # 构建完整的图生图提示词
    full_prompt = f"""
请基于提供的角色形象，生成以下场景的图像。
务必保持角色的外貌、服装、气质与参考图像完全一致。

场景描述：
{scene_prompt}

要求：
1. 角色外貌、服装必须与参考图像完全一致
2. 场景环境按照描述生成
3. 保持半写实动漫插画风格
4. 细腻光影层次，丰富质感细节
"""

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    },
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": image_data
                        }
                    }
                ]
            }
        ]
    }

    print(f"正在生成场景图像...")
    print(f"角色参考: {character_image_path}")
    print(f"场景描述: {scene_prompt[:100]}...")

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()

        # 提取并保存编辑后的图像
        for candidate in result.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    image_data = base64.b64decode(part['inlineData']['data'])
                    image = Image.open(BytesIO(image_data))
                    image.save(output_path)
                    print(f"✅ 场景图像已保存: {output_path}")
                    return True

        print("❌ 响应中未找到图像数据")
        return False
    else:
        print(f"❌ API 错误: {response.status_code} - {response.text}")
        return False

def identify_characters_in_scene(scene_text):
    """识别场景中出现的角色"""
    characters = []
    for character_name in CHARACTER_MAPPING.keys():
        if character_name in scene_text:
            characters.append(character_name)
    return characters

def load_scene_prompts(episode_num):
    """从提示词文件加载场景描述"""
    prompt_file = f"image-prompts/Episode-{episode_num:02d}-Natural-Chinese-Prompts.txt"

    if not os.path.exists(prompt_file):
        print(f"❌ 提示词文件不存在: {prompt_file}")
        return []

    with open(prompt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析场景
    scenes = []
    pattern = r'## Scene (\d+) - (Start|End) Frame.*?\*\*完整提示词\*\*：\s*\n(.+?)(?=\n\n---|\n\n##|\Z)'

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        scene_id = match.group(1)
        frame_type = match.group(2)
        prompt = match.group(3).strip()

        # 识别角色
        characters = identify_characters_in_scene(prompt)

        scenes.append({
            'scene_id': scene_id,
            'frame_type': frame_type,
            'prompt': prompt,
            'characters': characters
        })

    return scenes

def generate_episode_scenes(episode_num):
    """批量生成一个Episode的所有场景"""
    print("=" * 70)
    print(f"开始生成 Episode {episode_num:02d} 场景图像")
    print("=" * 70)
    print()

    # 加载场景提示词
    scenes = load_scene_prompts(episode_num)

    if not scenes:
        print(f"❌ Episode {episode_num:02d} 没有找到场景")
        return

    # 创建输出目录
    output_dir = f"generated_images_gemini/Episode-{episode_num:02d}"
    os.makedirs(output_dir, exist_ok=True)

    success_count = 0

    for i, scene in enumerate(scenes, 1):
        scene_id = scene['scene_id']
        frame_type = scene['frame_type']
        prompt = scene['prompt']
        characters = scene['characters']

        shot_num = i
        print(f"\n[Shot {shot_num:03d}] Scene {scene_id} - {frame_type}")
        print("-" * 70)

        # 确定使用哪个角色形象（如果有多个角色，使用第一个主要角色）
        if not characters:
            print("⚠️  场景中未识别到角色，跳过")
            continue

        character_name = characters[0]
        character_filename = CHARACTER_MAPPING[character_name]
        character_image_path = os.path.join("character_images", character_filename)

        # 检查角色形象是否存在
        if not os.path.exists(character_image_path):
            print(f"❌ 角色形象不存在: {character_image_path}")
            print(f"   请先运行: python generate_character_base.py")
            continue

        # 生成输出文件名
        output_filename = f"Episode-{episode_num:02d}-Shot-{shot_num:03d}-Generated.png"
        output_path = os.path.join(output_dir, output_filename)

        # 生成图像
        if edit_image(character_image_path, prompt, output_path):
            success_count += 1
        else:
            print(f"❌ 生成失败: Shot {shot_num:03d}")

    print()
    print("=" * 70)
    print(f"✅ Episode {episode_num:02d} 场景图像生成完成！")
    print(f"成功: {success_count} / {len(scenes)}")
    print(f"保存目录: {output_dir}/")
    print("=" * 70)

def generate_single_shot(episode_num, shot_num, character_name=None):
    """生成单个镜头"""
    scenes = load_scene_prompts(episode_num)

    if shot_num < 1 or shot_num > len(scenes):
        print(f"❌ Shot {shot_num} 不存在（Episode {episode_num:02d} 共 {len(scenes)} 个镜头）")
        return

    scene = scenes[shot_num - 1]
    scene_id = scene['scene_id']
    frame_type = scene['frame_type']
    prompt = scene['prompt']
    characters = scene['characters']

    print(f"生成 Episode {episode_num:02d} - Shot {shot_num:03d}")
    print(f"Scene {scene_id} - {frame_type}")
    print("-" * 70)

    # 确定角色
    if character_name:
        if character_name not in CHARACTER_MAPPING:
            print(f"❌ 未知角色: {character_name}")
            return
    else:
        if not characters:
            print("❌ 场景中未识别到角色，请手动指定")
            return
        character_name = characters[0]

    character_filename = CHARACTER_MAPPING[character_name]
    character_image_path = os.path.join("character_images", character_filename)

    if not os.path.exists(character_image_path):
        print(f"❌ 角色形象不存在: {character_image_path}")
        return

    # 输出路径
    output_dir = f"generated_images_gemini/Episode-{episode_num:02d}"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"Episode-{episode_num:02d}-Shot-{shot_num:03d}-Generated.png"
    output_path = os.path.join(output_dir, output_filename)

    # 生成图像
    if edit_image(character_image_path, prompt, output_path):
        print(f"✅ Shot {shot_num:03d} 生成成功！")
    else:
        print(f"❌ Shot {shot_num:03d} 生成失败")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  批量生成Episode: python generate_with_gemini.py --episode <集数>")
        print("  生成单个镜头:   python generate_with_gemini.py --episode <集数> --shot <镜头号> [--character <角色名>]")
        sys.exit(1)

    episode_num = None
    shot_num = None
    character_name = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--episode" and i + 1 < len(sys.argv):
            episode_num = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--shot" and i + 1 < len(sys.argv):
            shot_num = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--character" and i + 1 < len(sys.argv):
            character_name = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if episode_num is None:
        print("❌ 必须指定 --episode 参数")
        sys.exit(1)

    if shot_num:
        # 生成单个镜头
        generate_single_shot(episode_num, shot_num, character_name)
    else:
        # 批量生成Episode
        generate_episode_scenes(episode_num)
