# 执行完整的网文改编漫剧制作流程（**国风动漫版**），从小说章节到最终动漫风格图像和视频生成的全自动一条龙制作。

参数：章节范围（如：1-2, 3-4）

**重要更新：现在使用逐章处理模式，确保内容准确对应！**

## 执行方式

```bash
# 处理单个章节（推荐）
/fullflow-anime 1

# 处理多个章节（逐章处理）
/fullflow-anime 1-3
```

## 🚨🚨🚨 强制完整性规则 🚨🚨🚨

**绝对禁止的行为**：
1. ❌ **禁止复用已有文档**：不得复制或使用任何已有的剧本、提示词文件
2. ❌ **禁止弄虚作假**：不得说"生成关键部分并保存"、"生成示例"
3. ❌ **禁止偷懒捷径**：必须从小说原文重新完整生成
4. ❌ **禁止简化流程**：不得以任何理由简化、跳过、省略任何步骤

**必须遵守的标准**：
1. ✅ 逐章读取小说原文，确保内容准确
2. ✅ 每章独立处理，生成完整剧本
3. ✅ 基于剧本生成所有图像提示词
4. ✅ 生成所有图像和视频
5. ✅ 汇总到Excel文档

## 执行流程（新版本）

### 对于每个章节：

#### 1. 读取章节内容
- 从 `novel/chapter_XXX.txt` 读取小说原文
- 确保完整理解章节内容

#### 2. 生成剧本（使用 Skills）
- 调用 **webtoon-skill** 生成剧本
- 读取 adapt-method.md 获取改编方法
- 读取 output-style.md 掌握视觉化写作
- 读取 enhanced-script-method.md 应用专业技巧
- 使用V-符号系统（※△【】）
- 每章生成一个剧本文件

#### 3. 生成图像提示词（使用 Skills）
- 调用 **image-prompt-skill** 生成提示词
- **按顺序读取**：
  - anime-style-generation.md（核心规则）
  - enhanced-rules.md（场景模板、角色锁定表、风格锚定词库）
  - few-shot-examples.md（Few-Shot示例参考）
- 根据场景类型选择对应模板（对话/动作/环境/群像）
- 应用角色特征锁定表确保一致性
- 确保包含至少3个风格锚定词
- 输出JSON格式初稿：Episode-XX-Prompts.json

#### 3.5 验证提示词（使用验证脚本）【新增质量保障步骤】
- 运行 **prompt_validator.py** 自动验证
- 检查维度：
  - 六要素完整性（场景、角色、站位、光影、氛围、构图）
  - 角色绑定正确性（【图X参考】与角色列表匹配）
  - 参考图存在性（文件是否存在）
  - 风格锚定词（至少3个）
  - 质量约束词（画面干净、无畸形等）
  - 长度控制（140-260字符）
  - 格式正确性
  - 错误比喻检查
- 自动修复可修复的问题
- 生成验证报告：validation_report.md
- 输出修复后：Episode-XX-Prompts-fixed.json
- 如有无法自动修复的问题，调用 prompt-quality-agent 处理

#### 4. 生成图像（使用 Skills）
- 调用 **seedream-character-only skill**
- 使用 nano-banana-pro 引擎
- 基于提示词生成国风动漫风格图像
- 确保角色一致性

#### 5. 生成视频（使用 Skills）
- 调用 **video-generation-skill**
- 基于生成的图像创建视频
- 使用 Gemini Video API 或其他引擎

#### 6. 更新Excel（使用 Skills）
- 调用 **excel-generator-skill**
- 汇总所有生成的内容
- 生成完整制作文档

## 使用的 Skills

### 1. webtoon-skill
- **功能**：小说到剧本转换
- **读取文件**：
  - adapt-method.md（改编方法）
  - output-style.md（视觉化写作）
  - enhanced-script-method.md（专业技巧）
- **输出**：Episode-XX.md 剧本文件

### 2. image-prompt-skill
- **功能**：剧本到图像提示词转换（带质量保障）
- **读取文件**：
  - anime-style-generation.md（核心规则）
  - enhanced-rules.md（场景模板、角色锁定表、风格锚定词库）
  - few-shot-examples.md（Few-Shot示例参考）
- **验证脚本**：prompt_validator.py
- **输出**：
  - Episode-XX-Prompts.json（初稿）
  - Episode-XX-Prompts-fixed.json（修复后）
  - validation_report.md（验证报告）

### 2.5 prompt_validator（新增）
- **功能**：自动验证和修复提示词
- **检查维度**：8项（六要素、角色绑定、参考图、风格词、质量约束、长度、格式、比喻）
- **自动修复**：补充质量约束、补充风格锚定词
- **输出**：验证报告 + 修复后的JSON

### 2.6 prompt-quality-agent（新增）
- **功能**：处理验证脚本无法修复的复杂问题
- **调用时机**：验证报告显示需要人工处理时
- **处理内容**：语义理解、复杂角色关系、特殊场景氛围

### 3. seedream-character-only skill
- **功能**：生成角色一致性图像
- **引擎**：nano-banana-pro
- **输入**：Episode-XX-Prompts-fixed.json（使用修复后的提示词）
- **输出**：PNG图像文件

### 4. video-generation-skill
- **功能**：图像转视频
- **输出**：MP4视频文件

### 5. excel-generator-skill
- **功能**：数据汇总
- **输出**：Excel制作文档

## 输出结构

```
outputs/run_YYYYMMDD_HHMMSS_anime/
├── 00_info.json                    # 运行信息
├── 01_scripts/                     # 剧本文件
│   ├── Episode-01.md
│   ├── Episode-02.md
│   └── ...
├── 02_image_prompts/               # 图像提示词
│   ├── Episode-01-Prompts.json          # 初稿
│   ├── Episode-01-Prompts-fixed.json    # 修复后（用于图像生成）
│   ├── Episode-02-Prompts.json
│   ├── Episode-02-Prompts-fixed.json
│   └── ...
├── 02.5_validation/                # 【新增】验证报告
│   ├── validation_report.md             # 验证汇总报告
│   ├── Episode-01-validation.json       # 单集验证结果
│   └── fixed_prompts.json               # 自动修复的提示词
├── 03_generated_images/            # 生成的图像
│   ├── Episode-01/
│   │   ├── Episode-01-Shot-001.png
│   │   └── ...
│   └── Episode-02/
├── 04_video_prompts/               # 视频提示词
│   ├── Episode-01-Video-Prompts.txt
│   └── ...
├── 05_generated_videos/            # 生成的视频
│   ├── Episode-01/
│   │   └── Episode-01-Shot-001.mp4
│   └── ...
└── 06_final_excel/                 # 最终Excel
    └── Production-Data-YYYYMMDD_HHMMSS.xlsx
```

## 核心优势

1. **逐章处理**：避免上下文混乱，确保内容准确对应
2. **完整生成**：每个步骤都必须完整执行
3. **质量保障**：【新增】双重保障系统确保提示词质量
   - 生成阶段：场景模板 + 角色锁定表 + 风格锚定词库
   - 验证阶段：8维度自动检查 + 自动修复
4. **问题预防**：【新增】提前发现并修复问题，减少重新生成
5. **自动化**：一键处理多个章节
6. **技能驱动**：使用专业的 Skills 而非临时 Agent

## 质量保障指标【新增】

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 内容对应率 | ~70% | ~95% |
| 角色一致性 | ~60% | ~90% |
| 风格稳定性 | ~75% | ~95% |
| 重新生成率 | ~30% | ~5% |

## 使用示例

```bash
# 处理第1章
/fullflow-anime 1

# 处理第1-3章（自动逐章处理）
/fullflow-anime 1-3

# 处理第5-10章
/fullflow-anime 5-10
```

## 重要提醒

1. 每次处理都会创建新的时间戳目录
2. 所有内容都是全新生成，不会复用
3. 支持中断后继续（基于已有的输出目录）
4. 自动记录处理进度
5. 完全基于 Skills 系统，确保专业性
6. 【新增】提示词必须通过验证后才能生成图像
7. 【新增】验证报告会保存在 02.5_validation/ 目录
8. 【新增】如有需要人工处理的问题，会调用 prompt-quality-agent

## 常见问题【新增】

### Q: 验证步骤会拖慢执行速度吗？
A: 不会。验证脚本通常在几秒内完成，相比因质量问题重新生成图像节省的时间（每张图2-3分钟），验证大大提高了整体效率。

### Q: 自动修复能解决所有问题吗？
A: 不能。自动修复可以补充质量约束和风格锚定词，但六要素缺失、位置信息模糊等问题需要人工处理。遇到这类问题时会调用 prompt-quality-agent。

### Q: 如何判断提示词质量是否合格？
A: 查看验证报告中的"质量指标"：
- 内容对应率 ≥95%
- 角色一致性 ≥90%
- 风格稳定性 ≥95%
- 验证通过率 =100%

## 风格控制

- **国风动漫风格**：大眼睛、精致面容、8-9头身
- **角色一致性**：nano-banana-pro 引擎自动保证 + 角色特征锁定表辅助
- **画质标准**：高质量动漫插画，4K输出
- **画面要求**：干净，无水印，无畸形
- **风格锚定**：【新增】每条提示词至少包含3个风格锚定词

## 质量标准【新增】

### 提示词必须达到的标准
- 内容对应率：≥95%（与剧本描述一致）
- 角色一致性：≥90%（同一角色不同镜头外观统一）
- 风格稳定性：≥95%（国风动漫风格统一）
- 验证通过率：100%（所有提示词必须通过验证后才能生成图像）

### 质量保障措施
1. **生成阶段**：
   - 使用场景分类模板（对话/动作/环境/群像）
   - 应用角色特征锁定表
   - 确保包含风格锚定词
   - 参考Few-Shot优秀示例

2. **验证阶段**：
   - 自动检查8个维度
   - 自动修复可修复问题
   - 生成详细验证报告
   - 复杂问题人工处理

## 执行命令示例

执行时会自动调用相应的 Skills：
```bash
python scripts/fullflow_orchestrator_anime.py [章节范围]
```

这个脚本会：
1. 逐章调用 webtoon-skill 生成剧本
2. 调用 image-prompt-skill 生成提示词（使用增强规则 + Few-Shot示例）
3. 【新增】运行 prompt_validator.py 验证并自动修复提示词
4. 调用 seedream-character-only 生成图像（使用修复后的提示词）
5. 调用 video-generation-skill 生成视频
6. 调用 excel-generator-skill 汇总数据

确保每章内容都准确对应，所有步骤都完整执行。

## 独立使用验证脚本【新增】

如果你已经有提示词JSON文件，可以单独运行验证：

```bash
# 验证并自动修复
python .claude/skills/image-prompt-skill/prompt_validator.py <prompts.json> --fix

# 仅验证不修复
python .claude/skills/image-prompt-skill/prompt_validator.py <prompts.json>

# 指定输出目录
python .claude/skills/image-prompt-skill/prompt_validator.py <prompts.json> --fix --output-dir ./validation
```