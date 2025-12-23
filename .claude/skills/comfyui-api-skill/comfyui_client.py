#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI API Client
ComfyUI API调用客户端，支持工作流加载、参数修改、任务提交和监控
"""

import json
import uuid
import urllib.request
import urllib.parse
import urllib.error
import time
import os
import websocket
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class ComfyUIClient:
    def __init__(self, server_address: str = "127.0.0.1:8188"):
        """
        初始化ComfyUI API客户端

        Args:
            server_address: ComfyUI服务器地址，格式为 "ip:port"
        """
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.base_url = f"http://{server_address}"
        self.ws_url = f"ws://{server_address}/ws?clientId={self.client_id}"

        # 任务状态跟踪
        self.active_tasks = {}
        self.completed_tasks = {}

    def load_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """
        加载ComfyUI工作流JSON文件

        Args:
            workflow_path: 工作流JSON文件路径

        Returns:
            Dict: 工作流数据
        """
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            print(f"成功加载工作流: {workflow_path}")
            return workflow_data
        except Exception as e:
            print(f"加载工作流失败: {e}")
            return {}

    def modify_workflow_params(self, workflow_data: Dict[str, Any],
                             param_modifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        修改工作流中的参数

        Args:
            workflow_data: 原始工作流数据
            param_modifications: 参数修改字典，格式为 {"node_id.input_name": "new_value"}

        Returns:
            Dict: 修改后的工作流数据
        """
        modified_workflow = workflow_data.copy()

        for param_path, new_value in param_modifications.items():
            try:
                # 解析参数路径，格式：node_id.input_name
                if '.' in param_path:
                    node_id, input_name = param_path.split('.', 1)
                    if node_id in modified_workflow:
                        if 'inputs' not in modified_workflow[node_id]:
                            modified_workflow[node_id]['inputs'] = {}
                        modified_workflow[node_id]['inputs'][input_name] = new_value
                        print(f"修改参数: {param_path} = {new_value}")
                    else:
                        print(f"警告: 节点 {node_id} 不存在")
                else:
                    print(f"警告: 参数路径格式错误: {param_path}")
            except Exception as e:
                print(f"修改参数失败: {param_path}, 错误: {e}")

        return modified_workflow

    def submit_prompt(self, workflow_data: Dict[str, Any]) -> Optional[str]:
        """
        提交提示词任务到ComfyUI

        Args:
            workflow_data: 工作流数据

        Returns:
            str: 任务ID (prompt_id)，如果失败返回None
        """
        try:
            prompt_request = {
                "prompt": workflow_data,
                "client_id": self.client_id
            }

            data = json.dumps(prompt_request).encode('utf-8')
            request = urllib.request.Request(
                f"{self.base_url}/prompt",
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            response = urllib.request.urlopen(request)
            result = json.loads(response.read().decode('utf-8'))

            prompt_id = result.get('prompt_id')
            if prompt_id:
                print(f"任务提交成功，ID: {prompt_id}")
                self.active_tasks[prompt_id] = {
                    'status': 'submitted',
                    'timestamp': time.time()
                }
                return prompt_id
            else:
                print("任务提交失败：未获取到prompt_id")
                return None

        except urllib.error.HTTPError as e:
            print(f"HTTP错误: {e.code} - {e.reason}")
            if hasattr(e, 'read'):
                error_detail = e.read().decode('utf-8')
                print(f"错误详情: {error_detail}")
            return None
        except Exception as e:
            print(f"提交任务时出错: {e}")
            return None

    def check_task_status(self, prompt_id: str) -> Dict[str, Any]:
        """
        检查任务状态

        Args:
            prompt_id: 任务ID

        Returns:
            Dict: 任务状态信息
        """
        try:
            # 先检查任务是否在队列中（正在运行或等待）
            request = urllib.request.Request(f"{self.base_url}/queue")
            response = urllib.request.urlopen(request)
            queue_data = json.loads(response.read().decode('utf-8'))

            # 检查是否在运行队列中
            for item in queue_data.get('queue_running', []):
                if len(item) >= 2 and item[1] == prompt_id:
                    return {'completed': False, 'status_str': 'running', 'outputs': {}}

            # 检查是否在等待队列中
            for item in queue_data.get('queue_pending', []):
                if len(item) >= 2 and item[1] == prompt_id:
                    return {'completed': False, 'status_str': 'pending', 'outputs': {}}

            # 如果不在队列中，查询history
            request = urllib.request.Request(f"{self.base_url}/history/{prompt_id}")
            response = urllib.request.urlopen(request)
            history = json.loads(response.read().decode('utf-8'))

            if prompt_id in history:
                task_info = history[prompt_id]
                status = task_info.get('status', {})
                # 如果在history中找到了，说明已完成
                return {
                    'completed': True,
                    'status_str': status.get('status_str', 'completed'),
                    'outputs': task_info.get('outputs', {})
                }
            else:
                # 既不在队列也不在history中，可能刚提交还未开始
                return {'completed': False, 'status_str': 'pending', 'outputs': {}}

        except Exception as e:
            print(f"检查任务状态时出错: {e}")
            return {'completed': False, 'status_str': 'error', 'outputs': {}}

    def wait_for_completion(self, prompt_id: str, timeout: int = 300,
                          check_interval: int = 5) -> Tuple[bool, Dict[str, Any]]:
        """
        等待任务完成

        Args:
            prompt_id: 任务ID
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）

        Returns:
            Tuple[bool, Dict]: (是否成功, 任务结果)
        """
        start_time = time.time()

        print(f"等待任务完成: {prompt_id}")

        while time.time() - start_time < timeout:
            status_info = self.check_task_status(prompt_id)

            if status_info['completed']:
                print(f"任务完成: {prompt_id}")
                self.completed_tasks[prompt_id] = status_info
                if prompt_id in self.active_tasks:
                    del self.active_tasks[prompt_id]
                return True, status_info

            print(f"任务状态: {status_info['status_str']}")
            time.sleep(check_interval)

        print(f"任务超时: {prompt_id}")
        return False, {}

    def download_images(self, prompt_id: str, output_dir: str) -> List[str]:
        """
        下载生成的图像

        Args:
            prompt_id: 任务ID
            output_dir: 输出目录

        Returns:
            List[str]: 下载的图像文件路径列表
        """
        downloaded_files = []

        try:
            # 确保输出目录存在
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # 获取任务状态和输出信息
            status_info = self.check_task_status(prompt_id)
            outputs = status_info.get('outputs', {})

            for node_id, node_output in outputs.items():
                if 'images' in node_output:
                    for image_info in node_output['images']:
                        filename = image_info.get('filename')
                        subfolder = image_info.get('subfolder', '')
                        type_info = image_info.get('type', 'output')

                        if filename:
                            # 构建下载URL
                            url_path = f"/view?filename={urllib.parse.quote(filename)}"
                            if subfolder:
                                url_path += f"&subfolder={urllib.parse.quote(subfolder)}"
                            url_path += f"&type={type_info}"

                            download_url = f"{self.base_url}{url_path}"

                            # 下载文件
                            output_path = os.path.join(output_dir, filename)
                            urllib.request.urlretrieve(download_url, output_path)
                            downloaded_files.append(output_path)
                            print(f"下载图像: {output_path}")

        except Exception as e:
            print(f"下载图像时出错: {e}")

        return downloaded_files

    def generate_images(self, workflow_path: str, param_modifications: Dict[str, Any],
                       output_dir: str, timeout: int = 300) -> Tuple[bool, List[str]]:
        """
        完整的图像生成流程：加载工作流、修改参数、提交任务、等待完成、下载图像

        Args:
            workflow_path: 工作流JSON文件路径
            param_modifications: 参数修改字典
            output_dir: 输出目录
            timeout: 超时时间（秒）

        Returns:
            Tuple[bool, List[str]]: (是否成功, 下载的图像文件路径列表)
        """
        print("开始图像生成流程...")

        # 1. 加载工作流
        workflow_data = self.load_workflow(workflow_path)
        if not workflow_data:
            return False, []

        # 2. 修改参数
        modified_workflow = self.modify_workflow_params(workflow_data, param_modifications)

        # 3. 提交任务
        prompt_id = self.submit_prompt(modified_workflow)
        if not prompt_id:
            return False, []

        # 4. 等待完成
        success, result = self.wait_for_completion(prompt_id, timeout)
        if not success:
            return False, []

        # 5. 下载图像
        downloaded_files = self.download_images(prompt_id, output_dir)

        print(f"图像生成完成，共生成 {len(downloaded_files)} 个文件")
        return True, downloaded_files

    def batch_generate(self, workflow_path: str, param_list: List[Dict[str, Any]],
                      output_dir: str, timeout: int = 300) -> List[Tuple[bool, List[str]]]:
        """
        批量生成图像

        Args:
            workflow_path: 工作流JSON文件路径
            param_list: 参数修改字典列表
            output_dir: 输出目录
            timeout: 每个任务的超时时间（秒）

        Returns:
            List[Tuple[bool, List[str]]]: 每个任务的结果列表
        """
        results = []

        print(f"开始批量生成，共 {len(param_list)} 个任务")

        for i, param_modifications in enumerate(param_list, 1):
            print(f"\n处理任务 {i}/{len(param_list)}")

            # 为每个任务创建子目录
            task_output_dir = os.path.join(output_dir, f"task_{i:03d}")

            success, files = self.generate_images(
                workflow_path, param_modifications, task_output_dir, timeout
            )
            results.append((success, files))

            if success:
                print(f"任务 {i} 完成，生成 {len(files)} 个文件")
            else:
                print(f"任务 {i} 失败")

        return results


def main():
    """示例用法"""
    # 创建客户端
    client = ComfyUIClient("127.0.0.1:8188")

    # 示例：单个图像生成
    workflow_path = "comfyui-workflows/default_workflow.json"
    param_modifications = {
        "6.text": "a beautiful landscape with mountains and lakes",
        "3.seed": 123456,
        "5.width": 768,
        "5.height": 512
    }
    output_dir = "generated_images"

    success, files = client.generate_images(workflow_path, param_modifications, output_dir)

    if success:
        print(f"生成成功，文件: {files}")
    else:
        print("生成失败")


if __name__ == "__main__":
    main()