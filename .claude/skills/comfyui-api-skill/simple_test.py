#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI API Skill 简化测试脚本
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from comfyui_client import ComfyUIClient
    from workflow_manager import WorkflowManager
    from image_generator import NovelWebtoonImageGenerator

    print("成功导入ComfyUI API模块")

    # 测试工作流管理器
    print("\n测试工作流管理器...")
    manager = WorkflowManager()

    # 创建workflows目录
    workflows_dir = Path("comfyui-workflows")
    workflows_dir.mkdir(exist_ok=True)

    # 列出工作流文件
    workflows = manager.list_workflows()
    print(f"发现工作流文件: {workflows}")

    # 创建测试工作流
    print("\n创建测试工作流模板...")
    generator = NovelWebtoonImageGenerator()
    template_path = generator.create_workflow_from_template("test_workflow")
    print(f"模板创建成功: {template_path}")

    # 重新列出工作流
    workflows = manager.list_workflows()
    print(f"更新后的工作流文件: {workflows}")

    # 测试Excel数据处理
    print("\n测试Excel数据处理...")
    excel_files = [
        "FullFlow-完整制作流程.xlsx",
        "完整制作流程-统一表格.xlsx",
    ]

    found_excel = False
    for excel_file in excel_files:
        if os.path.exists(excel_file):
            print(f"找到Excel文件: {excel_file}")
            try:
                tasks = generator.process_excel_data(excel_file)
                print(f"成功处理Excel，加载了 {len(tasks)} 个任务")
                found_excel = True

                # 显示前3个任务
                for i, task in enumerate(tasks[:3], 1):
                    print(f"  任务{i}: 第{task['集数']}集镜头{task['镜头编号']}")
                break
            except Exception as e:
                print(f"处理Excel失败: {e}")

    if not found_excel:
        print("没有找到可用的Excel文件")

    print("\n=== 测试完成 ===")
    print("ComfyUI API技能包基础功能正常")
    print("\n使用说明:")
    print("1. 启动ComfyUI服务器 (127.0.0.1:8188)")
    print("2. 将工作流JSON文件复制到 comfyui-workflows/ 目录")
    print("3. 运行 image_generator.py 开始生成图像")

except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖已安装: pip install websocket-client openpyxl")
except Exception as e:
    print(f"测试过程中出现错误: {e}")