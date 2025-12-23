# Nano Banana 图生图技能

## 技能说明

这是一个基于 Gemini 2.5 Flash Image API 的图生图技能，用于生成保持角色一致性的漫剧场景图像。

## 核心特点

- **图生图模式**：基于角色形象图生成场景
- **角色一致性**：先生成角色基础形象，再用于所有场景
- **高质量输出**：使用 Gemini 2.5 Flash Image 模型
- **灵活切换**：可替代 ComfyUI，当用户明确要求时使用

## 工作流程

### 第一步：生成角色基础形象

为每个主要角色生成标准形象图：
- 猪八戒（净坛使者）
- 孙悟空（回忆中的齐天大圣）
- 斗战胜佛（佛化孙悟空）
- 其他主要角色

```bash
python generate_character_base.py
```

### 第二步：基于角色形象生成场景

使用角色形象图 + 场景描述生成最终场景图：

```bash
python generate_with_gemini.py --episode 01 --shot 001
```

## API 配置

- **API Key**: `ak-0BSEBCvgtNAA4qMcgzkYFQwvkoXorF8A`
- **Base URL**: `https://model-api.skyengine.com.cn/v1beta`
- **Model**: `gemini-2.5-flash-image:generateContent`

## 文件结构

```
.claude/skills/nano-banana-skill/
├── SKILL.md                      # 本文档
├── character-templates.md        # 角色模板定义
├── generate_character_base.py    # 生成角色基础形象
└── generate_with_gemini.py       # Gemini 图生图生成器
```

## 使用场景

### 默认使用 ComfyUI
大部分情况下使用 ComfyUI 批量生成

### 使用 Nano Banana 的情况
- 用户明确要求使用 nano banana 工具
- 需要更精细的角色一致性控制
- ComfyUI 不可用或效果不理想时

## 角色一致性策略

1. **角色库管理**：`character_images/` 目录存储所有角色基础形象
2. **场景生成**：读取对应角色形象 + 场景提示词
3. **API 调用**：将角色形象和场景描述发送给 Gemini
4. **质量保证**：Gemini 会基于角色形象保持一致性

## 命令示例

### 生成角色基础形象
```bash
python generate_character_base.py --character "猪八戒"
```

### 批量生成Episode场景
```bash
python generate_with_gemini.py --episode 01
```

### 单独生成某个镜头
```bash
python generate_with_gemini.py --episode 01 --shot 001 --character "猪八戒"
```

## 注意事项

- 确保先生成角色基础形象，再生成场景
- 角色形象图会被保存在 `character_images/` 目录
- 场景图会被保存在 `generated_images_gemini/` 目录
- API Key 已配置，直接使用即可
