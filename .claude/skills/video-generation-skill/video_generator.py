#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
302.ai 视频生成核心模块
提供图生视频（Image-to-Video）的完整功能实现
"""

import base64
import http.client
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("[WARNING] OpenCV not installed. Video thumbnail extraction will be limited.")

# Make sure the ComfyUI API skill is available on sys.path
COMFY_SKILL_PATH = Path(__file__).resolve().parent.parent / "comfyui-api-skill"
if COMFY_SKILL_PATH.exists():
    sys.path.insert(0, str(COMFY_SKILL_PATH))

try:
    from comfyui_client import ComfyUIClient  # type: ignore
    COMFY_AVAILABLE = True
except Exception:
    ComfyUIClient = None  # type: ignore
    COMFY_AVAILABLE = False


# ============================================================================
# 图像处理模块
# ============================================================================

def image_to_base64(image_path: str) -> str:
    """
    将PNG图像转换为Base64编码字符串

    Args:
        image_path: 图像文件路径

    Returns:
        Base64编码的字符串

    Raises:
        FileNotFoundError: 文件不存在
        Exception: 读取或编码失败
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    file_size_mb = image_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 10:
        print(f"  [WARNING] Image size {file_size_mb:.2f}MB exceeds 10MB limit")

    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        raise Exception(f"Failed to encode image: {e}")


def extract_video_first_frame(video_path: str, output_path: str) -> bool:
    """
    使用OpenCV提取视频首帧作为封面图

    Args:
        video_path: 视频文件路径
        output_path: 输出封面图路径

    Returns:
        bool: 成功返回True，失败返回False
    """
    if not CV2_AVAILABLE:
        print(f"  [ERROR] OpenCV not available, cannot extract thumbnail")
        return False

    try:
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            print(f"  [ERROR] Cannot open video: {video_path}")
            return False

        # 读取第一帧
        ret, frame = cap.read()

        if ret and frame is not None:
            # 保存为PNG
            cv2.imwrite(str(output_path), frame)
            cap.release()
            return True
        else:
            print(f"  [ERROR] Cannot read first frame: {video_path}")
            cap.release()
            return False

    except Exception as e:
        print(f"  [ERROR] Failed to extract thumbnail: {e}")
        return False


# ============================================================================
# API客户端模块
# ============================================================================

class Video302AIClient:
    """302.ai 视频生成API客户端"""

    def __init__(self, api_key: str):
        """
        初始化API客户端

        Args:
            api_key: 302.ai API密钥（包含"Bearer "前缀）
        """
        self.api_key = api_key
        self.base_host = "api.302.ai"

    def submit_video_task(self, prompt: str, image_path: str,
                          resolution: str = "720P",
                          metadata: Optional[Dict[str, Any]] = None) -> Dict:
        """
        提交视频生成任务

        Args:
            prompt: 视频提示词（运动描述）
            image_path: 待转换图像路径
            resolution: 分辨率（720P或1080P）
            metadata: 额外上下文（未使用）

        Returns:
            dict: {'task_id': '...', 'task_status': 'PENDING', 'request_id': '...'}

        Raises:
            Exception: API调用失败
        """
        try:
            conn = http.client.HTTPSConnection(self.base_host, timeout=30)

            img_base64 = image_to_base64(image_path)

            payload = json.dumps({
                "model": "wan2.2-i2v-flash",
                "input": {
                    "prompt": prompt,
                    "img_url": f"data:image/png;base64,{img_base64}"
                },
                "parameters": {
                    "resolution": resolution,
                    "prompt_extend": True
                }
            })

            headers = {
                'Authorization': self.api_key,
                'Content-Type': 'application/json'
            }

            conn.request("POST",
                        "/aliyun/api/v1/services/aigc/video-generation/video-synthesis",
                        payload, headers)

            res = conn.getresponse()
            data = res.read()
            conn.close()

            response = json.loads(data.decode("utf-8"))

            # 检查响应格式
            if 'output' in response:
                return {
                    'task_id': response['output'].get('task_id'),
                    'task_status': response['output'].get('task_status'),
                    'request_id': response.get('request_id')
                }
            else:
                raise Exception(f"Unexpected API response: {response}")

        except Exception as e:
            raise Exception(f"Failed to submit video task: {e}")

    def query_task_status(self, task_id: str) -> Dict:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            dict: {
                'task_status': 'PENDING|RUNNING|SUCCESS|FAILED',
                'video_url': '...' (if SUCCESS),
                'submit_time': '...',
                'scheduled_time': '...'
            }

        Raises:
            Exception: API调用失败
        """
        try:
            conn = http.client.HTTPSConnection(self.base_host, timeout=30)

            headers = {
                'Authorization': self.api_key
            }

            conn.request("GET", f"/aliyun/api/v1/tasks/{task_id}", '', headers)

            res = conn.getresponse()
            data = res.read()
            conn.close()

            response = json.loads(data.decode("utf-8"))

            if 'output' in response:
                return response['output']
            else:
                raise Exception(f"Unexpected API response: {response}")

        except Exception as e:
            raise Exception(f"Failed to query task status: {e}")

    def download_video(self, video_url: str, save_path: str) -> str:
        """
        下载视频文件

        Args:
            video_url: 视频URL
            save_path: 保存路径

        Returns:
            str: 保存的文件路径

        Raises:
            Exception: 下载失败
        """
        try:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)

            urllib.request.urlretrieve(video_url, str(save_path))

            if save_path.exists():
                file_size_mb = save_path.stat().st_size / (1024 * 1024)
                print(f"    Downloaded: {save_path.name} ({file_size_mb:.2f}MB)")
                return str(save_path)
            else:
                raise Exception("File not created after download")

        except Exception as e:
            raise Exception(f"Failed to download video: {e}")


class ComfyUIVideoClient:
    """本地 ComfyUI 图生视频客户端"""

    supports_polling = False

    def __init__(self,
                 server_address: str = "127.0.0.1:8188",
                 workflow_path: str = "comfyui-workflows/wan2.2_generate_video.json",
                 input_dir: Optional[str] = None,
                 timeout: int = 1800):
        if not COMFY_AVAILABLE:
            raise ImportError("ComfyUI API skill not available")

        self.server_address = server_address
        self.workflow_path = Path(workflow_path)
        self.timeout = timeout
        self.client = ComfyUIClient(server_address)
        self.input_dir = Path(input_dir or os.getenv("COMFYUI_INPUT_DIR", "ComfyUI/input"))
        self.save_prefix_root = os.getenv("COMFYUI_VIDEO_PREFIX_ROOT", "video_outputs")
        self.load_image_node = os.getenv("COMFYUI_LOAD_IMAGE_NODE", "97")
        self.prompt_node = os.getenv("COMFYUI_PROMPT_NODE", "116:93")
        self.save_video_node = os.getenv("COMFYUI_SAVE_VIDEO_NODE", "108")

    def _prepare_input_image(self, image_path: str) -> str:
        """Copy image into ComfyUI input directory."""
        source_path = Path(image_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        self.input_dir.mkdir(parents=True, exist_ok=True)
        target_name = f"{source_path.stem}_{uuid.uuid4().hex[:6]}{source_path.suffix}"
        target_path = self.input_dir / target_name
        shutil.copy(source_path, target_path)
        return target_name

    def _download_outputs(self, prompt_id: str, target_dir: Path) -> List[Path]:
        """Download generated files from ComfyUI."""
        outputs = self.client.check_task_status(prompt_id).get('outputs', {})
        downloaded: List[Path] = []
        target_dir.mkdir(parents=True, exist_ok=True)

        for node_output in outputs.values():
            for field in ('video', 'videos', 'files'):
                file_entries = node_output.get(field)
                if not file_entries:
                    continue
                for file_info in file_entries:
                    filename = file_info.get('filename')
                    subfolder = file_info.get('subfolder', '')
                    type_info = file_info.get('type', 'output')
                    if not filename:
                        continue
                    url_path = f"/view?filename={urllib.parse.quote(filename)}"
                    if subfolder:
                        url_path += f"&subfolder={urllib.parse.quote(subfolder)}"
                    url_path += f"&type={type_info}"
                    dest_path = target_dir / Path(filename).name
                    urllib.request.urlretrieve(f"http://{self.server_address}{url_path}", dest_path)
                    downloaded.append(dest_path)
        return downloaded

    def submit_video_task(self, prompt: str, image_path: str,
                          resolution: str = "720P",
                          metadata: Optional[Dict[str, Any]] = None) -> Dict:
        metadata = metadata or {}
        if not self.workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {self.workflow_path}")

        comfy_image_name = self._prepare_input_image(image_path)
        task_key = metadata.get('task_key', Path(image_path).stem)
        video_output_path = Path(metadata.get('video_output_path',
                                              f"outputs/videos/{task_key}.mp4"))
        thumbnail_path = metadata.get('thumbnail_path')
        output_dir = video_output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        filename_prefix = str(Path(self.save_prefix_root) / f"{task_key}_{uuid.uuid4().hex[:4]}")
        param_modifications = {
            f"{self.load_image_node}.image": comfy_image_name,
            f"{self.prompt_node}.text": prompt,
            f"{self.save_video_node}.filename_prefix": filename_prefix
        }

        workflow_data = self.client.load_workflow(str(self.workflow_path))
        if not workflow_data:
            raise Exception("Failed to load ComfyUI workflow")
        modified_workflow = self.client.modify_workflow_params(workflow_data, param_modifications)

        prompt_id = self.client.submit_prompt(modified_workflow)
        if not prompt_id:
            raise Exception("Failed to submit ComfyUI prompt")

        success, _ = self.client.wait_for_completion(prompt_id, timeout=self.timeout)
        if not success:
            raise Exception("ComfyUI video generation timeout")

        downloaded_files = self._download_outputs(prompt_id, output_dir)
        mp4_files = [p for p in downloaded_files if p.suffix.lower() == '.mp4']
        if not mp4_files:
            raise Exception("No video file returned by ComfyUI")

        final_video_path = video_output_path
        if mp4_files[0] != final_video_path:
            shutil.move(mp4_files[0], final_video_path)

        extracted_thumbnail = None
        if thumbnail_path:
            thumbnail_path = Path(thumbnail_path)
            if extract_video_first_frame(str(final_video_path), str(thumbnail_path)):
                extracted_thumbnail = str(thumbnail_path)

        return {
            'task_id': prompt_id,
            'task_status': 'SUCCESS',
            'video_url': None,
            'video_path': str(final_video_path),
            'thumbnail_path': extracted_thumbnail
        }

    def query_task_status(self, task_id: str) -> Dict:
        """
        查询任务状态（ComfyUI不需要轮询，任务已同步完成）

        Args:
            task_id: 任务ID

        Returns:
            dict: 固定返回SUCCESS状态
        """
        # ComfyUI是同步的，submit时已经完成，无需查询
        return {
            'task_status': 'SUCCESS',
            'task_id': task_id
        }

    def download_video(self, video_url: str, save_path: str) -> str:
        """
        下载视频（ComfyUI不需要此方法，视频已在submit时保存）

        Args:
            video_url: 视频URL（未使用）
            save_path: 保存路径（未使用）

        Returns:
            str: 保存路径
        """
        # ComfyUI在submit时已经保存了视频，无需下载
        return save_path


# ============================================================================
# 任务管理模块
# ============================================================================

class VideoTaskManager:
    """视频生成任务状态管理器"""

    def __init__(self, run_dir: Path):
        """
        初始化任务管理器

        Args:
            run_dir: 运行目录（包含output_paths.json的目录）
        """
        self.run_dir = Path(run_dir)
        self.tasks_file = self.run_dir / "video_tasks.json"
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> Dict:
        """加载任务记录"""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load tasks file: {e}")
                return {}
        return {}

    def _save_tasks(self):
        """保存任务记录"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save tasks file: {e}")

    def save_task(self, task_key: str, task_id: str, image_path: str,
                  prompt: str, episode: int, shot_id: str):
        """
        保存新任务信息

        Args:
            task_key: 任务唯一键（如 "Episode-01-001"）
            task_id: API返回的任务ID
            image_path: 源图像路径
            prompt: 视频提示词
            episode: 集数
            shot_id: 镜头编号
        """
        self.tasks[task_key] = {
            'task_id': task_id,
            'status': 'PENDING',
            'episode': episode,
            'shot_id': shot_id,
            'image_path': image_path,
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'video_url': None,
            'video_path': None,
            'thumbnail_path': None,
            'submit_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'complete_time': None,
            'error_message': None
        }
        self._save_tasks()

    def update_task_status(self, task_key: str, status: str,
                          video_url: Optional[str] = None,
                          video_path: Optional[str] = None,
                          thumbnail_path: Optional[str] = None,
                          error_message: Optional[str] = None):
        """
        更新任务状态

        Args:
            task_key: 任务唯一键
            status: 新状态（SUCCESS, FAILED, RUNNING等）
            video_url: 视频URL（可选）
            video_path: 本地视频路径（可选）
            thumbnail_path: 封面图路径（可选）
            error_message: 错误信息（可选）
        """
        if task_key in self.tasks:
            self.tasks[task_key]['status'] = status

            if video_url:
                self.tasks[task_key]['video_url'] = video_url
            if video_path:
                self.tasks[task_key]['video_path'] = video_path
            if thumbnail_path:
                self.tasks[task_key]['thumbnail_path'] = thumbnail_path
            if error_message:
                self.tasks[task_key]['error_message'] = error_message

            if status in ['SUCCESS', 'FAILED']:
                self.tasks[task_key]['complete_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self._save_tasks()

    def get_task(self, task_key: str) -> Optional[Dict]:
        """获取任务信息"""
        return self.tasks.get(task_key)

    def get_all_tasks(self) -> Dict:
        """获取所有任务"""
        return self.tasks

    def get_pending_tasks(self) -> List[str]:
        """获取所有未完成的任务键"""
        return [key for key, task in self.tasks.items()
                if task['status'] not in ['SUCCESS', 'FAILED']]


# ============================================================================
# 批量处理模块
# ============================================================================

class VideoBatchProcessor:
    """视频批量处理器"""

    def __init__(self, api_client: Video302AIClient,
                 task_manager: VideoTaskManager):
        """
        初始化批量处理器

        Args:
            api_client: API客户端实例
            task_manager: 任务管理器实例
        """
        self.api_client = api_client
        self.task_manager = task_manager

    def parse_video_prompts(self, prompt_file: Path) -> Dict[str, str]:
        """
        解析视频提示词文件

        Args:
            prompt_file: 提示词文件路径

        Returns:
            dict: {shot_id: prompt}
        """
        prompts = {}

        if not prompt_file.exists():
            return prompts

        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '｜' in line:
                        # 格式: 001｜【基础画面】...
                        parts = line.split('｜', 1)
                        if len(parts) == 2:
                            shot_id = parts[0].strip()
                            prompt = parts[1].strip()
                            prompts[shot_id] = prompt
        except Exception as e:
            print(f"[ERROR] Failed to parse prompts file: {e}")

        return prompts

    def scan_episodes(self, run_dir: Path) -> List[Dict]:
        """
        扫描所有需要处理的Episode和镜头

        Args:
            run_dir: 运行目录

        Returns:
            list: [{'episode': 1, 'shot_id': '001', 'image_path': Path(...), 'prompt': '...', ...}]
        """
        images_dir = run_dir / '05_generated_images'
        prompts_dir = run_dir / '07_video_prompts'
        videos_dir = run_dir / '08_generated_videos'

        tasks_list = []

        # 遍历所有Episode目录
        for ep_dir in sorted(images_dir.glob('Episode-*')):
            ep_num_str = ep_dir.name.split('-')[1]
            ep_num = int(ep_num_str)

            print(f"\nScanning Episode {ep_num_str}...")

            # 读取视频提示词
            prompt_file = prompts_dir / f"Episode-{ep_num_str}-Video-Prompts.txt"
            prompts = self.parse_video_prompts(prompt_file)

            if not prompts:
                print(f"  [WARNING] No prompts found for Episode {ep_num_str}")
                continue

            # 遍历图像文件
            for img_file in sorted(ep_dir.glob('*.png')):
                # 提取shot_id (假设文件名格式: Episode-01-Shot-001.png)
                filename = img_file.stem  # Episode-01-Shot-001
                parts = filename.split('-')

                if len(parts) >= 4 and parts[2] == 'Shot':
                    shot_id = parts[3]  # 001

                    if shot_id in prompts:
                        video_output_dir = videos_dir / f"Episode-{ep_num_str}"
                        video_output_dir.mkdir(parents=True, exist_ok=True)

                        task_info = {
                            'episode': ep_num,
                            'shot_id': shot_id,
                            'task_key': f"Episode-{ep_num_str}-{shot_id}",
                            'image_path': img_file,
                            'prompt': prompts[shot_id],
                            'video_path': video_output_dir / f"Episode-{ep_num_str}-Shot-{shot_id}.mp4",
                            'thumbnail_path': video_output_dir / f"Episode-{ep_num_str}-Shot-{shot_id}-thumbnail.png"
                        }
                        tasks_list.append(task_info)

            print(f"  Found {len([t for t in tasks_list if t['episode'] == ep_num])} shots")

        return tasks_list

    def process_all_episodes(self, run_dir: Path) -> Dict:
        """
        处理所有Episode的视频生成（第1阶段：批量提交）

        Args:
            run_dir: 运行目录

        Returns:
            dict: {'total': int, 'submitted': int, 'skipped': int, 'failed': int}
        """
        print("\n" + "=" * 70)
        print("第1阶段：扫描镜头并批量提交视频生成任务")
        print("=" * 70)

        # 扫描所有任务
        tasks_list = self.scan_episodes(run_dir)
        print(f"\n共发现 {len(tasks_list)} 个镜头需要处理")

        stats = {'total': len(tasks_list), 'submitted': 0, 'skipped': 0, 'failed': 0}

        supports_polling = getattr(self.api_client, 'supports_polling', True)

        # 批量提交
        for task_info in tasks_list:
            task_key = task_info['task_key']
            print(f"\n处理 {task_key}...")

            # 检查是否已完成
            existing_task = self.task_manager.get_task(task_key)
            if existing_task and existing_task['status'] == 'SUCCESS':
                if task_info['video_path'].exists():
                    print(f"  [SKIP] 视频已存在")
                    stats['skipped'] += 1
                    continue

            # 提交新任务
            metadata = {
                'task_key': task_key,
                'video_output_path': str(task_info['video_path']),
                'thumbnail_path': str(task_info['thumbnail_path'])
            }

            try:
                # 提交API任务
                print(f"  提交视频生成任务...")
                result = self.api_client.submit_video_task(
                    prompt=task_info['prompt'],
                    image_path=str(task_info['image_path']),
                    resolution="720P",
                    metadata=metadata
                )

                # 保存任务记录
                self.task_manager.save_task(
                    task_key=task_key,
                    task_id=result['task_id'],
                    image_path=str(task_info['image_path']),
                    prompt=task_info['prompt'],
                    episode=task_info['episode'],
                    shot_id=task_info['shot_id']
                )

                print(f"  [SUCCESS] Task ID: {result['task_id'][:8]}...")
                if not supports_polling and result.get('task_status') == 'SUCCESS':
                    self.task_manager.update_task_status(
                        task_key=task_key,
                        status='SUCCESS',
                        video_url=result.get('video_url'),
                        video_path=result.get('video_path'),
                        thumbnail_path=result.get('thumbnail_path')
                    )
                stats['submitted'] += 1

            except Exception as e:
                print(f"  [FAILED] {e}")
                if metadata:
                    self.task_manager.update_task_status(
                        task_key=task_key,
                        status='FAILED',
                        error_message=str(e)
                    )
                stats['failed'] += 1

        return stats

    def wait_for_all_tasks(self, timeout: int = 7200, poll_interval: int = 10) -> Dict:
        """
        等待所有任务完成（第2阶段：轮询和下载）

        Args:
            timeout: 总超时时间（秒）
            poll_interval: 轮询间隔（秒）

        Returns:
            dict: {'total': int, 'success': int, 'failed': int, 'timeout': int}
        """
        print("\n" + "=" * 70)
        print("第2阶段：轮询任务状态并下载视频")
        print("=" * 70)

        start_time = time.time()
        all_tasks = self.task_manager.get_all_tasks()
        pending_keys = [key for key, task in all_tasks.items()
                       if task['status'] not in ['SUCCESS', 'FAILED']]

        if not pending_keys:
            print("\n[INFO] 没有待处理的任务")
            return {'total': 0, 'success': 0, 'failed': 0, 'timeout': 0}

        print(f"\n共有 {len(pending_keys)} 个任务需要等待完成")
        print(f"轮询间隔: {poll_interval}秒 | 总超时: {timeout}秒\n")

        while pending_keys and (time.time() - start_time) < timeout:
            # 轮询每个待处理任务
            for task_key in list(pending_keys):
                task_info = self.task_manager.get_task(task_key)
                task_id = task_info['task_id']

                try:
                    # 查询状态
                    status_data = self.api_client.query_task_status(task_id)
                    current_status = status_data['task_status']

                    if current_status in ['SUCCESS', 'SUCCEEDED']:
                        # 任务成功，下载视频
                        video_url = status_data.get('video_url')
                        if video_url:
                            print(f"\n[{task_key}] 生成成功，开始下载...")

                            # 获取保存路径
                            all_tasks_full = self.task_manager.get_all_tasks()
                            episode = all_tasks_full[task_key]['episode']
                            shot_id = all_tasks_full[task_key]['shot_id']

                            video_dir = self.task_manager.run_dir / '08_generated_videos' / f'Episode-{episode:02d}'
                            video_path = video_dir / f'Episode-{episode:02d}-Shot-{shot_id}.mp4'
                            thumbnail_path = video_dir / f'Episode-{episode:02d}-Shot-{shot_id}-thumbnail.png'

                            # 下载视频
                            self.api_client.download_video(video_url, str(video_path))

                            # 提取封面
                            print(f"    提取视频封面...")
                            if extract_video_first_frame(str(video_path), str(thumbnail_path)):
                                print(f"    封面提取成功: {thumbnail_path.name}")
                            else:
                                print(f"    [WARNING] 封面提取失败")

                            # 更新任务状态
                            self.task_manager.update_task_status(
                                task_key=task_key,
                                status='SUCCESS',
                                video_url=video_url,
                                video_path=str(video_path),
                                thumbnail_path=str(thumbnail_path) if thumbnail_path.exists() else None
                            )

                            pending_keys.remove(task_key)

                    elif current_status == 'FAILED':
                        # 任务失败
                        print(f"\n[{task_key}] 生成失败")
                        self.task_manager.update_task_status(
                            task_key=task_key,
                            status='FAILED',
                            error_message='Video generation failed'
                        )
                        pending_keys.remove(task_key)

                    # PENDING或RUNNING状态，继续等待

                except Exception as e:
                    print(f"\n[ERROR] {task_key}: {e}")

            # 显示进度
            elapsed = int(time.time() - start_time)
            completed = len(all_tasks) - len(pending_keys)
            progress_pct = (completed / len(all_tasks)) * 100 if len(all_tasks) > 0 else 0

            print(f"\r[{elapsed}s] 进度: {completed}/{len(all_tasks)} ({progress_pct:.1f}%) | 等待中: {len(pending_keys)}", end='', flush=True)

            # 等待下一轮轮询
            if pending_keys:
                time.sleep(poll_interval)

        # 统计结果
        print("\n")  # 换行
        final_tasks = self.task_manager.get_all_tasks()
        stats = {
            'total': len(final_tasks),
            'success': sum(1 for t in final_tasks.values() if t['status'] == 'SUCCESS'),
            'failed': sum(1 for t in final_tasks.values() if t['status'] == 'FAILED'),
            'timeout': len(pending_keys)
        }

        return stats


# ============================================================================
# 模块测试函数（可选）
# ============================================================================

if __name__ == '__main__':
    print("video_generator.py - 302.ai Video Generation Module")
    print("This module should be imported, not run directly.")
    print("\nAvailable classes:")
    print("  - Video302AIClient")
    print("  - VideoTaskManager")
    print("  - VideoBatchProcessor")
    print("\nAvailable functions:")
    print("  - image_to_base64()")
    print("  - extract_video_first_frame()")
