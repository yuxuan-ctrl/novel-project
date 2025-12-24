# 两阶段图像生成流程使用指南

## 📖 概述

这个脚本实现了**两阶段图像生成流程**，确保角色和场景的一致性：

### ✨ 优势

1. **角色一致性**：先生成角色参考图，后续所有镜头都使用相同参考
2. **场景一致性**：先生成场景参考图，确保环境统一
3. **图生图质量**：使用参考图生成的图像比纯文生图质量更高
4. **可复用性**：参考图可以在多个镜头中复用

---

## 🚀 使用方法

### 阶段1：生成参考图

生成3个角色参考图和7个场景参考图：

```bash
cd /Users/tt/Desktop/fork/novel-project/.claude/skills/seedream-character-only

python two_stage_generation.py --stage1
```

**会生成以下参考图**：

#### 角色参考图（3张）
- `linxuan.png` - 林渊（囚服状态）
- `linxuan_modern.png` - 林渊（现代状态）
- `huijue.png` - 青袍修士

#### 场景参考图（7张）
- `矿洞.png` - 陈塘关矿场
- `现代办公室.png` - 现代办公室
- `系统界面.png` - 封神榜系统界面
- `封神榜虚空.png` - 虚空中的封神榜
- `偏房.png` - 破旧偏房
- `命数轨迹.png` - 虚空命数轨迹
- `天空.png` - 阴沉天空

**预计耗时**：约10分钟（10张图 × 每张约1分钟）

**输出目录**：
```
.claude/skills/seedream-character-only/
├── character_images/    # 角色参考图
│   ├── linxuan.png
│   ├── linxuan_modern.png
│   └── huijue.png
└── scene_images/        # 场景参考图
    ├── 矿洞.png
    ├── 现代办公室.png
    ├── 系统界面.png
    ├── 封神榜虚空.png
    ├── 偏房.png
    ├── 命数轨迹.png
    └── 天空.png
```

---

### 阶段2：生成最终镜头

使用参考图生成第1集的24个镜头：

```bash
python two_stage_generation.py --stage2 \
  outputs/run_20251223_233308_anime/02.5_validation/fixed_prompts.json \
  outputs/run_20251223_233308_anime/03_generated_images/Episode-01
```

**会做什么**：
1. 读取提示词JSON文件
2. 为每个镜头匹配合适的角色和场景参考图
3. 使用图生图API生成最终镜头
4. 下载并保存生成的图像

**预计耗时**：约2分钟（24镜头 × 每3秒请求间隔）

**输出示例**：
```
outputs/run_20251223_233308_anime/03_generated_images/Episode-01/
├── Episode-01-shot_001.png
├── Episode-01-shot_002.png
├── Episode-01-shot_003.png
...
└── Episode-01-shot_024.png
```

---

## 📊 完整执行流程

### 方案A：仅生成第1集（推荐测试）

```bash
# 1. 进入脚本目录
cd /Users/tt/Desktop/fork/novel-project/.claude/skills/seedream-character-only

# 2. 阶段1：生成参考图（一次性）
python two_stage_generation.py --stage1

# 3. 阶段2：生成第1集镜头
python two_stage_generation.py --stage2 \
  outputs/run_20251223_233308_anime/02.5_validation/fixed_prompts.json \
  outputs/run_20251223_233308_anime/03_generated_images/Episode-01
```

### 方案B：生成所有3集

```bash
# 1. 进入脚本目录
cd /Users/tt/Desktop/fork/novel-project/.claude/skills/seedream-character-only

# 2. 阶段1：生成参考图（一次性，所有集共用）
python two_stage_generation.py --stage1

# 3. 阶段2：生成第1集镜头
python two_stage_generation.py --stage2 \
  outputs/run_20251223_233308_anime/02_image_prompts/Episode-01-Prompts.json \
  outputs/run_20251223_233308_anime/03_generated_images/Episode-01

# 4. 阶段2：生成第2集镜头
python two_stage_generation.py --stage2 \
  outputs/run_20251223_233308_anime/02_image_prompts/Episode-02-Prompts.json \
  outputs/run_20251223_233308_anime/03_generated_images/Episode-02

# 5. 阶段2：生成第3集镜头
python two_stage_generation.py --stage2 \
  outputs/run_20251223_233308_anime/02_image_prompts/Episode-03-Prompts.json \
  outputs/run_20251223_233308_anime/03_generated_images/Episode-03
```

**预计总耗时**：约20分钟
- 阶段1：10分钟（生成10张参考图）
- 阶段2：10分钟（生成44张镜头图）

---

## 🔍 工作原理

### 阶段1：文生图生成参考图

使用详细的提示词，通过文生图API生成高质量的角色和场景参考图。

**示例角色提示词**：
```
【角色：林渊】中国青年男性，约25岁，修仙者转凡人囚徒形象。
脸型瘦削，剑眉星目，鼻梁高挺，眼神坚毅锐利，嘴唇薄而坚定。
服装：破旧的灰色囚服，衣衫褴褛多处破损撕裂，身上有明显血迹斑斑，赤足。
神态：面容苍白虚弱，但眼神中透着不屈和战意。
国风动漫风格，大眼睛精致面容，8-9头身比例。
```

### 阶段2：图生图生成最终镜头

使用参考图作为输入，通过图生图API生成最终镜头。

**关键步骤**：
1. 收集镜头所需的角色参考图（如linxuan.png）
2. 收集镜头所需的场景参考图（如矿洞.png）
3. 将参考图编码为base64
4. 调用图生图API，传递提示词和参考图
5. API返回生成的图像URL
6. 下载并保存图像

**提示词增强**：
```
原始提示词 + "严格保持参考图中角色的面容特征、发型、服装完全一致，不要改变角色外观。"
```

---

## ⚠️ 注意事项

### API限制

1. **请求频率**：脚本已设置3秒间隔，避免请求过快
2. **API密钥**：使用的是 `ak-yXx1CsHzL3J6HRakOLPmSAXaDcnPDcAy`
3. **并发限制**：当前是串行生成，如需并行请自行修改

### 文件检查

1. **参考图已存在**：如果参考图已生成，会自动跳过
2. **参考图缺失**：阶段2会检查必要参考图，缺失则报错
3. **输出目录**：会自动创建不存在的目录

### 质量控制

1. **图生图参数**：使用 `doubao-seedream-4-5-251128` 模型
2. **图像尺寸**：
   - 参考图：1024x1024
   - 最终镜头：1024x576（16:9）
3. **水印**：已关闭水印 (`watermark: False`)

---

## 🛠️ 故障排除

### 问题1：API调用失败

**症状**：`API错误: 401 - Unauthorized`

**解决**：
- 检查API密钥是否正确
- 确认密钥未过期

### 问题2：参考图生成失败

**症状**：阶段1某些图像生成失败

**解决**：
- 检查网络连接
- 确认API配额充足
- 失败的参考图会显示`[FAIL]`，可重新运行阶段1

### 问题3：图生图质量不佳

**症状**：最终镜头中角色外观不一致

**解决**：
- 检查角色参考图是否生成成功
- 确认参考图质量良好
- 尝试调整提示词中的角色描述

---

## 📈 性能优化

### 批量生成

如需加快速度，可修改脚本实现并行生成：

```python
# 将串行改为并行（需自行实现）
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(generate, shot) for shot in shots]
```

### 缓存参考图

参考图生成后可永久保存，供后续所有剧集使用。

---

## 📝 日志和监控

脚本会输出详细日志：

```
[1/24] shot_001
  使用参考图: 2 张
  [OK] outputs/.../Episode-01-shot_001.png
```

根据日志可监控：
- 进度：当前处理第几个镜头
- 参考图：使用了哪些参考图
- 状态：成功或失败

---

## 🎯 总结

两阶段流程的核心优势：

✅ **一致性**：角色和场景外观统一
✅ **质量**：图生图比纯文生图质量更高
✅ **效率**：参考图可复用，节省时间
✅ **可控**：可以精调参考图来影响所有镜头

开始生成吧！🚀

---

*创建时间：2025-12-23*
*脚本位置：`.claude/skills/seedream-character-only/two_stage_generation.py`*
