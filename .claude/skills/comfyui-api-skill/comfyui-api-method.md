# ComfyUI API 调用方法论

## API调用流程

### 1. 工作流准备
- 在ComfyUI中设计并导出API格式的工作流JSON
- 将JSON文件保存到 `comfyui-workflows/` 目录
- 识别需要动态修改的节点和参数

### 2. 参数映射
- 分析工作流JSON结构，找到关键节点
- 映射文本提示词到对应的节点ID
- 配置种子、尺寸、采样步数等参数

### 3. API请求构建
```python
# 基础请求结构
{
    "prompt": workflow_json_data,
    "client_id": unique_client_id
}
```

### 4. 任务提交与监控
- 提交任务到ComfyUI API端点
- 获取prompt_id用于状态查询
- 通过WebSocket或轮询监控执行状态

### 5. 结果获取
- 监控任务完成状态
- 下载生成的图像文件
- 处理错误和异常情况

## 常用节点类型

### 文本提示词节点
```json
{
    "inputs": {
        "text": "your_prompt_here"
    },
    "class_type": "CLIPTextEncode"
}
```

### 采样器节点
```json
{
    "inputs": {
        "seed": 123456,
        "steps": 20,
        "cfg": 8.0,
        "sampler_name": "euler",
        "scheduler": "normal"
    },
    "class_type": "KSampler"
}
```

### 图像尺寸节点
```json
{
    "inputs": {
        "width": 512,
        "height": 768,
        "batch_size": 1
    },
    "class_type": "EmptyLatentImage"
}
```

## 错误处理策略

### 连接错误
- 检查ComfyUI服务器是否运行
- 验证服务器地址和端口
- 实施重试机制

### 工作流错误
- 验证JSON格式正确性
- 检查节点依赖关系
- 确认模型文件存在

### 参数错误
- 验证参数类型和范围
- 提供默认值后备方案
- 记录详细错误信息

## 性能优化

### 批量处理
- 合并多个提示词到单个请求
- 使用队列管理大批量任务
- 实施并发限制避免服务器过载

### 缓存策略
- 缓存相似的生成结果
- 重用相同参数的工作流
- 优化网络传输

### 资源管理
- 监控GPU内存使用
- 实施任务队列优先级
- 清理临时文件和缓存

## 集成指南

### 与Excel数据集成
- 读取Excel中的图像提示词
- 批量生成对应镜头的图像
- 更新Excel记录生成状态

### 文件命名规范
```
Episode-{集数}-Shot-{镜头编号}-{timestamp}.png
```

### 质量控制
- 设置生成参数的最佳实践
- 实施结果质量检查
- 提供重新生成机制

这个方法论确保了ComfyUI API调用的可靠性、效率和与项目工作流程的无缝集成。