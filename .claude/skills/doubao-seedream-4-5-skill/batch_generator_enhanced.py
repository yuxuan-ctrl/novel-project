#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
即梦4.5增强版批量图像生成器
使用验证成功的两步生成法，确保人物面容保持
"""

import requests
import json
import base64
import os
import time
from typing import List, Dict, Tuple

# API配置
API_KEY = "ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A"
BASE_URL = "https://model-api.skyengine.com.cn/v1"
MODEL = "doubao-seedream-4-5-251128"

def generate_scene_only(prompt: str, size: str = "1920x1920") -> str:
    """生成纯场景（第一步）"""
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "prompt": prompt,
        "model": MODEL,
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

def merge_character_scene(character_img: str, scene_img: str, prompt: str,
                          size: str = "1920x1920", fidelity: str = "high") -> str:
    """融合人物与场景（第二步）"""
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
        "model": MODEL,
        "sequential_image_generation": "disabled",
        "size": size,
        "response_format": "url",
        "watermark": False,
        "input_fidelity": fidelity,
        "quality": "hd"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if 'data' in result and len(result['data']) > 0:
            return result['data'][0]['url']
    return None

def save_image_from_url(url: str, filename: str) -> bool:
    """从URL保存图片"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"保存失败: {e}")
    return False

def generate_enhanced_prompt(shot_info: Dict) -> Tuple[str, str]:
    """生成增强版提示词对（场景+融合）"""

    # 场景提示词（第一步）
    scene_prompt = f"""中国动画电影风格，{shot_info.get('location', '斩仙台')}{shot_info.get('shot_type', '全景')}
{shot_info.get('scene_desc', '')}
{shot_info.get('atmosphere', '')}的氛围
电影级光照，手绘质感
没有人物，只有场景
画幅 1920x1920"""

    # 融合提示词（第二步）
    merge_prompt = f"""将图1的人物{shot_info.get('character_name', '林玄')}与图2的场景融合：

【场景地点】{shot_info.get('location', '天庭斩仙台')}
【时间】{shot_info.get('time', '白日')}
【光线】{shot_info.get('lighting', '阴沉压抑')}

【人物布局】
{shot_info.get('position_desc', '人物位于画面中心，保持原有姿态')}

【光影效果】
{shot_info.get('lighting_effects', '光线自然包裹人物，与场景光照一致')}

【氛围】{shot_info.get('atmosphere', '肃穆压抑')}

【面容保持要求】
绝对保持{shot_info.get('character_name', '林玄')}的面容特征：
- 包括眼睛、鼻子、嘴巴、发型必须100%保持不变
- 面容细节清晰可见，不得模糊或变形
- 表情{shot_info.get('expression', '倔强痛苦')}

【风格要求】
• 中国动画电影风格（哪吒之魔童降世、姜子牙风格）
• 电影级光照，手绘质感，高清渲染
• 画幅 1920x1920"""

    return scene_prompt, merge_prompt

def generate_shots_batch(shots_config: List[Dict], output_dir: str,
                        character_img: str = "character_images/linxuan.png") -> None:
    """批量生成镜头图像"""

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("开始批量生成（增强版两步法）")
    print("=" * 60)

    for i, shot in enumerate(shots_config, 1):
        shot_num = shot.get('shot', i)
        print(f"\n处理 Shot {shot_num:03d}/{len(shots_config)}")
        print("-" * 40)

        # 生成提示词
        scene_prompt, merge_prompt = generate_enhanced_prompt(shot)

        # 第一步：生成场景
        print("步骤1：生成纯场景...")
        scene_url = generate_scene_only(scene_prompt)

        if scene_url:
            # 保存场景图
            scene_path = os.path.join(output_dir, f"Shot-{shot_num:03d}-Scene.png")
            if save_image_from_url(scene_url, scene_path):
                print(f"  场景已保存: {scene_path}")

                # 第二步：融合人物
                print("步骤2：融合人物与场景...")
                final_url = merge_character_scene(
                    character_img=character_img,
                    scene_img=scene_url,
                    prompt=merge_prompt,
                    fidelity="high"
                )

                if final_url:
                    # 保存最终图
                    final_path = os.path.join(output_dir, f"Shot-{shot_num:03d}-Final.png")
                    if save_image_from_url(final_url, final_path):
                        print(f"  完成！最终图: {final_path}")
                    else:
                        print(f"  保存失败")
                else:
                    print(f"  融合失败")
            else:
                print(f"  场景保存失败")
        else:
            print(f"  场景生成失败")

        # 短暂延迟避免过快请求
        time.sleep(1)

    print("\n" + "=" * 60)
    print("批量生成完成！")
    print(f"输出目录: {output_dir}")

# 示例镜头配置
def get_sample_shots_config() -> List[Dict]:
    """获取示例镜头配置"""
    return [
        {
            "shot": 1,
            "location": "天庭斩仙台",
            "shot_type": "全景",
            "scene_desc": "黑色石质平台悬浮在翻腾的云海中，十八根盘龙玉柱环绕，金色符文闪烁",
            "character_name": "林玄",
            "position_desc": "跪在斩仙台中央偏下，身形前倾，被铁链束缚四肢",
            "lighting": "阴沉压抑，光线从云层缝隙中透出",
            "lighting_effects": "铁链反射冷光，俯视角度形成阴影",
            "expression": "倔强痛苦",
            "atmosphere": "肃穆压抑"
        },
        {
            "shot": 2,
            "location": "斩仙台",
            "shot_type": "中景特写",
            "scene_desc": "黑色石质平台表面，有裂纹和岁月痕迹，盘龙玉柱局部",
            "character_name": "林玄",
            "position_desc": "画面中心，跪姿抬头向上，锁链紧缚手腕",
            "lighting": "从右侧斜射，形成明暗对比",
            "lighting_effects": "右上方光线在面部形成强烈明暗对比，血迹呈现暗红色",
            "expression": "愤怒不屈",
            "atmosphere": "紧张对峙"
        }
        # 可以继续添加更多镜头...
    ]

if __name__ == "__main__":
    # 示例使用
    shots_config = get_sample_shots_config()
    output_dir = "outputs/enhanced_test"

    generate_shots_batch(shots_config, output_dir)