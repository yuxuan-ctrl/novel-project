# ComfyUI API Skill Package

## 技能定义

ComfyUI API调用技能包，专门用于通过API接口调用ComfyUI生成图像。支持加载JSON工作流文件，修改参数，提交任务并监控执行状态。

## 调用时机

当需要进行以下任务时调用此技能：

### 图像生成任务
- 基于文本提示词生成图像
- 使用预定义的ComfyUI工作流
- 批量图像生成
- 自定义工作流参数调整

### API集成任务
- 将网文改编项目的图像提示词转换为实际图像
- 集成到完整的制作流程中
- 自动化图像生成管道

### 工作流管理
- 管理多个ComfyUI工作流JSON文件
- 动态修改工作流参数
- 监控任务执行状态

## 资源文件调用

### 核心API方法
- `comfyui-api-method.md` - ComfyUI API调用核心方法论
- `workflow-management.md` - 工作流文件管理规范
- `parameter-mapping.md` - 参数映射和配置指南

### Python实现
- `comfyui_client.py` - 主要的API调用客户端
- `workflow_manager.py` - 工作流文件管理工具
- `image_generator.py` - 图像生成封装工具

### 配置文件
- `config.json` - API服务器配置
- `default_params.json` - 默认参数配置

## 调用方式

```
调用 comfyui-api-skill 时需要读取：
1. comfyui-api-method.md（了解API调用方法）
2. comfyui_client.py（执行API调用）
3. workflow_manager.py（管理工作流文件）
4. comfyui-workflows/目录下的JSON工作流文件
```

## 输入要求
- ComfyUI服务器地址和端口
- 工作流JSON文件路径
- 需要修改的参数（提示词、种子、尺寸等）
- 输出图像保存路径

## 输出格式
- 生成的图像文件（PNG/JPG格式）
- 任务执行状态和结果信息
- 错误日志和调试信息

## 专业能力

### API集成
- HTTP请求处理和错误管理
- JSON数据解析和修改
- 异步任务监控和状态查询
- 文件上传和下载处理

### 工作流管理
- JSON工作流文件的加载和验证
- 动态参数替换和配置
- 工作流模板管理
- 批量处理支持

### 图像处理
- 支持多种图像格式输出
- 图像质量和参数优化
- 批量图像生成管理
- 结果文件组织和命名

## 使用场景

### 网文改编项目集成
- 将Excel表格中的图像提示词批量生成为实际图像
- 为每个镜头生成对应的视觉内容
- 保持角色外观的一致性

### 工作流自动化
- 定时批量图像生成
- 参数化图像生成管道
- 质量控制和结果验证

此技能包专注于将ComfyUI的强大图像生成能力集成到网文改编项目的完整制作流程中。