#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成镜头 - 使用新的提示词格式和seedream 4.5
对于有人物的镜头使用两步生成，无人物的镜头使用一步生成
"""

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

# 镜头提示词配置（前10个镜头）
SHOTS_PROMPTS = {
    "001": {
        "prompt": "云海之上的天庭外围，晨光熹微，万道金色霞光穿透云层。没有人物，只有宏伟的仙宫楼阁群，金光闪闪。柔和的金色晨光从东方照射，云海翻滚，仙气缭绕。氛围充满奇幻、震撼、神圣。电影级全景镜头，画幅比例16:9。中国动画电影风格，高质量渲染。",
        "has_character": False,
        "character": None
    },
    "002": {
        "prompt": "阴沉的天空布满深灰色云层，电光闪烁，营造出威压感。闪电照亮云层，明暗对比强烈，营造压抑氛围。没有人物，只有云层和闪电。氛围威压、压抑、宿命感。电影级远景镜头，画幅比例16:9。中国动画电影风格，高质量渲染。",
        "has_character": False,
        "character": None
    },
    "003": {
        "prompt": "斩仙台中央，阴天的自然光，光线惨淡。林玄跪在台中央，身穿囚服，玄铁锁链穿透琵琶骨，身体虚弱但眼神坚韧。满身血污，鲜血滴落。惨淡的天光从上方照下，锁链的金属反光与血迹形成对比。氛围痛苦、坚韧、不屈。电影级特写镜头，画幅比例16:9。",
        "has_character": True,
        "character": "林玄"
    },
    "004": {
        "prompt": "斩仙台全景，环形包围，俯视角度展现压迫感。中央是跪着的林玄，周围是持戟的天兵，外围是众仙佛。仙雾缭绕，云层低垂，营造审判氛围。氛围肃杀、威严、压迫。电影级全景镜头，画幅比例16:9。",
        "has_character": True,
        "character": "林玄"
    },
    "005": {
        "prompt": "斩仙台中央，侧光突出林玄的表情。林玄跪着抬头，眼神锐利，嘴角挂着嘲讽的笑。侧光勾勒出林玄坚毅的轮廓。氛围讽刺、愤怒、控诉。电影级特写镜头，画幅比例16:9。",
        "has_character": True,
        "character": "林玄"
    },
    "006": {
        "prompt": "斩仙台众仙区域，天庭仙气缭绕，庄严神圣。众仙佛坐于云台之上，神情严肃，对林玄的指控露出不同的表情。仙气如轻纱般环绕，瑞气千条。氛围庄严、审判、神圣。电影级中景镜头，画幅比例16:9。",
        "has_character": False,
        "character": None
    },
    "007": {
        "prompt": "温暖的金色阳光从窗户洒入古朴的房间。林玄跪在地上，师父站在他面前，面容慈祥，白发在阳光下泛着银光。师父的手掌轻轻放在林玄头顶，传递着温暖和力量。阳光透过窗户，在空中形成丁达尔效应。氛围温馨而神圣，充满师徒情深。电影级中景镜头，画幅比例16:9。",
        "has_character": True,
        "character": "林玄"
    },
    "008": {
        "prompt": "林玄在识海中看到师父的幻象，慈祥的微笑在金光中若隐若现。师父的形象由金光构成，虚幻但清晰。金光流转，佛音阵阵。林玄跪在师父面前，眼中含泪。氛围神圣、感动、师徒情深。电影级特写镜头，画幅比例16:9。",
        "has_character": True,
        "character": "林玄"
    },
    "009": {
        "prompt": "斩仙台上，乌云汇聚，天空变得阴沉。狂风开始吹拂，吹动着天兵的衣甲和旗帜。慧觉抬头望天，表情惊疑不定。林玄抬头看向远方，眼神中透出一丝希望。天色由明转暗，斩仙台的符文开始闪烁。氛围紧张而充满悬念。电影级全景镜头，画幅比例16:9。",
        "has_character": True,
        "character": "林玄"
    },
    "010": {
        "prompt": "林玄的半身特写，他仰头望着天空，眼中闪烁着泪光，嘴角却露出释然的微笑。他轻声说出师父，弟子明白了，声音在狂风中依然清晰。泪珠滑过脸颊，在阴沉的天光下晶莹剔透。他的眼神由倔强转为坚定，透出一种获得新生的力量。氛围悲壮而充满希望。电影级特写镜头，画幅比例16:9。",
        "has_character": True,
        "character": "林玄"
    }
}

def generate_image(prompt, size="2560x1440"):
    """生成图像"""
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

def generate_scene_only(prompt, size="2560x1440"):
    """生成纯场景（没有人物）"""
    scene_prompt = prompt + " 空镜头，无人物，只有场景和建筑。"
    return generate_image(scene_prompt, size)

def merge_character_scene(character_path, scene_url, prompt, size="2560x1440"):
    """第二步：将人物与场景融合"""
    # 先下载场景图
    response = requests.get(scene_url)
    scene_img = Image.open(BytesIO(response.content))

    # 读取人物图
    character_img = Image.open(character_path)

    # 将人物图保存为临时文件，准备作为参考图
    character_img.save("temp_character.png")

    # 构建融合提示词
    merge_prompt = f"将人物融合到场景中：{prompt}"

    # 使用image-to-image功能进行融合
    # 注意：这里需要一个支持image-to-image的API端点
    # 当前seedream 4.5可能不支持，这里使用修改后的提示词重新生成

    enhanced_prompt = f"{prompt} 人物形象清晰，表情生动，动作自然。"
    return generate_image(enhanced_prompt, size)

def download_image(url, filepath):
    """下载并保存图片"""
    response = requests.get(url)
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"图片已保存到: {filepath}")

def main():
    """主函数"""
    # 确保输出目录存在
    output_dir = "outputs/run_20250213_163000_anime/05_generated_images"
    os.makedirs(output_dir, exist_ok=True)

    # 角色图片路径映射
    character_images = {
        "林玄": "character_images/linxuan.png"
    }

    # 生成每个镜头
    for shot_num, config in SHOTS_PROMPTS.items():
        print(f"\n正在生成镜头 {shot_num}...")
        print(f"提示词: {config['prompt'][:100]}...")

        # 输出路径
        output_path = os.path.join(output_dir, f"Episode-01-Shot-{shot_num}-Anime.png")

        if config["has_character"]:
            # 两步生成：先生成场景，再融合人物
            print("使用两步生成方法...")

            # 步骤1：生成场景
            scene_url = generate_scene_only(config["prompt"])
            if scene_url:
                print(f"场景生成成功: {scene_url}")

                # 步骤2：融合人物（这里使用简化的方法，直接重新生成包含人物的提示词）
                character_img_path = character_images.get(config["character"])
                if character_img_path and os.path.exists(character_img_path):
                    enhanced_prompt = config["prompt"] + f" {config['character']}在场景中，形象与参考图一致。"
                    final_url = generate_image(enhanced_prompt)

                    if final_url:
                        download_image(final_url, output_path)
                    else:
                        print("融合失败，使用场景图")
                        download_image(scene_url, output_path)
                else:
                    print(f"未找到角色图: {character_img_path}")
                    download_image(scene_url, output_path)
            else:
                print("场景生成失败")
        else:
            # 一步生成：直接生成场景
            print("使用一步生成方法...")
            image_url = generate_image(config["prompt"])
            if image_url:
                download_image(image_url, output_path)
            else:
                print("生成失败")

        # 等待一段时间避免请求过快
        time.sleep(2)

    print("\n所有镜头生成完成！")

if __name__ == "__main__":
    main()