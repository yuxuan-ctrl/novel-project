# 命令名称：/chapter-flow

# 功能描述
逐章处理小说生成漫剧内容，简化流程，一次只处理一个章节，确保内容准确对应。

# 参数
- chapters: 章节号（单个或范围，如：1 或 1-3）
- style: 风格（anime/realistic，默认anime）

# 使用示例
```bash
# 处理第1章
/chapter-flow 1

# 处理第1-3章
/chapter-flow 1-3

# 处理第5章，半写实风格
/chapter-flow 5 --style realistic
```

# 执行步骤
1. 读取指定章节的小说内容
2. 基于章节内容生成剧本
3. 基于剧本生成图像提示词
4. 生成图像
5. 生成视频
6. 更新Excel汇总

# 输出结构
```
outputs/run_YYYYMMDD_HHMMSS_anime/
├── 01_scripts/
│   └── Episode-XX.md
├── 02_image_prompts/
│   └── Episode-XX-Prompts.json
├── 03_generated_images/
│   └── Episode-XX/
├── 04_video_prompts/
│   └── Episode-XX-Video-Prompts.txt
├── 05_generated_videos/
│   └── Episode-XX/
└── 06_final_excel/
    └── Production-Data.xlsx
```

# 核心优势
- 逐章处理，内容准确对应
- 简化流程，避免上下文混乱
- 支持单章或多章批量处理
- 自动生成完整制作文档