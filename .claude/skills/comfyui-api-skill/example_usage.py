#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI API Skill 使用示例
演示如何在网文改编项目中使用ComfyUI生成图像
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from image_generator import NovelWebtoonImageGenerator


def example_single_image():
    """示例：生成单张图像"""
    print("=== 示例：生成单张图像 ===")

    generator = NovelWebtoonImageGenerator()

    # 模拟一个镜头任务
    test_task = {
        '集数': 1,
        '镜头编号': 1,
        '场景': '山洞深处',
        '镜头类型': 'Medium Shot',
        '人物提示词': '叶凡，古装男子，深邃眼神',
        '背景提示词': '昏暗的山洞，神秘光芒',
        '完整提示词': '叶凡站在昏暗的山洞深处，身穿古装，神情严肃，周围散发着神秘的光芒，古风画面，高质量',
        'output_filename': 'Episode-01-Shot-01'
    }

    print(f"任务: 第{test_task['集数']}集镜头{test_task['镜头编号']}")
    print(f"提示词: {test_task['完整提示词'][:50]}...")

    # 注意：这需要ComfyUI服务器运行在 127.0.0.1:8188
    # 如果服务器未运行，这个调用会失败
    try:
        success, files = generator.generate_single_image(test_task)
        if success:
            print(f"生成成功！文件: {files}")
        else:
            print("生成失败，请检查ComfyUI服务器状态")
    except Exception as e:
        print(f"生成过程中出错: {e}")
        print("请确保ComfyUI服务器运行在 127.0.0.1:8188")


def example_batch_from_excel():
    """示例：从Excel文件批量生成"""
    print("\n=== 示例：从Excel批量生成图像 ===")

    generator = NovelWebtoonImageGenerator()

    # 查找可用的Excel文件
    excel_files = [
        "FullFlow-完整制作流程.xlsx",
        "完整制作流程-统一表格.xlsx"
    ]

    excel_file = None
    for file_path in excel_files:
        if os.path.exists(file_path):
            excel_file = file_path
            break

    if excel_file:
        print(f"使用Excel文件: {excel_file}")

        # 先处理数据看看有多少任务
        tasks = generator.process_excel_data(excel_file)
        print(f"发现 {len(tasks)} 个图像生成任务")

        # 显示前5个任务
        print("前5个任务:")
        for i, task in enumerate(tasks[:5], 1):
            print(f"  {i}. 第{task['集数']}集镜头{task['镜头编号']}: {task['场景']}")

        # 实际批量生成（需要ComfyUI服务器）
        print("\n开始批量生成...")
        try:
            results = generator.batch_generate_from_excel(excel_file)

            print("\n生成结果:")
            print(f"总任务数: {results['total_tasks']}")
            print(f"成功: {results['successful_tasks']}")
            print(f"失败: {results['failed_tasks']}")
            print(f"生成文件数: {len(results['generated_files'])}")

            if results['errors']:
                print("错误信息:")
                for error in results['errors'][:5]:  # 只显示前5个错误
                    print(f"  - {error}")

        except Exception as e:
            print(f"批量生成失败: {e}")
            print("这通常是因为ComfyUI服务器未运行或工作流文件问题")
    else:
        print("没有找到可用的Excel文件")


def example_workflow_management():
    """示例：工作流管理"""
    print("\n=== 示例：工作流管理 ===")

    from workflow_manager import WorkflowManager

    manager = WorkflowManager()

    # 列出所有工作流
    workflows = manager.list_workflows()
    print(f"可用工作流: {workflows}")

    if workflows:
        workflow_name = workflows[0]
        print(f"\n分析工作流: {workflow_name}")

        # 分析工作流结构
        analysis = manager.analyze_workflow(workflow_name)
        print(f"节点数: {len(analysis['nodes'])}")
        print(f"文本输入: {len(analysis['text_inputs'])}")

        # 显示文本输入节点
        print("文本输入节点:")
        for text_input in analysis['text_inputs'][:3]:  # 只显示前3个
            print(f"  {text_input['path']}: {text_input['current_value'][:30]}...")

        # 创建参数模板
        template_file = manager.save_parameter_template(workflow_name)
        print(f"参数模板已保存: {template_file}")


def example_custom_parameters():
    """示例：自定义参数生成"""
    print("\n=== 示例：自定义参数生成 ===")

    from comfyui_client import ComfyUIClient

    client = ComfyUIClient()

    # 自定义参数示例
    custom_params = {
        "6.text": "古风美男，站在仙境般的山洞中，身着白色古装，神情坚毅，周围仙雾缭绕",
        "7.text": "lowres, bad anatomy, bad hands, text, error, blurry",
        "3.seed": 42,
        "3.steps": 25,
        "3.cfg": 7.5,
        "5.width": 768,
        "5.height": 1024,
        "5.batch_size": 1
    }

    print("自定义参数:")
    for param, value in custom_params.items():
        if isinstance(value, str) and len(value) > 50:
            print(f"  {param}: {value[:50]}...")
        else:
            print(f"  {param}: {value}")

    print("\n注意：实际生成需要ComfyUI服务器运行")


def main():
    """运行所有示例"""
    print("ComfyUI API Skill 使用示例")
    print("=" * 50)

    print("注意：以下示例需要ComfyUI服务器运行在 127.0.0.1:8188")
    print("如果没有运行服务器，生成操作会失败，但其他功能仍可正常演示")
    print()

    # 工作流管理示例
    example_workflow_management()

    # 自定义参数示例
    example_custom_parameters()

    # Excel批量处理示例
    example_batch_from_excel()

    # 单图生成示例（可能失败如果没有ComfyUI服务器）
    # example_single_image()

    print("\n" + "=" * 50)
    print("示例演示完成！")
    print("\n如何开始实际使用:")
    print("1. 启动ComfyUI服务器: python main.py --listen 127.0.0.1 --port 8188")
    print("2. 将你的工作流JSON导出并复制到 comfyui-workflows/ 目录")
    print("3. 取消注释 example_single_image() 来测试单图生成")
    print("4. 使用 generator.batch_generate_from_excel() 进行批量生成")


if __name__ == "__main__":
    main()