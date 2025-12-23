#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用增强版两步法生成整集镜头
基于验证成功的方法，确保面容保持
"""

import os
import sys
import json
import time
from typing import List, Dict

from batch_generator_enhanced import generate_shots_batch

def parse_storyboard_to_shots(storyboard_file: str) -> List[Dict]:
    """解析分镜文件，转换为镜头配置"""
    shots = []

    try:
        with open(storyboard_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简单解析逻辑（实际使用时可能需要更复杂的解析）
        sections = content.split('## Shot ')[1:]  # 跳过第一个空部分

        for section in sections:
            lines = section.strip().split('\n')
            if not lines:
                continue

            shot_num = lines[0].split()[0]

            # 提取关键信息
            shot_info = {
                'shot': int(shot_num),
                'location': '天庭斩仙台',
                'shot_type': '全景',
                'scene_desc': '',
                'character_name': '林玄',
                'position_desc': '跪在斩仙台中央',
                'lighting': '阴沉压抑',
                'lighting_effects': '铁链反射冷光',
                'expression': '倔强痛苦',
                'atmosphere': '肃穆压抑'
            }

            # 尝试从内容中提取更多信息
            full_text = '\n'.join(lines)
            if '特写' in full_text:
                shot_info['shot_type'] = '特写'
            if '慧觉' in full_text:
                shot_info['character_name'] = '林玄和慧觉'
                shot_info['position_desc'] = '林玄跪在台前，慧觉站立一旁'

            shots.append(shot_info)

    except Exception as e:
        print(f"解析分镜文件失败: {e}")

    return shots

def generate_episode(episode_num: int, storyboard_dir: str, output_base_dir: str):
    """生成一整集的图像"""

    # 输入文件
    storyboard_file = os.path.join(storyboard_dir, f"Episode-{episode_num:02d}-Storyboard.md")

    if not os.path.exists(storyboard_file):
        print(f"找不到分镜文件: {storyboard_file}")
        return

    # 输出目录
    output_dir = os.path.join(output_base_dir, f"Episode-{episode_num:02d}")

    print(f"\n{'='*60}")
    print(f"开始生成第 {episode_num} 集")
    print(f"{'='*60}")

    # 解析分镜
    shots = parse_storyboard_to_shots(storyboard_file)
    print(f"解析到 {len(shots)} 个镜头")

    # 批量生成
    generate_shots_batch(shots, output_dir)

    # 生成汇总报告
    report = {
        'episode': episode_num,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_shots': len(shots),
        'output_dir': output_dir,
        'method': '两步生成法（场景+人物融合）',
        'model': 'doubao-seedream-4-5-251128',
        'face_preservation': True
    }

    report_file = os.path.join(output_dir, 'generation_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n生成报告已保存: {report_file}")

if __name__ == "__main__":
    # 配置路径
    storyboard_dir = "outputs/run_20250213_153000_anime/03_storyboards"
    output_base_dir = "outputs/run_20250213_153000_anime/05_generated_images_enhanced"

    # 生成集数范围
    episodes = [1, 2, 3]  # 可以修改为需要的集数

    for episode in episodes:
        try:
            generate_episode(episode, storyboard_dir, output_base_dir)
        except Exception as e:
            print(f"生成第 {episode} 集时出错: {e}")
            continue

    print("\n" + "="*60)
    print("所有集数生成完成！")
    print("="*60)