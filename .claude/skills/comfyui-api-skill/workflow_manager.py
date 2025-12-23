#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Workflow Manager
ComfyUI工作流管理工具，用于管理多个工作流文件和参数映射
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class WorkflowManager:
    def __init__(self, workflows_dir: str = "comfyui-workflows"):
        """
        初始化工作流管理器

        Args:
            workflows_dir: 工作流文件目录
        """
        self.workflows_dir = Path(workflows_dir)
        self.workflows_dir.mkdir(exist_ok=True)

        # 工作流缓存
        self.loaded_workflows = {}

        # 常用参数映射
        self.common_param_mappings = {
            'positive_prompt': ['6.text', '7.text'],  # 常见的正向提示词节点
            'negative_prompt': ['11.text', '12.text'],  # 常见的负向提示词节点
            'seed': ['3.seed', '4.seed'],  # 种子节点
            'steps': ['3.steps', '4.steps'],  # 采样步数
            'cfg': ['3.cfg', '4.cfg'],  # CFG值
            'width': ['5.width', '8.width'],  # 图像宽度
            'height': ['5.height', '8.height'],  # 图像高度
            'batch_size': ['5.batch_size', '8.batch_size'],  # 批次大小
        }

    def list_workflows(self) -> List[str]:
        """
        列出所有可用的工作流文件

        Returns:
            List[str]: 工作流文件名列表
        """
        workflow_files = []
        for file_path in self.workflows_dir.glob("*.json"):
            workflow_files.append(file_path.name)
        return sorted(workflow_files)

    def load_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        加载工作流文件

        Args:
            workflow_name: 工作流文件名

        Returns:
            Dict: 工作流数据
        """
        if workflow_name in self.loaded_workflows:
            return self.loaded_workflows[workflow_name]

        workflow_path = self.workflows_dir / workflow_name
        if not workflow_path.exists():
            raise FileNotFoundError(f"工作流文件不存在: {workflow_path}")

        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)

            self.loaded_workflows[workflow_name] = workflow_data
            print(f"成功加载工作流: {workflow_name}")
            return workflow_data

        except Exception as e:
            raise Exception(f"加载工作流失败: {e}")

    def analyze_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        分析工作流结构，识别可修改的参数

        Args:
            workflow_name: 工作流文件名

        Returns:
            Dict: 工作流分析结果
        """
        workflow_data = self.load_workflow(workflow_name)

        analysis = {
            'nodes': {},
            'text_inputs': [],
            'numeric_inputs': [],
            'boolean_inputs': []
        }

        for node_id, node_data in workflow_data.items():
            node_class = node_data.get('class_type', 'Unknown')
            inputs = node_data.get('inputs', {})

            analysis['nodes'][node_id] = {
                'class_type': node_class,
                'inputs': list(inputs.keys())
            }

            # 分类输入类型
            for input_name, input_value in inputs.items():
                param_path = f"{node_id}.{input_name}"

                if isinstance(input_value, str):
                    analysis['text_inputs'].append({
                        'path': param_path,
                        'current_value': input_value,
                        'node_class': node_class
                    })
                elif isinstance(input_value, (int, float)):
                    analysis['numeric_inputs'].append({
                        'path': param_path,
                        'current_value': input_value,
                        'node_class': node_class
                    })
                elif isinstance(input_value, bool):
                    analysis['boolean_inputs'].append({
                        'path': param_path,
                        'current_value': input_value,
                        'node_class': node_class
                    })

        return analysis

    def find_parameter_nodes(self, workflow_name: str, parameter_type: str) -> List[str]:
        """
        查找特定类型参数的节点

        Args:
            workflow_name: 工作流文件名
            parameter_type: 参数类型 (positive_prompt, negative_prompt, seed, etc.)

        Returns:
            List[str]: 匹配的参数路径列表
        """
        analysis = self.analyze_workflow(workflow_name)
        matching_paths = []

        # 使用预定义的映射
        if parameter_type in self.common_param_mappings:
            potential_paths = self.common_param_mappings[parameter_type]
            for path in potential_paths:
                # 检查路径是否存在于工作流中
                node_id, input_name = path.split('.', 1)
                if node_id in analysis['nodes']:
                    if input_name in analysis['nodes'][node_id]['inputs']:
                        matching_paths.append(path)

        # 如果没有预定义映射，尝试基于节点类型和输入名称智能匹配
        if not matching_paths:
            if parameter_type == 'positive_prompt':
                for input_info in analysis['text_inputs']:
                    if 'text' in input_info['path'].lower() and 'positive' not in input_info['path'].lower():
                        matching_paths.append(input_info['path'])
                        break
            elif parameter_type == 'negative_prompt':
                for input_info in analysis['text_inputs']:
                    if 'negative' in input_info['path'].lower() or 'neg' in input_info['path'].lower():
                        matching_paths.append(input_info['path'])
                        break

        return matching_paths

    def create_parameter_template(self, workflow_name: str) -> Dict[str, Any]:
        """
        为工作流创建参数模板

        Args:
            workflow_name: 工作流文件名

        Returns:
            Dict: 参数模板
        """
        template = {
            'workflow_name': workflow_name,
            'parameters': {}
        }

        # 查找常用参数
        for param_type in self.common_param_mappings.keys():
            paths = self.find_parameter_nodes(workflow_name, param_type)
            if paths:
                template['parameters'][param_type] = {
                    'paths': paths,
                    'default_value': None,
                    'description': f"{param_type} parameter"
                }

        return template

    def save_parameter_template(self, workflow_name: str) -> str:
        """
        保存参数模板到文件

        Args:
            workflow_name: 工作流文件名

        Returns:
            str: 模板文件路径
        """
        template = self.create_parameter_template(workflow_name)

        template_name = workflow_name.replace('.json', '_template.json')
        template_path = self.workflows_dir / template_name

        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        print(f"参数模板已保存: {template_path}")
        return str(template_path)

    def build_param_modifications(self, template_file: str,
                                 values: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于模板和值构建参数修改字典

        Args:
            template_file: 参数模板文件路径
            values: 参数值字典

        Returns:
            Dict: 参数修改字典
        """
        with open(template_file, 'r', encoding='utf-8') as f:
            template = json.load(f)

        modifications = {}

        for param_type, param_info in template['parameters'].items():
            if param_type in values:
                value = values[param_type]
                paths = param_info['paths']

                # 对所有匹配的路径应用相同的值
                for path in paths:
                    modifications[path] = value

        return modifications

    def create_default_config(self) -> Dict[str, Any]:
        """
        创建默认配置文件

        Returns:
            Dict: 默认配置
        """
        default_config = {
            'server_address': '127.0.0.1:8188',
            'default_timeout': 300,
            'output_directory': 'generated_images',
            'default_parameters': {
                'steps': 20,
                'cfg': 8.0,
                'width': 512,
                'height': 768,
                'batch_size': 1
            }
        }

        config_path = self.workflows_dir / 'config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

        print(f"默认配置已创建: {config_path}")
        return default_config


def main():
    """示例用法"""
    manager = WorkflowManager()

    # 列出工作流
    workflows = manager.list_workflows()
    print(f"可用工作流: {workflows}")

    # 如果有工作流文件，分析第一个
    if workflows:
        workflow_name = workflows[0]
        print(f"\n分析工作流: {workflow_name}")

        # 分析工作流
        analysis = manager.analyze_workflow(workflow_name)
        print(f"节点数量: {len(analysis['nodes'])}")
        print(f"文本输入: {len(analysis['text_inputs'])}")
        print(f"数值输入: {len(analysis['numeric_inputs'])}")

        # 创建参数模板
        template_file = manager.save_parameter_template(workflow_name)

        # 示例：构建参数修改
        values = {
            'positive_prompt': 'a beautiful landscape',
            'seed': 12345,
            'steps': 25
        }
        modifications = manager.build_param_modifications(template_file, values)
        print(f"参数修改: {modifications}")

    # 创建默认配置
    manager.create_default_config()


if __name__ == "__main__":
    main()