# 视频生成方法论

## 概述

本文档描述使用302.ai API进行图生视频（Image-to-Video）的完整方法论，包括API调用流程、Base64编码处理、异步任务管理、错误处理和视频后处理。

## 核心原理

### Image-to-Video工作流程
1. **输入准备**：静态图像（PNG/JPG） + 文本提示词（运动描述）
2. **图像编码**：将图像转换为Base64字符串
3. **任务提交**：调用302.ai API提交视频生成任务
4. **异步处理**：API后台生成视频，返回task_id
5. **状态轮询**：定期查询任务状态（PENDING → RUNNING → SUCCESS/FAILED）
6. **视频下载**：任务成功后下载MP4文件
7. **封面提取**：提取视频首帧作为预览图

## 302.ai API调用规范

### API端点

**视频生成接口**
```
POST https://api.302.ai/aliyun/api/v1/services/aigc/video-generation/video-synthesis
```

**任务查询接口**
```
GET https://api.302.ai/aliyun/api/v1/tasks/{task_id}
```

### 请求格式

#### 提交视频生成任务
```json
{
  "model": "wan2.2-i2v-flash",
  "input": {
    "prompt": "运动描述文本",
    "img_url": "data:image/png;base64,{base64_string}"
  },
  "parameters": {
    "resolution": "720P",
    "prompt_extend": true
  }
}
```

**Headers**:
```
Authorization: Bearer {your_api_key}
Content-Type: application/json
```

#### 响应格式（提交成功）
```json
{
  "output": {
    "task_status": "PENDING",
    "task_id": "3b0d3b6a-b1c7-412d-9ad6-f35ad34cd1bc"
  },
  "request_id": "7738144b-c7c3-9d0f-b22d-a3dbb47cfec7"
}
```

#### 查询任务状态
```json
{
  "request_id": "a0e47a62-925a-9489-9d8a-83e86aecffdc",
  "output": {
    "task_id": "3b0d3b6a-b1c7-412d-9ad6-f35ad34cd1bc",
    "task_status": "SUCCESS",
    "video_url": "https://...",
    "submit_time": "2025-01-17 02:58:50.316",
    "scheduled_time": "2025-01-17 02:58:50.335"
  }
}
```

**任务状态**：
- `PENDING`：已提交，等待处理
- `RUNNING`：正在生成
- `SUCCESS`：生成成功，包含video_url
- `FAILED`：生成失败

## Base64图像编码

### 编码实现
```python
import base64
from pathlib import Path

def image_to_base64(image_path: str) -> str:
    """
    将图像文件转换为Base64编码字符串

    Args:
        image_path: 图像文件路径

    Returns:
        Base64编码的字符串
    """
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')
```

### 使用方式
```python
# 编码图像
img_base64 = image_to_base64('path/to/image.png')

# 构建img_url
img_url = f"data:image/png;base64,{img_base64}"
```

### 文件大小限制
- **最大文件大小**：10MB
- **支持格式**：JPEG, JPG, PNG, BMP, WEBP
- **处理策略**：超过10MB的图像需要压缩

### 图像压缩（可选）
```python
from PIL import Image
import io

def compress_image(image_path: str, max_size_mb: int = 10) -> bytes:
    """压缩图像以满足大小限制"""
    img = Image.open(image_path)

    # 转换为RGB（如果是RGBA）
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # 逐步降低质量直到文件小于限制
    for quality in range(95, 50, -5):
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
        size_mb = len(buffer.getvalue()) / (1024 * 1024)

        if size_mb <= max_size_mb:
            return buffer.getvalue()

    # 如果仍然过大，缩小图像尺寸
    img.thumbnail((img.width // 2, img.height // 2))
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()
```

## 异步任务管理

### 任务记录结构
使用JSON文件记录所有任务的状态：

```json
{
  "Episode-01-001": {
    "task_id": "3b0d3b6a-b1c7-412d-9ad6-f35ad34cd1bc",
    "status": "SUCCESS",
    "image_path": "05_generated_images/Episode-01/Episode-01-Shot-001.png",
    "prompt": "【基础画面】叶凡睁开眼睛...｜【相机运动】镜头推进...｜...",
    "video_url": "https://example.com/video.mp4",
    "video_path": "08_generated_videos/Episode-01/Episode-01-Shot-001.mp4",
    "thumbnail_path": "08_generated_videos/Episode-01/Episode-01-Shot-001-thumbnail.png",
    "submit_time": "2025-01-17 10:30:15",
    "complete_time": "2025-01-17 10:32:45",
    "error_message": null
  }
}
```

### 任务状态机
```
[未提交] → submit_video_task() → [PENDING]
                                        ↓
                               wait_for_completion()
                                        ↓
                                   [RUNNING]
                                   ↙     ↘
                            [SUCCESS]  [FAILED]
                                ↓          ↓
                        download_video()  记录错误
                                ↓
                        extract_thumbnail()
                                ↓
                            [COMPLETED]
```

### 轮询策略
```python
def poll_task_status(task_id: str, max_wait: int = 7200, interval: int = 10):
    """
    轮询任务状态直到完成或超时

    Args:
        task_id: 任务ID
        max_wait: 最大等待时间（秒）
        interval: 轮询间隔（秒）
    """
    start_time = time.time()

    while time.time() - start_time < max_wait:
        status_data = query_task_status(task_id)
        status = status_data['output']['task_status']

        if status == 'SUCCESS':
            return status_data
        elif status == 'FAILED':
            raise Exception(f"Task {task_id} failed")

        # PENDING或RUNNING，继续等待
        time.sleep(interval)

    raise TimeoutError(f"Task {task_id} timeout after {max_wait} seconds")
```

## 批量处理策略

### 处理流程
1. **扫描输入目录**：查找所有需要处理的图像文件
2. **读取提示词**：从视频提示词文件中匹配对应的提示词
3. **批量提交**：一次性提交所有任务，获取所有task_id
4. **并行轮询**：同时监控所有任务的状态
5. **增量下载**：任务完成立即下载，不等待所有任务完成
6. **统计报告**：实时显示进度和完成统计

### 目录扫描
```python
def scan_images_and_prompts(run_dir: Path):
    """
    扫描图像和提示词文件

    Returns:
        List[dict]: [
            {
                'episode': 1,
                'shot_id': '001',
                'image_path': Path(...),
                'prompt': '...',
                'video_output_dir': Path(...)
            }
        ]
    """
    images_dir = run_dir / '05_generated_images'
    prompts_dir = run_dir / '07_video_prompts'

    tasks = []

    # 遍历所有Episode目录
    for ep_dir in sorted(images_dir.glob('Episode-*')):
        ep_num = int(ep_dir.name.split('-')[1])

        # 读取该集的视频提示词
        prompt_file = prompts_dir / f"Episode-{ep_num:02d}-Video-Prompts.txt"
        prompts = parse_video_prompts(prompt_file)

        # 遍历所有图像文件
        for img_file in sorted(ep_dir.glob('Episode-*-Shot-*.png')):
            shot_id = extract_shot_id(img_file.name)

            if shot_id in prompts:
                tasks.append({
                    'episode': ep_num,
                    'shot_id': shot_id,
                    'image_path': img_file,
                    'prompt': prompts[shot_id],
                    'video_output_dir': run_dir / '08_generated_videos' / f'Episode-{ep_num:02d}'
                })

    return tasks
```

### 进度监控
```python
def monitor_progress(tasks_status: dict):
    """
    实时显示任务进度

    Args:
        tasks_status: {task_key: {'status': '...', ...}}
    """
    total = len(tasks_status)
    completed = sum(1 for t in tasks_status.values() if t['status'] in ['SUCCESS', 'FAILED'])
    success = sum(1 for t in tasks_status.values() if t['status'] == 'SUCCESS')
    failed = sum(1 for t in tasks_status.values() if t['status'] == 'FAILED')

    progress_pct = (completed / total) * 100 if total > 0 else 0

    print(f"[{time.strftime('%H:%M:%S')}] 进度: {completed}/{total} ({progress_pct:.1f}%)")
    print(f"  成功: {success} | 失败: {failed} | 进行中: {total - completed}")
```

## 错误处理和重试

### 常见错误类型
1. **网络错误**：连接超时、请求失败
2. **API错误**：密钥无效、配额不足、参数错误
3. **文件错误**：图像文件不存在、文件过大
4. **任务失败**：API返回FAILED状态
5. **超时错误**：任务等待时间过长

### 错误处理策略
```python
def submit_with_retry(api_client, prompt, img_base64, max_retries=3):
    """
    带重试的任务提交
    """
    for attempt in range(max_retries):
        try:
            result = api_client.submit_video_task(prompt, img_base64)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"  提交失败，{wait_time}秒后重试... ({attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"  提交失败，已达到最大重试次数: {e}")
                raise
```

### 断点续传
检查已完成的任务，跳过重复处理：
```python
def should_skip_task(task_key: str, video_output_path: Path, tasks_record: dict):
    """
    判断任务是否应该跳过

    Returns:
        bool: True表示跳过，False表示需要处理
    """
    # 1. 检查视频文件是否已存在
    if video_output_path.exists():
        return True

    # 2. 检查任务记录中是否已成功
    if task_key in tasks_record:
        status = tasks_record[task_key].get('status')
        if status == 'SUCCESS':
            return True

    return False
```

## 视频后处理

### 视频首帧提取
使用OpenCV提取视频的第一帧作为封面图：

```python
import cv2
from pathlib import Path

def extract_video_first_frame(video_path: str, output_path: str) -> bool:
    """
    提取视频首帧并保存为PNG图像

    Args:
        video_path: 视频文件路径
        output_path: 输出封面图路径

    Returns:
        bool: 成功返回True，失败返回False
    """
    try:
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            print(f"  [ERROR] 无法打开视频: {video_path}")
            return False

        # 读取第一帧
        ret, frame = cap.read()

        if ret and frame is not None:
            # 保存为PNG
            cv2.imwrite(str(output_path), frame)
            cap.release()
            return True
        else:
            print(f"  [ERROR] 无法读取视频首帧: {video_path}")
            cap.release()
            return False

    except Exception as e:
        print(f"  [ERROR] 提取视频首帧失败: {e}")
        return False
```

### 备用提取方法（使用PIL）
```python
from PIL import Image
import subprocess

def extract_first_frame_with_pillow(video_path: str, output_path: str):
    """使用PIL作为备用方法"""
    try:
        # 使用ffmpeg提取首帧
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vframes', '1',
            '-f', 'image2',
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"  [ERROR] PIL提取失败: {e}")
        return False
```

### 封面图优化
```python
def optimize_thumbnail(thumbnail_path: str, target_width: int = 150):
    """
    优化封面图大小以减少Excel文件体积

    Args:
        thumbnail_path: 封面图路径
        target_width: 目标宽度（像素）
    """
    try:
        from PIL import Image

        img = Image.open(thumbnail_path)

        # 计算等比例高度
        aspect_ratio = img.height / img.width
        target_height = int(target_width * aspect_ratio)

        # 调整大小
        img_resized = img.resize((target_width, target_height), Image.LANCZOS)

        # 保存（覆盖原文件）
        img_resized.save(thumbnail_path, 'PNG', optimize=True)

    except Exception as e:
        print(f"  [WARNING] 封面图优化失败: {e}")
```

## 性能优化

### 并发控制
虽然采用一次性提交策略，但下载阶段可以并发：

```python
from concurrent.futures import ThreadPoolExecutor

def download_videos_concurrently(completed_tasks: list, max_workers: int = 5):
    """
    并发下载多个视频

    Args:
        completed_tasks: 已完成的任务列表
        max_workers: 最大并发数
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for task in completed_tasks:
            future = executor.submit(
                download_and_extract,
                task['video_url'],
                task['video_path'],
                task['thumbnail_path']
            )
            futures.append(future)

        # 等待所有下载完成
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"  [ERROR] 下载失败: {e}")
```

### 缓存策略
缓存Base64编码的图像，避免重复编码：

```python
_image_cache = {}

def get_cached_base64(image_path: str) -> str:
    """
    获取缓存的Base64编码，如果不存在则编码并缓存
    """
    if image_path not in _image_cache:
        _image_cache[image_path] = image_to_base64(image_path)
    return _image_cache[image_path]
```

## 最佳实践

### 1. 提示词优化
- 确保提示词描述清晰、具体
- 包含运动方向、速度、时长信息
- 避免过于复杂的多重运动描述

### 2. 图像质量控制
- 使用高质量的静态图像（至少768x768）
- 确保图像主体清晰、无模糊
- 避免过暗或过亮的图像

### 3. 批量处理建议
- 合理设置轮询间隔（推荐10-15秒）
- 监控API响应速度，调整策略
- 记录详细日志供后续分析

### 4. 文件组织
- 使用统一的命名规范
- 保持目录结构清晰
- 及时清理失败的临时文件

### 5. 错误恢复
- 失败任务单独记录，便于批量重试
- 保留原始提示词和图像，支持手动重新生成
- 定期备份tasks.json文件

## 故障排查

### 问题1：API密钥无效
**现象**：返回401或403错误
**解决**：
- 检查环境变量 `VIDEO_302AI_API_KEY` 是否正确设置
- 确认密钥包含 "Bearer " 前缀
- 验证密钥未过期

### 问题2：图像过大无法提交
**现象**：提交失败或返回400错误
**解决**：
- 检查图像文件大小
- 使用图像压缩功能
- 调整图像分辨率

### 问题3：任务一直PENDING
**现象**：长时间停留在PENDING状态
**解决**：
- 检查API服务状态
- 确认账户配额充足
- 增加轮询超时时间

### 问题4：视频下载失败
**现象**：video_url无法访问
**解决**：
- 检查网络连接
- 验证URL是否过期
- 尝试重新提交任务

### 问题5：封面提取失败
**现象**：OpenCV无法读取视频
**解决**：
- 检查OpenCV版本
- 尝试备用提取方法（ffmpeg）
- 验证视频文件完整性

这份方法论文档提供了完整的技术指导，确保视频生成流程稳定、可靠、高效。
