# 分镜JSON模板规范

## 标准模板结构

### 完整JSON数组格式
```json
[
  {
    "scene_id": "scene_001",
    "frame_type": "start",
    "place": "具体地点描述，不跨空间",
    "time": "自然时间 + 环境氛围",
    "characters": ["画面中真实可见的人物列表"],
    "action": "这一帧的定格动作，动作起点",
    "emotion": "当前画面的主导情绪",
    "dialogues": ["从direct_dialogues中选择的对白，0-3句"],
    "narration": "从scenes_raw提取的叙述性文本，1-3句",
    "camera": {
      "shot_type": "镜头类型",
      "angle": "拍摄角度",
      "movement": "摄像机运动",
      "focus": "焦点位置"
    },
    "character_layout": "人物相对站位与远近关系描述",
    "background_pure": "纯环境描述，不提任何人物"
  },
  {
    "scene_id": "scene_001",
    "frame_type": "end",
    "place": "与start一致的地点描述",
    "time": "与start一致的时间描述",
    "characters": ["与start一致或自然变化的人物列表"],
    "action": "动作结束或情绪变化后的姿态",
    "emotion": "情绪的落点或变化结果",
    "dialogues": ["与时间点对应的对白"],
    "narration": "叙述的延续或结果",
    "camera": {
      "shot_type": "与start一致",
      "angle": "与start一致",
      "movement": "与start一致",
      "focus": "与start一致"
    },
    "character_layout": "与start一致或自然延续的站位",
    "background_pure": "与start一致的纯环境描述"
  }
]
```

## 字段填写规范

### scene_id
- **格式**：`"scene_001"`, `"scene_002"`, ...
- **规则**：同一镜头的start/end使用相同scene_id
- **编号**：从001开始，连续递增
- **注意**：不能跳号或重复

### frame_type
- **取值**：`"start"` 或 `"end"`
- **规则**：每个镜头必须有且仅有两帧
- **顺序**：start帧在前，end帧在后
- **作用**：标识关键帧的性质

### place
- **要求**：具体地点描述，不跨空间
- **示例**：
  - ✅ `"魏县城门外的青石广场"`
  - ✅ `"陈府正厅"`
  - ❌ `"从广场到大门"` (跨空间)
- **一致性**：同镜头start/end必须一致

### time
- **格式**：自然时间 + 环境氛围
- **示例**：
  - `"清晨，薄雾轻起"`
  - `"白日，阳光炽烈"`
  - `"夜晚，灯火昏黄"`
- **一致性**：同镜头start/end必须一致

### characters
- **类型**：字符串数组
- **内容**：画面中真实可见的人物
- **规则**：不写只在旁白里提到但画面看不到的人物
- **示例**：`["叶凡", "苏灵溪"]`

### action
- **start帧**：动作起点，准备阶段
- **end帧**：动作结束，情绪落点
- **语态**：使用现在时
- **长度**：一句话概括
- **示例**：
  - start: `"叶凡抬起右手，准备挥出"`
  - end: `"叶凡收回右手，目光平静"`

### emotion
- **格式**：中文短语
- **示例**：`"紧张"`, `"愤怒"`, `"落寞"`, `"温暖"`, `"屈辱"`, `"决心"`
- **变化**：end帧可以与start帧不同，体现情绪变化

### dialogues
- **来源**：严格从direct_dialogues中选择
- **数量**：0-3句对白
- **时间匹配**：对白时间点与镜头时间对应
- **空值**：无合适对白时使用`[]`

### narration
- **来源**：从scenes_raw提取
- **处理**：可略作改写，适合旁白
- **长度**：1-3句
- **风格**：叙述性，客观描述

### camera对象
```json
{
  "shot_type": "Medium Shot / Close-up / Wide Shot / Extreme Close-up / Full Shot / Over-the-Shoulder Shot",
  "angle": "Eye-level / Low-angle / High-angle / 3/4 view",
  "movement": "Push in / Pull back / Pan left / Pan right / Static / Tilt up / Tilt down / Track",
  "focus": "前景 / 中景 / 角色脸部 / 手部动作 / 环境"
}
```

#### shot_type可选值
- `"Wide Shot"` - 远景
- `"Full Shot"` - 全景
- `"Medium Shot"` - 中景
- `"Close-up"` - 特写
- `"Extreme Close-up"` - 大特写
- `"Over-the-Shoulder Shot"` - 过肩镜头

#### angle可选值
- `"Eye-level"` - 平视
- `"Low-angle"` - 仰角
- `"High-angle"` - 俯角
- `"3/4 view"` - 四分之三角度

#### movement可选值
- `"Static"` - 静止
- `"Push in"` - 推进
- `"Pull back"` - 拉远
- `"Pan left"` - 向左摇摆
- `"Pan right"` - 向右摇摆
- `"Tilt up"` - 向上倾斜
- `"Tilt down"` - 向下倾斜
- `"Track"` - 跟踪

#### focus可选值
- `"前景"` - 前景焦点
- `"中景"` - 中景焦点
- `"角色脸部"` - 角色脸部焦点
- `"手部动作"` - 手部动作焦点
- `"环境"` - 环境焦点

### character_layout
- **格式**：一句话描述
- **内容**：人物相对站位与远近关系
- **要素**：
  - 距离层次：前景/中景/远景
  - 水平位置：左/中/右
  - 朝向关系：面对/背对/侧身
  - 动作状态：站立/坐下/行走
- **示例**：
```
"前景偏左是李言初，低头站立，双手在身前；中景偏右是陈家三小姐，微微侧身看向他；远处虚化的人群构成背景。"
```

### background_pure
- **要求**：只描述环境，不提任何人物
- **内容**：
  - 地面材质
  - 主要建筑
  - 远景轮廓
  - 天空光线
  - 氛围特点
- **示例**：
```
"魏县城门外的宽阔青石广场，地面由大块青石铺就，远处是高耸的城门和连绵城墙，屋檐飞角层层叠叠，天空湛蓝，点缀几缕白云，整体光线明亮柔和。"
```

## 常见错误及避免

### JSON格式错误
- ❌ 忘记引号：`scene_id: scene_001`
- ✅ 正确格式：`"scene_id": "scene_001"`
- ❌ 多余逗号：`"focus": "环境",}`
- ✅ 正确格式：`"focus": "环境"}`

### 镜头逻辑错误
- ❌ 空间跳跃：start在"广场"，end在"房间"
- ✅ 空间一致：start和end都在"广场"
- ❌ 时间跳跃：start是"早晨"，end是"夜晚"
- ✅ 时间一致：start和end都是"早晨"

### 内容创造错误
- ❌ 自创对白：添加原文没有的对话
- ✅ 严格选择：只从direct_dialogues中选择
- ❌ 自创情节：添加原文没有的动作
- ✅ 忠实改编：基于scenes_raw进行描述

### 描述不准确
- ❌ 模糊描述：`"某个地方"`
- ✅ 具体描述：`"魏县城门外的青石广场"`
- ❌ 混合描述：background_pure中提到人物
- ✅ 纯净描述：background_pure只描述环境

这套模板确保了分镜数据的标准化和一致性，为后续制作提供了可靠的结构基础。