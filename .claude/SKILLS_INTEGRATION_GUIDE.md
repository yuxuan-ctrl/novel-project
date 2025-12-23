# Skills集成指南

## 集成说明

原有的Agents功能已经正确集成到现有的Skills中，避免了重复创建。

## 集成内容

### 1. 剧本生成功能

**原始Agent**：`script-creative-director.md`

**集成到**：`webtoon-skill`

**新增文件**：
- `webtoon-skill/enhanced-script-method.md` - 专业剧本创作方法
  - 三幕式结构强化
  - 视觉化升级技巧
  - 角色声音塑造
  - 节奏控制公式
  - 悬念设置专业方法

**使用方式**：
```python
# 调用webtoon-skill时，它会自动读取：
1. adapt-method.md - 基础改编方法
2. output-style.md - 视觉化写作规范
3. enhanced-script-method.md - 专业增强方法
4. script-template.md - 剧本模板
```

### 2. 图像提示词生成

**原始Agent**：`image-prompt-generator-anime.md`

**集成到**：`image-prompt-skill`

**新增文件**：
- `image-prompt-skill/anime-style-generation.md` - 动漫风格提示词方法
  - 国风动漫风格特征
  - 信息优先级规则
  - 六要素覆盖法
  - 特殊场景处理
  - JSON输出格式

**使用方式**：
```python
# 调用image-prompt-skill时，它会读取：
1. character-consistency-guide.md - 角色一致性
2. anime-style-generation.md - 动漫风格（新增）
3. prompt-generation-method.md - 基础方法
4. prompt-examples.md - 参考示例
```

## 处理流程更新

### 新的处理脚本

1. `process_chapter_with_skills.py` - 使用Skills的单章节处理脚本
2. `fullflow_orchestrator_anime.py` - 完整流程执行器

### 调用方式

```python
# 剧本生成
script = call_webtoon_skill_for_script(content, chapter_num, output_dir)

# 图像提示词生成
prompts = call_image_prompt_skill(script_path, chapter_num, output_dir)

# 图像生成
from seedream_character_only import generate_image_with_reference
result = generate_image_with_reference(
    prompt=prompt,
    character_name=character,
    engine='nano-banana-pro',
    style='anime'
)
```

## 优势

1. **避免重复**：不创建重复的Skill
2. **功能增强**：在现有Skill基础上增加专业方法
3. **保持兼容**：不影响现有功能
4. **易于维护**：集中管理相关功能

## 命令使用

```bash
# 使用新的处理方式
/python scripts/process_chapter_with_skills.py

# 或使用fullflow命令
/fullflow-anime 1-3
```

## 注意事项

1. 调用Skills时要确保读取正确的资源文件
2. 集成的方法不会覆盖原有功能，而是增强
3. 输出格式保持与原有系统一致
4. 新增的方法论文件可以在需要时扩展