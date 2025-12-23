#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI API Skill 测试脚本
用于测试ComfyUI API连接和基本功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from comfyui_client import ComfyUIClient
from workflow_manager import WorkflowManager
from image_generator import NovelWebtoonImageGenerator


def test_server_connection(server_address: str = "127.0.0.1:8188"):
    """测试ComfyUI服务器连接"""
    print("=== 测试服务器连接 ===")

    client = ComfyUIClient(server_address)

    try:
        import urllib.request
        response = urllib.request.urlopen(f"http://{server_address}/", timeout=10)
        print(f"服务器连接成功: {server_address}")
        return True
    except Exception as e:
        print(f"服务器连接失败: {e}")
        print(f"请确保ComfyUI服务器运行在 {server_address}")
        return False


def test_workflow_manager():
    """测试工作流管理器"""
    print("\n=== 测试工作流管理器 ===")

    manager = WorkflowManager()

    # 列出工作流
    workflows = manager.list_workflows()
    print(f"发现工作流文件: {workflows}")

    # 如果没有工作流，创建默认模板
    if not workflows:
        print("创建默认工作流模板...")
        generator = NovelWebtoonImageGenerator()
        template_path = generator.create_workflow_from_template("test_workflow")
        print(f"✅ 模板创建成功: {template_path}")

        workflows = manager.list_workflows()

    # 分析第一个工作流
    if workflows:
        workflow_name = workflows[0]
        print(f"\n分析工作流: {workflow_name}")

        try:
            analysis = manager.analyze_workflow(workflow_name)
            print(f"✅ 工作流分析成功")
            print(f"   节点数量: {len(analysis['nodes'])}")
            print(f"   文本输入: {len(analysis['text_inputs'])}")
            print(f"   数值输入: {len(analysis['numeric_inputs'])}")

            # 创建参数模板
            template_file = manager.save_parameter_template(workflow_name)
            print(f"✅ 参数模板保存: {template_file}")

            return True
        except Exception as e:
            print(f"❌ 工作流分析失败: {e}")
            return False

    return False


def test_image_generation_dry_run():
    """测试图像生成（干运行，不实际生成）"""
    print("\n=== 测试图像生成设置 ===")

    generator = NovelWebtoonImageGenerator()

    # 测试任务数据处理
    test_task = {
        '集数': 1,
        '镜头编号': 1,
        '场景': '山洞深处',
        '镜头类型': 'Medium Shot',
        '人物提示词': '叶凡，古装男子',
        '背景提示词': '昏暗的山洞，神秘氛围',
        '完整提示词': '叶凡站在昏暗的山洞深处，身穿古装，神情严肃，周围散发着神秘的光芒',
        'output_filename': 'Episode-01-Shot-01'
    }

    # 测试提示词增强
    original_prompt = test_task['完整提示词']
    enhanced_prompt = generator.enhance_prompt_with_consistency(
        original_prompt, ['叶凡', '男主角']
    )

    print(f"原始提示词: {original_prompt}")
    print(f"增强提示词: {enhanced_prompt}")

    if enhanced_prompt != original_prompt:
        print("✅ 角色一致性增强功能正常")
    else:
        print("⚠️ 角色一致性增强未生效")

    return True


def test_excel_processing():
    """测试Excel数据处理"""
    print("\n=== 测试Excel数据处理 ===")

    generator = NovelWebtoonImageGenerator()

    # 检查Excel文件是否存在
    excel_files = [
        "FullFlow-完整制作流程.xlsx",
        "完整制作流程-统一表格.xlsx",
        "网文改编漫剧完整项目-新版.xlsx"
    ]

    for excel_file in excel_files:
        if os.path.exists(excel_file):
            print(f"找到Excel文件: {excel_file}")

            try:
                tasks = generator.process_excel_data(excel_file)
                if tasks:
                    print(f"✅ Excel数据处理成功，加载了 {len(tasks)} 个任务")

                    # 显示前几个任务的信息
                    for i, task in enumerate(tasks[:3], 1):
                        print(f"   任务{i}: 第{task['集数']}集镜头{task['镜头编号']} - {task['场景']}")

                    return True
                else:
                    print("⚠️ Excel文件中没有找到有效任务")
            except Exception as e:
                print(f"❌ Excel数据处理失败: {e}")

    print("❌ 没有找到可用的Excel文件")
    return False


def main():
    """运行所有测试"""
    print("ComfyUI API Skill 功能测试")
    print("=" * 50)

    test_results = []

    # 测试服务器连接
    test_results.append(("服务器连接", test_server_connection()))

    # 测试工作流管理
    test_results.append(("工作流管理", test_workflow_manager()))

    # 测试图像生成设置
    test_results.append(("图像生成设置", test_image_generation_dry_run()))

    # 测试Excel处理
    test_results.append(("Excel数据处理", test_excel_processing()))

    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")

    passed = 0
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总体结果: {passed}/{len(test_results)} 项测试通过")

    if passed == len(test_results):
        print("\n🎉 所有测试通过！ComfyUI API技能包已准备就绪。")
        print("\n下一步:")
        print("1. 确保ComfyUI服务器运行在 127.0.0.1:8188")
        print("2. 将你的工作流JSON文件复制到 comfyui-workflows/ 目录")
        print("3. 运行 image_generator.py 开始批量生成图像")
    else:
        print(f"\n⚠️ 有 {len(test_results) - passed} 项测试失败，请检查配置。")


if __name__ == "__main__":
    main()