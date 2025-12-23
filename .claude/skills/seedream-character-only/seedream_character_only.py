#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包即梦 Seedream 4.5 - 支持多人物三视图生成图像
升级版：可同时使用多张角色参考图，解决角色错乱问题
"""

import requests
import json
import base64
import os
import time
import sys
from pathlib import Path
from typing import List, Optional

class MultiCharacterGenerator:
    def __init__(self, api_key=None):
        """
        初始化多角色生成器

        Args:
            api_key: API密钥
        """
        self.api_key = api_key or "ak-yXx1CsHzL3J6HRakOLPmSAXaDcnPDcAy"
        self.base_url = "https://model-api.skyengine.com.cn/v1"
        self.character_images_dir = "character_images"
        self.scene_images_dir = "scene_images"

    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_with_characters(self, prompt: str, character_img_paths: List[str], scene_img_paths: List[str] = None, size: str = "2k") -> Optional[str]:
        """
        使用多张人物图和场景图生成图像

        Args:
            prompt: 提示词（应包含【图一参考A，图二参考B】【背景参考场景名】格式的绑定声明）
            character_img_paths: 人物图路径列表
            scene_img_paths: 场景图路径列表
            size: 图片尺寸

        Returns:
            生成的图片URL
        """
        url = f"{self.base_url}/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 编码所有图片
        encoded_images = []
        valid_paths = []

        # 先处理角色图
        for img_path in character_img_paths:
            full_path = os.path.join(self.character_images_dir, img_path)
            if os.path.exists(full_path):
                encoded_images.append(f"data:image/png;base64,{self.encode_image(full_path)}")
                valid_paths.append(f"角色:{img_path}")
            else:
                print(f"警告：找不到角色图 {full_path}，已跳过")

        # 再处理场景图
        if scene_img_paths:
            for img_path in scene_img_paths:
                full_path = os.path.join(self.scene_images_dir, img_path)
                if os.path.exists(full_path):
                    encoded_images.append(f"data:image/png;base64,{self.encode_image(full_path)}")
                    valid_paths.append(f"场景:{img_path}")
                else:
                    print(f"警告：找不到场景图 {full_path}，已跳过")

        # 构建请求 - 根据是否有角色图决定是否包含images参数
        data = {
            "prompt": prompt,
            "model": "doubao-seedream-4-5-251128",
            # "model": "doubao-seedream-4.0-250828",
            "size": size,
            "response_format": "url",
            "watermark": False
        }

        # 如果有参考图，添加到请求中并调整提示词
        if encoded_images:
            data["image"] = encoded_images
            if character_img_paths:
                data["prompt"] = prompt + " 严格保持每个角色的面容特征、发型、服装与对应的参考图完全一致，不要混淆角色特征。"
            print(f"  使用参考图: {valid_paths}")
        else:
            print("  无参考图，仅使用提示词生成图像")

        # 发送请求
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                return result['data'][0]['url']
        else:
            print(f"API错误: {response.status_code} - {response.text}")

        return None

    def download_image(self, url: str, output_path: str) -> bool:
        """
        下载并保存图片

        Args:
            url: 图片URL
            output_path: 保存路径

        Returns:
            bool: 是否成功
        """
        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"  已保存: {output_path}")
            return True
        else:
            print(f"  下载失败: {response.status_code}")
            return False

    def load_json_config(self, json_file: str) -> dict:
        """
        加载JSON配置文件（新格式）

        Args:
            json_file: JSON文件路径

        Returns:
            配置字典
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 兼容两种格式：
        # 格式1: {"shots": [...]}
        # 格式2: [...] (直接是数组)
        if 'shots' in data:
            return data
        else:
            # 如果是数组格式，包装成格式1
            return {"shots": data}

    def generate_from_json(self, json_file: str, output_dir: str):
        """
        从JSON配置生成图像（支持多角色）

        Args:
            json_file: JSON配置文件路径
            output_dir: 输出目录
        """
        print("=" * 60)
        print("Seedream Multi-Character Generator v2.0")
        print("支持多角色参考图，解决角色错乱问题")
        print("=" * 60)

        # 加载配置
        config = self.load_json_config(json_file)
        
        # 验证配置格式
        if 'shots' not in config:
            print("错误：JSON格式不正确，缺少'shots'字段")
            return

        all_shots = config['shots']
        character_shots = [shot for shot in all_shots if shot['has_character']]

        scene_shots = [shot for shot in all_shots if not shot['has_character']]
        print(f"\n共加载 {len(all_shots)} 个镜头")
        print(f"其中 {len(character_shots)} 个镜头包含角色")
        print(f"其中 {len(scene_shots)} 个镜头为纯场景")
        print(f"输出目录: {output_dir}\n")

        # 处理每个镜头
        success_count = 0

        for i, shot in enumerate(all_shots, 1):
            print(f"[{i}/{len(all_shots)}] 处理镜头 {shot['shot_number']}")
            
            # 检查提示词格式并提取场景参考
            scene_refs = []

            # 检查是否有背景参考
            if "【背景参考" in shot['prompt']:
                # 提取场景参考图名
                import re
                scene_match = re.search(r'【背景参考(.+?)】', shot['prompt'])
                if scene_match:
                    scene_name = scene_match.group(1)
                    scene_refs.append(scene_name)
                    print(f"  场景: {scene_name}")

            if shot['has_character']:
                # 验证提示词是否包含绑定声明
                if "【图一参考" not in shot['prompt']:
                    print(f"  警告：镜头 {shot['shot_number']} 有角色但提示词缺少绑定声明")

                # 分离角色参考图和场景参考图
                char_refs = []
                scene_refs = []

                for ref in shot['character_refs']:
                    # 检查是否在角色映射表中
                    if ref in ['linxuan.png', 'huijue.png', 'puti_zushi.png', 'rulai_fozu.png', 'sun_wukong.png', 'yudi.png', 'guanyin_pusa.png']:
                        char_refs.append(ref)
                    else:
                        scene_refs.append(ref)

                # 验证角色与角色参考图数量一致
                if len(shot['characters']) != len(char_refs):
                    print(f"  错误：镜头 {shot['shot_number']} 角色数与角色参考图数不匹配")
                    print(f"  角色数: {len(shot['characters'])}, 角色参考图数: {len(char_refs)}")
                    continue

                print(f"  角色: {', '.join(shot['characters'])}")

                # 生成图像
                url = self.generate_with_characters(
                    shot['prompt'],
                    char_refs,
                    scene_refs
                )
            else:
                url = self.generate_with_characters(
                    shot['prompt'],
                    [],
                    scene_refs
                )

            if url:
                # 构建输出路径
                if shot['has_character'] and shot['characters']:
                    char_names = "_".join(shot['characters'])
                else:
                    char_names = "scene"
                    
                output_path = os.path.join(
                    output_dir,
                    f"Episode-01-Shot-{shot['shot_number']}-{char_names}.png"
                )

                # 下载图片
                if self.download_image(url, output_path):
                    success_count += 1
                    print(f"  [OK] 生成成功")
                else:
                    print(f"  [FAIL] 下载失败")
            else:
                print(f"  [FAIL] 生成失败")

            # 避免请求过快
            time.sleep(2)

        # 输出统计
        print("\n" + "=" * 60)
        print(f"完成！成功生成 {success_count}/{len(all_shots)} 个镜头")
        print(f"  - 角色镜头: {len(character_shots)} 个")
        print(f"  - 场景镜头: {len(scene_shots)} 个")
        print("=" * 60)

# 使用示例
if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) != 3:
        print("用法: python seedream_character_only.py <json配置文件路径> <输出目录>")
        print("示例: python seedream_character_only.py Episode-01-ImagePrompts.json ./output_images")
        sys.exit(1)

    # 获取命令行参数
    json_file = sys.argv[1]
    output_dir = sys.argv[2]

    # 检查配置文件是否存在
    if not os.path.exists(json_file):
        print(f"错误：找不到配置文件 {json_file}")
        sys.exit(1)

    # 创建生成器
    generator = MultiCharacterGenerator()

    # 执行生成
    generator.generate_from_json(json_file, output_dir)