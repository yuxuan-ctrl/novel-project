#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包即梦 Seedream 4.0 - 两步生成流程
步骤1：生成纯场景（没有人物）
步骤2：将人物与场景融合
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import base64
import requests
from datetime import datetime

API_URL_GEN = "https://aigc-backend.skyengine.com.cn/eliza/v1/images/generations"
API_URL_EDIT = "https://aigc-backend.skyengine.com.cn/eliza/v1/images/edits"
API_KEY = "promptt-dev:promptt-dev"

def generate_image(prompt, output_path=None, size="1024x1024", num_images=1):
    """文本生成图片"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": prompt,
        "sequential_image_generation": "auto",
        "sequential_image_generation_options": {
            "max_images": num_images
        },
        "size": size
    }

    print(f"正在生成图片...")
    print(f"提示词: {prompt}")
    print(f"尺寸: {size}")

    response = requests.post(API_URL_GEN, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()

        if "data" in result:
            saved_files = []
            for idx, item in enumerate(result["data"], 1):
                if "url" in item:
                    image_url = item["url"]
                    img_response = requests.get(image_url)

                    if img_response.status_code == 200:
                        if output_path:
                            if num_images > 1:
                                base, ext = os.path.splitext(output_path)
                                file_path = f"{base}_{idx}{ext}"
                            else:
                                file_path = output_path
                        else:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            file_path = f"seedream_{timestamp}_{idx}.png"

                        with open(file_path, 'wb') as f:
                            f.write(img_response.content)

                        saved_files.append(file_path)
                        print(f"✅ 图片 {idx} 已保存: {file_path}")

                elif "b64_json" in item:
                    image_data = base64.b64decode(item["b64_json"])

                    if output_path:
                        if num_images > 1:
                            base, ext = os.path.splitext(output_path)
                            file_path = f"{base}_{idx}{ext}"
                        else:
                            file_path = output_path
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_path = f"seedream_{timestamp}_{idx}.png"

                    with open(file_path, 'wb') as f:
                        f.write(image_data)

                    saved_files.append(file_path)
                    print(f"✅ 图片 {idx} 已保存: {file_path}")

            return saved_files
        else:
            print(f"❌ 响应中未找到图片数据")
            return None
    else:
        print(f"❌ API错误: {response.status_code}")
        return None

def image_to_image(image_path, prompt, output_path=None, input_fidelity="high", quality="hd", size="1024x1024"):
    """图片编辑（图生图）"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    if image_path.startswith("http://") or image_path.startswith("https://"):
        image_input = image_path
    else:
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

    response = requests.post(API_URL_EDIT, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()

        if "data" in result and len(result["data"]) > 0:
            item = result["data"][0]

            if "url" in item:
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
                image_data = base64.b64decode(item["b64_json"])

                if not output_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = f"seedream_edited_{timestamp}.png"

                with open(output_path, 'wb') as f:
                    f.write(image_data)

                print(f"✅ 编辑后图片已保存: {output_path}")
                return output_path

        print(f"❌ 响应中未找到图片数据")
        return None
    else:
        print(f"❌ API错误: {response.status_code}")
        return None

def two_step_generation(scene_prompt, character_path, output_dir, scene_size="1024x1024", final_size="1024x1024"):
    """两步生成流程"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("【步骤1】生成纯场景")
    print("=" * 60)

    # 步骤1：生成纯场景
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    scene_path = os.path.join(output_dir, f"step1_scene_{timestamp}.png")

    # 强调场景描述，不包含人物
    enhanced_scene_prompt = f"{scene_prompt}, epic environment, detailed background, atmospheric lighting, no characters, empty scene, wide angle shot, cinematic quality, anime style"

    print(f"场景提示词: {enhanced_scene_prompt}")
    scene_files = generate_image(enhanced_scene_prompt, scene_path, scene_size, 1)

    if not scene_files:
        print("❌ 场景生成失败")
        return None, None

    scene_file = scene_files[0]
    print(f"✅ 场景生成成功: {scene_file}")

    print("\n" + "=" * 60)
    print("【步骤2】人物与场景融合")
    print("=" * 60)

    # 步骤2：将人物与场景融合
    final_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = os.path.join(output_dir, f"step2_final_{final_timestamp}.png")

    # 融合提示词
    fusion_prompt = "将人物自然地融入到场景中，保持人物特征，光影匹配，风格统一，高质量合成，动漫风格"

    print(f"人物图片: {character_path}")
    print(f"融合提示词: {fusion_prompt}")

    # 使用image_to_image进行融合
    final_file = image_to_image(
        scene_file,
        fusion_prompt,
        final_path,
        input_fidelity="medium",  # 中等保真度，允许更多变化
        quality="hd",
        size=final_size
    )

    if final_file:
        print(f"✅ 最终图片生成成功: {final_file}")
        return scene_file, final_file
    else:
        print("❌ 人物融合失败")
        return scene_file, None

def test_zhanxiantai():
    """测试斩仙台场景生成"""
    print("开始测试斩仙台两步生成流程...")

    # 斩仙台场景描述（不包含人物）
    scene_prompt = "斩仙台，古代修仙者的处刑台，由巨大的青石铺成，石面刻满符文，四周云雾缭绕，远山如黛，石台边缘有断裂的锁链，血迹斑斑，气氛肃杀，仙侠风格"

    # 人物图片路径（使用绝对路径）
    character_path = "D:/AI/novel-claude-project/character_images/linxuan.png"

    # 输出目录
    output_dir = "D:/AI/novel-claude-project/outputs/run_20250213_153000_anime/05_generated_images/Episode-01"

    # 检查人物图片是否存在
    if not os.path.exists(character_path):
        print(f"❌ 人物图片不存在: {character_path}")
        return

    # 执行两步生成
    scene_file, final_file = two_step_generation(
        scene_prompt=scene_prompt,
        character_path=character_path,
        output_dir=output_dir,
        scene_size="1024x1024",
        final_size="1024x1024"
    )

    # 输出结果
    print("\n" + "=" * 60)
    print("生成结果总结")
    print("=" * 60)
    print(f"场景图片: {scene_file}")
    print(f"最终图片: {final_file}")

    # 质量评估提示
    print("\n质量评估要点：")
    print("1. 场景图质量：检查场景细节、氛围感、构图")
    print("2. 人物保真度：检查林玄的特征是否保持")
    print("3. 融合效果：检查人物与场景的光影匹配")
    print("4. 风格统一：确认整体动漫风格一致")

if __name__ == "__main__":
    # 如果有命令行参数，使用参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_zhanxiantai()
        else:
            print("用法: python two_step_generator.py test")
            print("      测试斩仙台两步生成流程")
    else:
        # 默认执行测试
        test_zhanxiantai()