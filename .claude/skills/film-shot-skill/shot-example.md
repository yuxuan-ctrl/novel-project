# 分镜示例参考

## 示例场景设定

**原始文本情况**：
- **scenes_raw**：山洞内，三名恶徒围困苏灵溪，她准备自爆。叶凡觉得吵闹，随手挥出清风，三人瞬间化为粒子消散。苏灵溪震惊地发现恶徒消失，向山洞深处行礼感谢。
- **direct_dialogues**：["圣女，你也不想...", "晚辈苏灵溪，多谢前辈出手相救。大恩大德，没齿难忘。"]

## 完整分镜示例

```json
[
  {
    "scene_id": "scene_001",
    "frame_type": "start",
    "place": "山洞入口处",
    "time": "白日，洞内昏暗",
    "characters": ["苏灵溪", "刀疤脸男子", "尖嘴猴腮男子", "第三个男子"],
    "action": "刀疤脸男子向前一步，脸上挂着令人作呕的笑容",
    "emotion": "威胁",
    "dialogues": ["圣女，你也不想..."],
    "narration": "三名恶徒将苏灵溪围困在山洞角落，恶意逼近",
    "camera": {
      "shot_type": "Medium Shot",
      "angle": "Eye-level",
      "movement": "Push in",
      "focus": "角色脸部"
    },
    "character_layout": "前景中央是刀疤脸男子，正面朝向镜头，恶笑表情；中景偏右是苏灵溪，背靠石壁，防御姿态；左右两侧是另外两名男子，呈包围态势",
    "background_pure": "山洞入口处的岩石洞壁，粗糙的石质纹理，昏暗的光线从洞外透入，洞壁上有自然的凹凸和裂缝，整体氛围阴暗压抑"
  },
  {
    "scene_id": "scene_001",
    "frame_type": "end",
    "place": "山洞入口处",
    "time": "白日，洞内昏暗",
    "characters": ["苏灵溪", "刀疤脸男子", "尖嘴猴腮男子", "第三个男子"],
    "action": "刀疤脸男子话音未落，突然停住，表情开始凝固",
    "emotion": "诡异",
    "dialogues": [],
    "narration": "清风从山洞深处拂过，恶徒们的笑容瞬间凝固",
    "camera": {
      "shot_type": "Medium Shot",
      "angle": "Eye-level",
      "movement": "Push in",
      "focus": "角色脸部"
    },
    "character_layout": "前景中央是刀疤脸男子，表情凝固，嘴巴半张；中景偏右是苏灵溪，紧张地看着变化；左右两侧的男子也开始呈现异样",
    "background_pure": "山洞入口处的岩石洞壁，粗糙的石质纹理，昏暗的光线从洞外透入，洞壁上有自然的凹凸和裂缝，整体氛围阴暗压抑"
  },
  {
    "scene_id": "scene_002",
    "frame_type": "start",
    "place": "山洞入口处",
    "time": "白日，洞内昏暗",
    "characters": ["苏灵溪"],
    "action": "三个男人的身体开始从头到脚化作微小粒子",
    "emotion": "震撼",
    "dialogues": [],
    "narration": "没有惨叫，没有血腥，恶徒们无声无息地消散",
    "camera": {
      "shot_type": "Wide Shot",
      "angle": "High-angle",
      "movement": "Static",
      "focus": "环境"
    },
    "character_layout": "中景中央是苏灵溪，震惊地看着眼前的景象；原本的三名男子正在化作粒子消散，身形变得透明虚幻",
    "background_pure": "山洞入口的宽阔空间，石质地面平整，洞壁高耸，深处延伸向黑暗，光线从洞口洒入形成明暗对比"
  },
  {
    "scene_id": "scene_002",
    "frame_type": "end",
    "place": "山洞入口处",
    "time": "白日，洞内昏暗",
    "characters": ["苏灵溪"],
    "action": "苏灵溪独自站立，环顾四周，山洞里空空荡荡",
    "emotion": "困惑",
    "dialogues": [],
    "narration": "仿佛恶徒们从未在这个世界上存在过",
    "camera": {
      "shot_type": "Wide Shot",
      "angle": "High-angle",
      "movement": "Static",
      "focus": "环境"
    },
    "character_layout": "中景中央是苏灵溪，孤独地站立在空旷的山洞中，身形显得渺小，周围再无其他人影",
    "background_pure": "山洞入口的宽阔空间，石质地面平整干净，洞壁高耸，深处延伸向黑暗，光线从洞口洒入形成明暗对比，整体显得空旷寂静"
  },
  {
    "scene_id": "scene_003",
    "frame_type": "start",
    "place": "山洞入口处",
    "time": "白日，洞内昏暗",
    "characters": ["苏灵溪"],
    "action": "苏灵溪强撑着摇摇欲坠的身体，朝着山洞深处弯腰准备行礼",
    "emotion": "感激",
    "dialogues": ["晚辈苏灵溪，多谢前辈出手相救。大恩大德，没齿难忘。"],
    "narration": "她意识到必定是绝世高人出手救了自己",
    "camera": {
      "shot_type": "Medium Shot",
      "angle": "3/4 view",
      "movement": "Static",
      "focus": "角色脸部"
    },
    "character_layout": "前景中央是苏灵溪，面向山洞深处，身体微微前倾准备行礼，表情恭敬而感激",
    "background_pure": "山洞从入口向深处延伸，石壁逐渐隐没在黑暗中，地面是天然的岩石，光线从浅入深逐渐减弱"
  },
  {
    "scene_id": "scene_003",
    "frame_type": "end",
    "place": "山洞入口处",
    "time": "白日，洞内昏暗",
    "characters": ["苏灵溪"],
    "action": "苏灵溪完成行礼，但身体因药性开始颤抖",
    "emotion": "虚弱",
    "dialogues": [],
    "narration": "体内的合欢散开始彻底爆发，热浪席卷全身",
    "camera": {
      "shot_type": "Medium Shot",
      "angle": "3/4 view",
      "movement": "Static",
      "focus": "角色脸部"
    },
    "character_layout": "前景中央是苏灵溪，刚完成行礼动作，但身体开始不自控地轻微颤抖，脸色开始泛红",
    "background_pure": "山洞从入口向深处延伸，石壁逐渐隐没在黑暗中，地面是天然的岩石，光线从浅入深逐渐减弱"
  }
]
```

## 示例分析

### 镜头拆分逻辑

#### Scene_001：威胁时刻
- **空间**：山洞入口处（不变）
- **时间**：白日，洞内昏暗（不变）
- **动作链**：恶徒威胁→话音停住
- **情绪变化**：威胁→诡异
- **镜头特点**：Medium Shot + Push in 突出紧张感

#### Scene_002：恶徒消散
- **空间**：山洞入口处（不变）
- **时间**：白日，洞内昏暗（不变）
- **动作链**：身体消散→完全消失
- **情绪变化**：震撼→困惑
- **镜头特点**：Wide Shot + High-angle 展现全貌

#### Scene_003：感谢行礼
- **空间**：山洞入口处（不变）
- **时间**：白日，洞内昏暗（不变）
- **动作链**：准备行礼→完成行礼
- **情绪变化**：感激→虚弱
- **镜头特点**：Medium Shot + 3/4 view 突出恭敬

### 优秀设计要点

#### 1. 空间时间一致性
- 所有镜头都在同一空间"山洞入口处"
- 时间保持"白日，洞内昏暗"不变
- 符合三不变原则

#### 2. 镜头类型选择恰当
- 威胁场面用Medium Shot突出对抗
- 消散场面用Wide Shot展现全貌
- 行礼场面用Medium Shot聚焦情感

#### 3. 摄影参数专业
- Push in增强紧张感
- High-angle体现震撼效果
- 3/4 view增加立体感

#### 4. 人物站位清晰
- 详细描述每个角色的位置关系
- 明确朝向和姿态
- 便于后续执行

#### 5. 背景描述独立
- background_pure完全不提人物
- 详细描述环境要素
- 可独立用于背景生成

#### 6. 对白使用准确
- 严格从direct_dialogues中选择
- 时间点匹配准确
- 无合适对白时使用空数组

#### 7. 情绪变化自然
- start到end的情绪变化合理
- 体现了情节的推进
- 符合剧情逻辑

### 常用组合模式

#### 紧张对峙场面
```
镜头类型：Medium Shot
角度：Eye-level
运动：Push in
焦点：角色脸部
情绪：威胁→紧张
```

#### 震撼揭示场面
```
镜头类型：Wide Shot
角度：High-angle
运动：Static
焦点：环境
情绪：震撼→困惑
```

#### 情感表达场面
```
镜头类型：Close-up
角度：3/4 view
运动：Static
焦点：角色脸部
情绪：感激→虚弱
```

这个示例展现了从威胁到解救再到感谢的完整情绪弧线，为分镜制作提供了专业的参考标准。