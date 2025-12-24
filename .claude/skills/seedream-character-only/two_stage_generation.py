#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两阶段图像生成流程 - 完整版
阶段1：生成角色参考图和场景参考图
阶段2：使用参考图进行图生图，生成最终镜头
"""

import requests
import json
import base64
import os
import time
import sys
from pathlib import Path

class TwoStageImageGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or "ak-yXx1CsHzL3J6HRakOLPmSAXaDcnPDcAy"
        self.base_url = "https://model-api.skyengine.com.cn/v1"

        # 输出目录
        self.character_ref_dir = "character_images"
        self.scene_ref_dir = "scene_images"
        self.final_output_dir = "final_shots"

    def encode_image(self, image_path):
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_text_to_image(self, prompt, size="2048x2048", model="doubao-seedream-4-5-251128"):
        """文生图：生成角色和场景参考图"""
        url = f"{self.base_url}/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "prompt": prompt,
            "model": model,
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
            print(f"  API错误: {response.status_code} - {response.text}")

        return None

    def generate_image_to_image(self, prompt, ref_images, size="2560x1440"):  # 16:9比例，约370万像素
        """图生图：使用参考图生成最终镜头"""
        url = f"{self.base_url}/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 编码参考图
        encoded_images = []
        for img_path in ref_images:
            if os.path.exists(img_path):
                encoded_images.append(f"data:image/png;base64,{self.encode_image(img_path)}")

        if not encoded_images:
            print("  错误：没有找到参考图")
            return None

        data = {
            "prompt": prompt + " 严格保持参考图中角色的面容特征、发型、服装完全一致，不要改变角色外观。",
            "model": "doubao-seedream-4-5-251128",
            "image": encoded_images,  # 图生图关键参数
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
            print(f"  API错误: {response.status_code} - {response.text}")

        return None

    def download_image(self, url, output_path):
        """下载并保存图片"""
        try:
            response = requests.get(url, timeout=120)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"  下载失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"  下载异常: {e}")
        return False

    # ==================== 阶段1：生成参考图 ====================

    def stage1_generate_references(self):
        """阶段1：生成所有角色和场景参考图"""
        print("=" * 70)
        print("阶段1：生成角色参考图和场景参考图")
        print("=" * 70)

        # 定义需要生成的角色参考图
        character_references = {
            "林渊_囚服": {
                "prompt": """【角色：林渊】中国青年男性，约25岁，修仙者转凡人囚徒形象。
脸型瘦削，剑眉星目，鼻梁高挺，眼神坚毅锐利，嘴唇薄而坚定。黑色短发，因牢狱生活略显凌乱。
服装：破旧的灰色囚服，衣衫褴褛多处破损撕裂，身上有明显血迹斑斑，赤足。
神态：面容苍白虚弱，但眼神中透着不屈和战意，神情冷冽。
国风动漫风格，大眼睛精致面容，8-9头身比例，流畅线条，色彩鲜明对比强烈。半身像，侧光照射形成明暗对比，突出眼神的锐利。高质量动漫插画，4K画质，画面干净无水印。""",
                "filename": "linxuan.png"
            },
            "林渊_现代": {
                "prompt": """【角色：林渊（现代）】中国青年男性，约25岁，资深程序员。
脸型瘦削，戴黑框眼镜，眼神专注疲惫，有淡淡黑眼圈。黑色短发，整洁职场风格。
服装：白色衬衫（领口解开，袖子挽起），黑色休闲裤。
神态：专注盯着屏幕，表情疲惫但眼神有光。现代写实与动漫风格融合，高质量插画，4K。""",
                "filename": "linxuan_modern.png"
            },
            "青袍修士": {
                "prompt": """【角色：青袍修士】中国青年男性，约35岁，炼气期修士。
脸型方正，神情冷傲高傲，眼神居高临下。黑色长发束在头顶，戴玉冠。
服装：青色长袍，上有金色云纹刺绣，腰间佩剑，衣袍飘飘。
神态：高高在上，冷漠，眼神中带着对凡人的不屑。
国风动漫风格，仙风道骨，流畅线条，色彩鲜明对比强烈（青色与金色）。全身像，仙家灵力光晕环绕。高质量仙侠动漫插画，4K。""",
                "filename": "huijue.png"
            }
        }

        # 定义需要生成的场景参考图
        scene_references = {
            "矿洞": {
                "prompt": """【场景：陈塘关矿场地下深处】仙侠矿洞。
远景：矿洞顶部倒悬密集钟乳石，洞壁有火把照明。中景：地面刻着复杂血色阵法纹路，阵法脉动发光。近景：阵法纹路血红色光，地面石板古老刻痕。
阴暗压抑神秘氛围。阴沉暗光环境，血红色阵法光芒在洞壁投下诡异影子。
国风动漫风格，电影级远景，16:9画幅，色彩鲜明对比强烈（红色阵法与暗背景）。高质量仙侠场景插画，4K。""",
                "filename": "矿洞.png"
            },
            "现代办公室": {
                "prompt": """【场景：现代办公室深夜】现代办公场景。
落地窗外城市夜景，霓虹灯光。办公桌上有电脑显示器、键盘、咖啡杯，屏幕显示代码。
现代孤寂氛围。办公室灯光，电脑屏幕蓝光照亮桌面。
现代写实与动漫风格融合，16:9画幅。高质量场景插画，4K。""",
                "filename": "现代办公室.png"
            },
            "系统界面": {
                "prompt": """【场景：封神榜系统界面】科幻仙侠系统UI。
金色半透明系统面板悬浮暗色背景，显示【封神榜第365号神位出现绑定延迟...检测到未知变量接触...】。面板边缘金色光粒子飘散，数据流交织成网。
科幻神秘系统级氛围。金色面板自发光，在暗色背景投下金色光晕。
国风动漫+科幻融合，流畅线条，16:9画幅，色彩鲜明对比强烈（金色与暗色）。高质量UI界面插画，4K。""",
                "filename": "系统界面.png"
            },
            "封神榜虚空": {
                "prompt": """【场景：封神榜虚空】宏大仙侠虚空。
无穷高远虚空深处，漫天金色星云。巨大金色榜单悬浮，铭刻无数名字，每个名字旁缠绕因果线条（有的炽烈如火，有的晦暗如灰）。
震撼威严宿命感。金色光芒自发光照亮虚空。
国风动漫风格，电影级远景，仰拍角度，16:9画幅，流畅线条。高质量仙侠场景插画，4K。""",
                "filename": "封神榜虚空.png"
            },
            "偏房": {
                "prompt": """【场景：破旧偏房】简陋古代房间。
窗外夜色深沉，月光微弱。简陋床榻，破旧桌椅，房间陈设简单。床榻被褥，桌上油灯。
孤寂清冷氛围。昏暗灯光，窗外月光微弱，油灯暖黄色光。
国风动漫风格，16:9画幅。高质量场景插画，4K。""",
                "filename": "偏房.png"
            },
            "命数轨迹": {
                "prompt": """【场景：虚空命数轨迹】抽象仙侠概念场景。
无数金色线条在虚空中流动，代表命数。有的平缓，有的陡峭，有的断裂，有的被标上血红色【必死节点】标记。节点闪烁红光。
宿命震撼系统化氛围。金色线条自发光，红色节点闪烁，暗色背景。
国风动漫+抽象概念融合，电影级远景，16:9画幅，流畅线条。高质量概念场景插画，4K。""",
                "filename": "命数轨迹.png"
            },
            "天空": {
                "prompt": """【场景：阴沉天空系统文字】仙侠天空。
阴沉天空，灰色云层厚重。巨大灰色文字悬浮【灾备协议触发：预热中...备份节点：启动倒计时...】。文字边缘灰色光晕。
诡异系统压迫感。灰色文字自发光照亮云层。
国风动漫风格，电影级远景，仰拍角度，16:9画幅。高质量场景插画，4K。""",
                "filename": "天空.png"
            }
        }

        # 生成角色参考图
        print("\n【生成角色参考图】")
        char_success = 0
        for name, info in character_references.items():
            print(f"\n生成角色: {name}")
            output_path = os.path.join(self.character_ref_dir, info['filename'])

            if os.path.exists(output_path):
                print(f"  [跳过] 文件已存在: {output_path}")
                char_success += 1
                continue

            url = self.generate_text_to_image(info['prompt'])
            if url and self.download_image(url, output_path):
                print(f"  [OK] 生成成功: {output_path}")
                char_success += 1
            else:
                print(f"  [FAIL] 生成失败")

            time.sleep(3)

        # 生成场景参考图
        print("\n【生成场景参考图】")
        scene_success = 0
        for name, info in scene_references.items():
            print(f"\n生成场景: {name}")
            output_path = os.path.join(self.scene_ref_dir, info['filename'])

            if os.path.exists(output_path):
                print(f"  [跳过] 文件已存在: {output_path}")
                scene_success += 1
                continue

            url = self.generate_text_to_image(info['prompt'])
            if url and self.download_image(url, output_path):
                print(f"  [OK] 生成成功: {output_path}")
                scene_success += 1
            else:
                print(f"  [FAIL] 生成失败")

            time.sleep(3)

        print("\n" + "=" * 70)
        print(f"阶段1完成！")
        print(f"  角色参考图: {char_success}/{len(character_references)}")
        print(f"  场景参考图: {scene_success}/{len(scene_references)}")
        print(f"  总计: {char_success + scene_success}/{len(character_references) + len(scene_references)}")
        print("=" * 70)

        return char_success + scene_success > 0

    # ==================== 阶段2：生成最终镜头 ====================

    def stage2_generate_shots(self, prompts_json_file, output_dir):
        """阶段2：使用参考图生成最终镜头"""
        print("\n" + "=" * 70)
        print("阶段2：使用参考图生成最终镜头")
        print("=" * 70)

        # 检查参考图是否存在
        required_chars = ["linxuan.png", "huijue.png"]
        required_scenes = ["矿洞.png", "系统界面.png"]

        missing = []
        for f in required_chars:
            if not os.path.exists(os.path.join(self.character_ref_dir, f)):
                missing.append(f"角色: {f}")
        for f in required_scenes:
            if not os.path.exists(os.path.join(self.scene_ref_dir, f)):
                missing.append(f"场景: {f}")

        if missing:
            print("\n❌ 缺少参考图，请先运行阶段1：")
            for m in missing:
                print(f"  - {m}")
            return False

        # 加载提示词配置
        with open(prompts_json_file, 'r', encoding='utf-8') as f:
            shots = json.load(f)

        print(f"\n共 {len(shots)} 个镜头待生成")
        print(f"输出目录: {output_dir}\n")

        success_count = 0

        for i, shot in enumerate(shots, 1):
            shot_num = shot.get('shot_number', f'shot_{i:03d}')
            print(f"[{i}/{len(shots)}] {shot_num}")

            # 收集参考图
            ref_images = []
            prompt = shot['prompt']

            # 提取角色参考图
            if 'characters' in shot and shot['characters']:
                for char in shot['characters']:
                    # 映射角色到文件名
                    if '林渊' in char:
                        ref_path = os.path.join(self.character_ref_dir, "linxuan.png")
                        if os.path.exists(ref_path):
                            ref_images.append(ref_path)
                    elif '修士' in char or '慧觉' in char or '青袍' in char:
                        ref_path = os.path.join(self.character_ref_dir, "huijue.png")
                        if os.path.exists(ref_path):
                            ref_images.append(ref_path)

            # 提取场景参考图
            import re
            scene_matches = re.findall(r'【背景参考(.+?)】', prompt)
            for scene_name in scene_matches:
                scene_path = os.path.join(self.scene_ref_dir, f"{scene_name}.png")
                if os.path.exists(scene_path):
                    ref_images.append(scene_path)

            print(f"  使用参考图: {len(ref_images)} 张")

            # 生成图像
            if ref_images:
                url = self.generate_image_to_image(prompt, ref_images)
            else:
                # 没有参考图，使用文生图
                url = self.generate_text_to_image(prompt)

            if url:
                output_path = os.path.join(output_dir, f"Episode-01-{shot_num}.png")
                if self.download_image(url, output_path):
                    print(f"  [OK] {output_path}")
                    success_count += 1
                else:
                    print(f"  [FAIL] 下载失败")
            else:
                print(f"  [FAIL] 生成失败")

            time.sleep(3)

        print("\n" + "=" * 70)
        print(f"阶段2完成！成功生成 {success_count}/{len(shots)} 个镜头")
        print("=" * 70)

        return success_count > 0


# ==================== 主程序 ====================

if __name__ == "__main__":
    generator = TwoStageImageGenerator()

    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法:")
        print("  python two_stage_generation.py --stage1    # 生成参考图")
        print("  python two_stage_generation.py --stage2 <prompts.json> <output_dir>  # 生成最终镜头")
        print("\n示例:")
        print("  python two_stage_generation.py --stage1")
        print("  python two_stage_generation.py --stage2 outputs/run_20251223_233308_anime/02.5_validation/fixed_prompts.json outputs/run_20251223_233308_anime/03_generated_images/Episode-01")
        sys.exit(1)

    stage = sys.argv[1]

    if stage == "--stage1":
        # 阶段1：生成参考图
        success = generator.stage1_generate_references()
        if success:
            print("\n✅ 阶段1完成！现在可以运行阶段2生成最终镜头")
        else:
            print("\n❌ 阶段1失败，请检查API和网络连接")

    elif stage == "--stage2":
        # 阶段2：生成最终镜头
        if len(sys.argv) != 4:
            print("错误：阶段2需要两个参数")
            print("用法: python two_stage_generation.py --stage2 <prompts.json> <output_dir>")
            sys.exit(1)

        prompts_file = sys.argv[2]
        output_dir = sys.argv[3]

        if not os.path.exists(prompts_file):
            print(f"错误：找不到提示词文件 {prompts_file}")
            sys.exit(1)

        success = generator.stage2_generate_shots(prompts_file, output_dir)
        if success:
            print("\n✅ 阶段2完成！所有镜头已生成")
        else:
            print("\n❌ 阶段2失败")

    else:
        print(f"错误：未知参数 {stage}")
        print("使用 --stage1 或 --stage2")
        sys.exit(1)
