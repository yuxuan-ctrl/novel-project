# video-prompt-skill

## 技能说明

这是图生视频（Image-to-Video）提示词生成的专业知识库，为 video-prompt-generator Agent 提供方法论支持。

## 技能文件结构

- `video-generation-method.md` - 核心方法论
- `video-prompt-template.md` - 标准模板
- `camera-movement-guide.md` - 相机运动设计
- `timing-control.md` - 时间轴控制技巧
- `i2v-tools-guide.md` - 主流工具适配指南

## 适用场景

- 静态图像转视频（Image-to-Video）
- 漫剧、动画分镜动态化
- 电影级视频特效预览
- 短视频内容生成

## 核心原则

1. **运动自然流畅** - 避免突兀、跳跃、不连贯
2. **角色一致性延续** - 沿用图像提示词的角色描述
3. **时间轴精确控制** - 分段描述动作和变化
4. **工具兼容性** - 适配RunwayML、Pika Labs、SVD

## 使用方式

Agent调用时需读取本目录下的所有方法论文件。
