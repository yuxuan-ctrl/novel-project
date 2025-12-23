# Film Shot Skill Package

## 技能定义

电影分镜制作技能包，提供专业的漫剧到分镜转换能力。

## 调用时机

当需要进行以下任务时调用此技能：

### 漫剧分镜拆解
- 将漫剧剧本转换为电影镜头序列
- 分析※△【】格式的场景和动作
- 设计镜头转换逻辑

### 摄影参数设计
- 确定镜头类型和拍摄角度
- 设计摄像机运动轨迹
- 规划焦点和构图

### 关键帧制作
- 为每个镜头设计start/end双帧
- 描述人物站位和动作状态
- 提供背景环境描述

## 资源文件调用

### 基础分镜方法论
- `shot-breakdown-method.md` - 核心分镜拆解方法论
- `camera-techniques.md` - 专业摄影技巧指南
- `visual-storytelling.md` - 视觉叙事原理

### 模板和示例
- `shot-template.md` - 标准分镜JSON模板
- `shot-example.md` - 完整分镜示例参考
- `frame-design-guide.md` - 关键帧设计指南

### 质量标准
- `quality-criteria.md` - 分镜质量检查标准
- `technical-specs.md` - 技术规范要求

## 调用方式

```
调用 film-shot-skill 时需要读取：
1. shot-breakdown-method.md + shot-template.md + shot-example.md（分镜拆解阶段）
2. camera-techniques.md + visual-storytelling.md（摄影设计阶段）
3. frame-design-guide.md + quality-criteria.md（关键帧制作阶段）
```

## 输入输出规范

### 输入要求
- scenes_raw：连贯叙述文本
- direct_dialogues：原文对白列表

### 输出格式
- 标准JSON数组格式
- 每镜头包含start/end双帧
- 完整字段结构（scene_id, frame_type, place, time, characters, action, emotion, dialogues, narration, camera, character_layout, background_pure）

## 专业领域

### 电影制作
- 分镜设计原理
- 镜头语言运用
- 视觉叙事技巧

### 摄影技术
- 镜头选择策略
- 构图美学原理
- 光影设计思路

### 动画制作
- 关键帧设计
- 动作拆解方法
- 场景转换逻辑

此技能包适用于影视制作、动画创作、广告拍摄等需要专业分镜设计的场景。