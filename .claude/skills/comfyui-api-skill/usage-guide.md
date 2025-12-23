# ComfyUI API Skill 使用指南

## 快速开始

### 1. 环境准备

确保你已经安装了必要的依赖：

```bash
pip install websocket-client openpyxl
```

### 2. ComfyUI服务器准备

- 启动ComfyUI服务器，默认地址：`127.0.0.1:8188`
- 确保API访问已启用
- 准备好你的模型文件

### 3. 工作流准备

#### 方法一：使用提供的默认模板
运行脚本会自动创建 `default_workflow.json` 模板：

```python
from image_generator import NovelWebtoonImageGenerator
generator = NovelWebtoonImageGenerator()
generator.create_workflow_from_template("default_workflow")
```

#### 方法二：从ComfyUI导出API格式工作流
1. 在ComfyUI中设计你的工作流
2. 点击 "Save (API Format)" 保存为JSON
3. 将JSON文件复制到 `comfyui-workflows/` 目录

### 4. 基础使用

```python
from comfyui_client import ComfyUIClient

# 创建客户端
client = ComfyUIClient("127.0.0.1:8188")

# 生成单张图片
workflow_path = "comfyui-workflows/your_workflow.json"
param_modifications = {
    "6.text": "a beautiful landscape",  # 正向提示词
    "3.seed": 123456,                 # 种子
    "5.width": 768,                   # 宽度
    "5.height": 512                   # 高度
}
output_dir = "generated_images"

success, files = client.generate_images(workflow_path, param_modifications, output_dir)
```

## 集成到网文改编项目

### 从Excel批量生成图像

```python
from image_generator import NovelWebtoonImageGenerator

# 创建生成器
generator = NovelWebtoonImageGenerator()

# 从Excel文件批量生成
excel_path = "FullFlow-完整制作流程.xlsx"
results = generator.batch_generate_from_excel(excel_path)

print(f"成功生成: {results['successful_tasks']}")
print(f"失败数量: {results['failed_tasks']}")
print(f"生成文件: {len(results['generated_files'])}")
```

### 输出文件结构

生成的图像将按以下结构组织：

```
generated_images/
├── Episode_01/
│   ├── Shot_01/
│   │   ├── Episode-01-Shot-01-01.png
│   │   └── Episode-01-Shot-01-02.png
│   ├── Shot_02/
│   │   └── Episode-01-Shot-02-01.png
│   └── ...
├── Episode_02/
│   └── ...
```

## 工作流参数配置

### 常用节点类型和参数路径

| 参数类型 | 常见节点路径 | 说明 |
|---------|-------------|-----|
| 正向提示词 | `6.text`, `7.text` | CLIP Text Encode节点 |
| 负向提示词 | `11.text`, `12.text` | 负向提示词节点 |
| 种子 | `3.seed`, `4.seed` | KSampler节点 |
| 采样步数 | `3.steps` | 生成质量相关 |
| CFG值 | `3.cfg` | 提示词遵循度 |
| 图像尺寸 | `5.width`, `5.height` | Empty Latent Image节点 |

### 自动参数检测

使用WorkflowManager分析你的工作流：

```python
from workflow_manager import WorkflowManager

manager = WorkflowManager()
analysis = manager.analyze_workflow("your_workflow.json")

# 查看所有文本输入节点
for text_input in analysis['text_inputs']:
    print(f"文本参数: {text_input['path']} = {text_input['current_value']}")
```

## 高级功能

### 角色一致性

系统会自动为角色描述添加一致性提示：

```python
# 原始提示词
"叶凡站在山洞中，表情严肃"

# 自动增强后
"叶凡(融合吴彦祖的深邃眼神与胡歌的文雅气质，古装扮相英俊不凡)站在山洞中，表情严肃"
```

### 批量处理配置

在 `config.json` 中调整批量处理设置：

```json
{
  "batch_settings": {
    "max_concurrent": 1,        // 最大并发数
    "delay_between_tasks": 2,   // 任务间延迟(秒)
    "retry_attempts": 3,        // 重试次数
    "auto_retry_delay": 10      // 重试延迟(秒)
  }
}
```

### 创建自定义工作流模板

```python
from workflow_manager import WorkflowManager

manager = WorkflowManager()

# 分析现有工作流
template_file = manager.save_parameter_template("your_workflow.json")

# 使用模板生成参数
values = {
    'positive_prompt': 'ancient chinese palace',
    'seed': 12345,
    'steps': 25
}
modifications = manager.build_param_modifications(template_file, values)
```

## 故障排除

### 常见错误

1. **连接错误**: 检查ComfyUI服务器是否运行在指定端口
2. **工作流错误**: 验证JSON格式和节点依赖关系
3. **模型缺失**: 确认工作流中引用的模型文件存在
4. **内存不足**: 调整批次大小或图像尺寸

### 调试模式

在Python脚本中添加详细日志：

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# 然后运行你的代码
```

### 性能优化

1. **减少并发数**: 避免GPU内存溢出
2. **调整图像尺寸**: 较小尺寸生成更快
3. **使用缓存**: 相似提示词可以重用结果
4. **定期清理**: 删除临时文件释放空间

## 与主项目集成

### 在FullFlow流程中使用

可以在 `/fullflow` 命令的第6阶段集成：

```
阶段6：图像生成
- 读取完整制作流程Excel
- 调用comfyui-api-skill批量生成图像
- 更新Excel记录生成状态
- 创建图像文件索引
```

### 文件命名规范

生成的图像文件遵循项目命名规范：
`Episode-{集数:02d}-Shot-{镜头编号:02d}-{序号:02d}.png`

这样确保了图像文件与制作流程的完美对应和可追溯性。