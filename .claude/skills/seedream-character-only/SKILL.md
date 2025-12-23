# Seedream Character-Only Generation Skill

## 描述
使用豆包即梦 Seedream 4.5 的图生图功能，只基于人物三视图生成图像，不使用风格图。

## 功能特性
- 读取JSON格式的镜头配置
- 只使用人物三视图作为参考
- 保持角色形象完全一致
- 批量处理多个镜头

## 使用方法
```python
from seedream_character_only import CharacterOnlyGenerator

generator = CharacterOnlyGenerator()
generator.generate_from_json("shots_config.json")
```

## 核心特点
- 不使用风格图，避免风格干扰
- 专注于角色一致性
- 提示词强调保持人物特征