#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成角色基础形象 - 使用 Gemini 2.5 Flash Image API
第一步：为每个主要角色生成标准形象图，用于后续场景生成
"""

import requests
import base64
import os
from PIL import Image
from io import BytesIO

API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1beta"

# 角色模板定义
CHARACTER_TEMPLATES = {
    "猪八戒": """
半写实动漫插画风格，中景肖像视角，纯白色背景，
中年男子角色设计，猪八戒净坛使者形象，
精致立体五官，成熟面容，真实比例，
大耳朵特征优雅不夸张，小而深邃有神眼睛，
圆润憨厚面容，朴实气质，匀称自然体型，
褐色僧袍华丽，宽大袈裟，腰系布带，
九齿钉耙武器在手，威武霸气，
柔和自然光线照亮面部，细腻光影层次，
中国古风玄幻半写实风格，轻小说封面质感，
丰富服饰细节，华丽纹理质感，成熟角色设计，
憨厚朴实表情，豪迈洒脱姿态
""",

    "孙悟空": """
半写实动漫插画风格，中景肖像视角，纯白色背景，
英俊精悍成年男子角色，齐天大圣孙悟空形象，
精致立体五官，深邃有神眼睛，锐利眼神，
尖嘴特征柔化优雅，优雅面部轮廓，
健康自然肤色，细腻皮肤质感，
金色锁子甲闪耀，华丽盔甲细节，
红色披风飘扬，战斗装束威武，
金箍棒武器在手，神通广大气场，
桀骜不驯姿态，野性十足表情，
柔和自然光线，细腻光影层次，
中国古风玄幻半写实风格，轻小说封面质感，
成熟角色设计，英雄气概
""",

    "斗战胜佛": """
半写实动漫插画风格，中景肖像视角，纯白色背景，
俊美僧人角色设计，斗战胜佛形象，
精致立体五官，成熟面容，真实比例，
空洞但清澈的眼神，失去灵性的目光，
尖嘴特征柔化优雅，优雅面部线条，
健康自然肤色，细腻皮肤质感，
金色袈裟华贵闪耀，佛光笼罩全身，
宝相庄严装束，华丽佛教服饰，
双手合十姿势僵硬机械，木然表情，
站姿笔直僵硬如雕塑，失去生气，
柔和佛光照亮面部，细腻光影层次，
中国古风佛教半写实风格，轻小说封面质感，
成熟角色设计，木然机械的诡异氛围
"""
}

# 角色文件名映射
CHARACTER_FILENAMES = {
    "猪八戒": "zhubajie.png",
    "孙悟空": "sunwukong_memory.png",
    "斗战胜佛": "douzhanshengfo.png"
}

def generate_image_from_text(prompt, output_path):
    """使用 Gemini API 从文本生成图像"""
    url = f"{BASE_URL}/models/gemini-2.5-flash-image:generateContent"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    print(f"正在生成图像...")
    print(f"提示词: {prompt[:100]}...")

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()

        # 提取并保存生成的图像
        for candidate in result.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    image_data = base64.b64decode(part['inlineData']['data'])
                    image = Image.open(BytesIO(image_data))
                    image.save(output_path)
                    print(f"✅ 图像已保存: {output_path}")
                    return True

        print("❌ 响应中未找到图像数据")
        return False
    else:
        print(f"❌ API 错误: {response.status_code} - {response.text}")
        return False

def generate_all_characters():
    """生成所有主要角色的基础形象"""
    # 创建角色图像目录
    output_dir = "character_images"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("开始生成角色基础形象")
    print("=" * 70)
    print()

    success_count = 0

    for character_name, prompt in CHARACTER_TEMPLATES.items():
        print(f"\n[{character_name}]")
        print("-" * 70)

        filename = CHARACTER_FILENAMES[character_name]
        output_path = os.path.join(output_dir, filename)

        # 检查是否已存在
        if os.path.exists(output_path):
            print(f"⚠️  角色形象已存在，跳过: {output_path}")
            continue

        # 生成图像
        if generate_image_from_text(prompt, output_path):
            success_count += 1
        else:
            print(f"❌ 生成失败: {character_name}")

    print()
    print("=" * 70)
    print(f"✅ 角色基础形象生成完成！")
    print(f"成功: {success_count} / {len(CHARACTER_TEMPLATES)}")
    print(f"保存目录: {output_dir}/")
    print("=" * 70)

def generate_single_character(character_name):
    """生成单个角色的基础形象"""
    if character_name not in CHARACTER_TEMPLATES:
        print(f"❌ 未知角色: {character_name}")
        print(f"可用角色: {', '.join(CHARACTER_TEMPLATES.keys())}")
        return

    output_dir = "character_images"
    os.makedirs(output_dir, exist_ok=True)

    prompt = CHARACTER_TEMPLATES[character_name]
    filename = CHARACTER_FILENAMES[character_name]
    output_path = os.path.join(output_dir, filename)

    print(f"正在生成角色: {character_name}")

    if generate_image_from_text(prompt, output_path):
        print(f"✅ 角色 {character_name} 生成成功！")
    else:
        print(f"❌ 角色 {character_name} 生成失败")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--character":
        # 生成单个角色
        if len(sys.argv) > 2:
            generate_single_character(sys.argv[2])
        else:
            print("用法: python generate_character_base.py --character <角色名>")
            print(f"可用角色: {', '.join(CHARACTER_TEMPLATES.keys())}")
    else:
        # 生成所有角色
        generate_all_characters()
