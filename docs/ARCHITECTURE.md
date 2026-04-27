# 51Talk TP Generator — 架构文档

> 版本：v3.2 | 更新日期：2026-04-17

---

## 目录

1. [项目概述](#1-项目概述)
2. [文件结构](#2-文件结构)
3. [模块依赖图](#3-模块依赖图)
4. [完整工作流](#4-完整工作流)
5. [核心生成流程](#5-核心生成流程)
6. [QA 工作流](#6-qa-工作流)
7. [Prompt 体系](#7-prompt-体系)
8. [数据结构](#8-数据结构)
9. [防幻觉机制](#9-防幻觉机制)
10. [错误处理与重试策略](#10-错误处理与重试策略)
11. [配置说明](#11-配置说明)
12. [输出结构](#12-输出结构)
13. [依赖与环境](#13-依赖与环境)

---

## 1. 项目概述

本工具面向 51Talk 沙特成人市场，以 AI 驱动方式批量生成 ESL 口语课件包。

**输入**：CEFR 级别（A1–C1）+ 单元主题描述
**输出**：完整的 6–10 节课，每节课包含 JSON / HTML / PDF 三种格式

**教学背景约束**：
- 课堂形式：菲律宾外教 1 对 1 在线口语课
- 单课时长：25 分钟
- 目标学员：沙特成人，母语阿拉伯语
- 禁止内容：书面作业、group/partner 活动、中东文化红线内容

**中东内容合规（绝对红线）**：
- 非伊斯兰宗教、节日、符号
- 酒精、猪肉、赌博（哈拉姆内容）
- 恋爱/约会、LGBTQ、裸露
- 以色列相关、恐怖组织
- 魔法、星座、进化论、神秘主义

---

## 2. 文件结构

```
tp_generator/
│
├── 入口脚本
│   ├── main.py              # 交互式 CLI（单课模式 / Unit 模式）
│   └── auto_runner.py       # 全自动运行器（随机选题 + 全流程 + 自动QA）
│
├── 核心模块
│   ├── config.py            # 全局配置（API / 模型 / 主题色 / 路径）
│   ├── content_processor.py # AI 调用核心（Unit规划 / 大纲 / 幻灯片 / 润色）
│   ├── slide_renderer.py    # HTML 渲染（logo base64内嵌）+ Playwright PDF 导出
│   ├── utils.py             # 工具函数（重试 / 目录 / 单课生成管道）
│   └── qa_tester.py         # QA 模块（程序化校验 + AI评审 + Excel日志）
│
├── 51talklogo.png           # Logo 资源（渲染时 base64 内嵌到 HTML/PDF）
│
├── prompts/                 # 所有 Prompt 文件（外置，不硬编码在 Python 中）
│   ├── common_teacher_context.md   # 教师画像 + 各级别教学设计规则
│   ├── common_slide_templates.md   # 8种幻灯片的 JSON Schema 模板
│   ├── common_unit_prompts.md      # Unit 规划 System Prompt + 大纲生成指令 + 合规红线
│   ├── common_polish.md            # 单 slide 润色 Prompt 模板
│   ├── common_qa_prompts.md        # 大纲QA + 单课QA 评审 Prompt（含合规检查维度）
│   ├── {Level} Lesson Generator.md # 各级别幻灯片大纲生成 Prompt（×5）
│   ├── {Level} Content Polisher.md # 各级别润色 Prompt（历史遗留，已由 common_polish 替代）
│   └── {Level} PDF QA.md           # 各级别 QA Prompt（历史遗留，已由 common_qa_prompts 替代）
│
├── output/                  # 所有输出（不纳入版本控制）
│   ├── preview_final.html   # HTML/CSS/JS 模板（slide_renderer.py 的样式来源）
│   ├── qa_log.xlsx          # 所有运行的 QA 历史汇总
│   ├── _debug/              # AI 原始响应调试文件
│   └── Unit_{级别}_{时间戳}_{主题}/
│       ├── unit_outline.json
│       ├── L{N}_{课名}_{级别}.json / .html / .pdf
│       └── _qa/
│           ├── outline_qa_{时间戳}.txt
│           └── lesson_qa_L{N}_{时间戳}.txt
│
└── DOCS/                    # 文档
    ├── README.md
    ├── ARCHITECTURE.md      # 本文档
    ├── FLOWCHART.md
    └── CHANGELOG.md
```

---

## 3. 模块依赖图

依赖关系严格单向，无循环：

```
main.py / auto_runner.py
        │
        ▼
    utils.py
    generate_lesson()
        │
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
content_processor.py   slide_renderer.py        qa_tester.py
  generate_all_slides()   build_html()           test_outline()
  generate_outline()      export_pdf()           test_lessons()
  generate_slide_content()                       append_qa_log()
  polish_content()
  generate_unit_outline()
  chat_unit_planning()
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               ▼
                           config.py
                    (client / AI_MODEL / THEME / OUTPUT_DIR)
                               │
                               ▼
                          prompts/*.md
                    (运行时按需加载，模块级缓存)
```

**关键规则**：
- `config.py` 是唯一实例化 OpenAI client 的地方，其他模块共享该单例
- `utils.generate_lesson()` 是 `main.py` 和 `auto_runner.py` 共用的单课生成管道
- `qa_tester.py` 复用 `content_processor._load_section()` 加载 QA Prompt

---

## 4. 完整工作流

### 4.1 交互模式（main.py）

```
用户启动 python main.py
        │
        ├── [模式1] 单课生成
        │       └─ 用户输入级别 + Blueprint 文本
        │              → generate_all_slides() → polish → save JSON → HTML → PDF
        │
        └── [模式2] Unit 生成
                ├─ 用户输入级别 + 单元描述
                ├─ chat_unit_planning()        多轮对话，用户输入 "proceed" 结束
                ├─ generate_unit_outline()     AI 生成 6-10 节课大纲 JSON
                ├─ create_unit_dir()
                ├─ for each lesson: generate_lesson()
                └─ 询问是否运行 QA → test_outline() + test_lessons() + append_qa_log()
```

### 4.2 自动模式（auto_runner.py）

```
python auto_runner.py
        ├─ random.choice(LEVELS)
        ├─ random.choice(RANDOM_TOPICS)   75个主题覆盖沙特本地生活场景
        ├─ _auto_chat_unit_planning()     自动发送 "proceed"，无需人工介入
        ├─ generate_unit_outline()
        ├─ for each lesson: generate_lesson()
        └─ 自动运行 QA（无需确认）
```

---

## 5. 核心生成流程

### 5.1 单课生成管道

`utils.generate_lesson(level, lesson, outline, unit_dir)` — 整课最多重试 3 次：

```
[步骤 1/4]  generate_all_slides()   → slides: list[dict]（8个幻灯片对象）
[步骤 2/4]  polish_content()        → 并行润色，每 slide 独立 API 调用
[步骤 3/4]  保存 JSON
[步骤 4/4]  build_html() → export_pdf()
```

### 5.2 幻灯片大纲生成

`generate_outline(level, blueprint_str)` — 生成 8 个 slide 的结构清单：

1. 加载 `{level} Lesson Generator.md`，截断到 `# Action` 前
2. 提取 blueprint 中的词汇和功能语块
3. 将真实词汇预填入 JSON Schema（关键防幻觉步骤）
4. API 调用（最多 3 次 retry）
5. `_fix_outline_key_points()` 无条件覆盖 key_points

**词汇分配规则**：

| 词汇数量 | 分配方式 |
|---------|---------|
| ≤ 2 个词 | 只生成 useful_language_1 |
| 3–4 个词 | Part1: 前2个，Part2: 余下 |
| 5+ 个词 | 对半拆分 |

### 5.3 幻灯片内容生成

`generate_slide_content()` — 每个 slide 独立 API 调用：

- **title slide**：不调 API，100% 从 `bp_fields`（unit outline 权威数据）构建
- **其他 7 种**：注入 TEACHER_PROFILE_NOTE + LEVEL_DESIGN_RULES + 动态 LOCK 规则

**动态 LOCK 规则**：

| slide 类型 | 注入的 LOCK |
|-----------|------------|
| useful_language | VOCABULARY LOCK（精确词汇列表） |
| conversation_builder | FUNCTIONAL LANGUAGE LOCK |
| warm_up | WARM-UP TOPIC LOCK + 单问题规则 |
| scenario | SCENARIO TASK LOCK |
| wrap_up | WRAP-UP RECAP LOCK + FINAL TASK SCOPE LOCK |
| practice | PRACTICE TOPIC LOCK |

**词汇忠实度验证**（useful_language 类型）：
- 检测幻觉词 / 缺失词 → 加严 prompt 重试（最多 3 次）
- 3 次后仍违规 → Python force-inject（补入缺失词，删除幻觉词）

**并行策略**：`ThreadPoolExecutor(max_workers=3)` → 失败 slide 串行重试 → 关键模块缺失 raise RuntimeError

### 5.4 内容润色

`polish_content()` → `_polish_single_slide()` — 逐 slide 并行润色：
- 改善英文自然度，不改结构/词汇/类型
- type 字段变化时拒绝并保留原始内容

### 5.5 HTML 渲染与 PDF 导出

`build_html(slides)` — 根据 slide type 调用对应 render_*() 函数，拼装完整 HTML（含 CSS + JS + base64 logo）

`export_pdf()` — Playwright headless Chromium → `fitSlideBody()` JS 缩放 → 导出 1920×1080 PDF

---

## 6. QA 工作流

### 6.1 程序化校验层（无 API，毫秒级）

**大纲校验**：顶层字段完整性 + 每课字段完整性 + 书面作业红线

**单课校验**：
- 模块完整性：REQUIRED = {title, warm_up, useful_language_1+, conversation_builder, practice, scenario, wrap_up}；BANNED = {grammar_focus, speaking_chain, quick_check}
- 词汇忠实度：outline.vocabulary vs lesson words（检测缺失/幻觉）
- 句型忠实度：outline.functional_language vs conversation_builder linkers（宽松子串匹配）

### 6.2 AI 评审层（并行，3 课同时）

**大纲评审维度**（OUTLINE_QA_PROMPT）：
1. 纯口语任务导向
2. CEFR 级别匹配
3. 教师友好度与交际句型
4. 课程逻辑与连贯性
5. 字段与格式规范
6. **中东内容合规** ⚡ 致命红线（v3.2 新增）

**单课评审维度**（LESSON_QA_PROMPT）：
1. 大纲 100% 忠实度
2. 课堂容量与结构限制
3. CCQ 与互动质量
4. 交际语块设计
5. 级别匹配与教师友好度
6. **中东内容合规** ⚡ 致命红线（v3.2 新增）

**Pass 标准**：报告含 "🟢" 且含 "完美通过"

### 6.3 Excel 日志写入

`append_qa_log()` → `output/qa_log.xlsx` 追加一行，记录：序号、日期、工具版本、级别、主题、课包大小、大纲JSON、样课JSON、QA反馈、Pass/Fail

---

## 7. Prompt 体系

### 加载机制

```python
_load_common_file(filename)       # 读取整个 .md 文件，按文件名缓存
_load_section(filename, section)  # 按 "# SECTION_NAME" 标记切割
_load_slide_templates(filename)   # 按 "# slide_type" 标记切割为 dict
_load_level_design_rules(file)    # 解析 "LEVEL: rule" 格式为 dict
```

### 4 层约束架构

| 层级 | 文件 | 约束内容 |
|------|------|---------|
| 1. 单元系统 prompt | `common_unit_prompts.md` → UNIT_SYSTEM_PROMPT | 沙特背景、1对1限制、完整合规红线 |
| 2. 大纲生成规则 | `common_unit_prompts.md` → UNIT_OUTLINE_INSTRUCTION | 6模块结构、CEFR词汇校准、螺旋复现、最终课闭环 |
| 3. 幻灯片模板 | `common_slide_templates.md` | 每种 slide 的 JSON Schema + TITLE LOCK + CCQ RULE + TEACHER INSTRUCTIONS LOCK |
| 4. 运行时 LOCK | Python f-string 动态注入 | VOCABULARY LOCK / FUNCTIONAL LANGUAGE LOCK / WARM-UP TOPIC LOCK / SCENARIO TASK LOCK / WRAP-UP RECAP LOCK / PRACTICE TOPIC LOCK / FINAL TASK SCOPE LOCK |

---

## 8. 数据结构

### Unit Outline JSON

```json
{
  "level": "B2",
  "total_lessons": 6,
  "overarching_objective": "Student can confidently negotiate a salary with HR",
  "final_task": "Role-play: full salary negotiation with HR manager",
  "lessons": [
    {
      "lesson_number": 1,
      "lesson_name": "Understanding the Initial Offer",
      "objective": "Student can clarify and analyse a job offer",
      "vocabulary": ["remuneration", "base salary", "fringe benefits", "allowance", "comprehensive"],
      "functional_language": ["Could you clarify what is included in...", "Does this figure account for..."],
      "topic": "Saudi workplace — reviewing a job offer",
      "lesson_task": "Role-play: Student asks HR to clarify the offer; Tutor plays HR manager"
    }
  ]
}
```

### 单课 JSON（slides list）

```json
[
  {"type": "title", "unit": "...", "lesson": "Lesson 1: ...", "objective": "...", "emoji": "🎯"},
  {"type": "warm_up", "title": "Warm Up", "question": "...", "starters": ["..."]},
  {"type": "useful_language_1", "title": "Useful Language (Part 1)", "words": [
    {"word": "remuneration", "emoji": "💰", "definition": "...", "example": "...", "check": "...",
     "teacher_instructions": ["Say the word...", "Students repeat...", "Ask the check question...", "Ask for an example..."]}
  ]},
  {"type": "useful_language_2", "title": "Useful Language (Part 2)", "words": [...]},
  {"type": "conversation_builder", "title": "Conversation Builder", "focus": "...",
   "linkers": [{"word": "Could you clarify...", "use": "..."}],
   "model": [{"speaker": "Teacher", "line": "..."}, {"speaker": "Student", "line": "..."}],
   "your_turn": {"teacher": "...", "student": "..."}},
  {"type": "practice", "title": "Let's Practice", "teacher_question": "...", "student_guide": ["I think ___ is..."]},
  {"type": "scenario", "title": "Real-World Scenario", "role_a": "...", "role_b": "...",
   "problem": "...", "mission": ["..."], "start": "..."},
  {"type": "wrap_up", "title": "Wrap-Up", "recap": ["vocab: ...", "chunk: ..."], "final_task": "...", "challenge": "..."}
]
```

### 幻灯片模块一览

| 模块 | type | 是否关键 | 教学功能 |
|------|------|---------|---------|
| 封面页 | title | 否（Python直建）| 课名与目标展示 |
| 热身 | warm_up | ✅ | 话题导入 |
| 词汇 Part1 | useful_language_1 | ✅ | 核心词汇 + CCQ |
| 词汇 Part2 | useful_language_2 | 否（词少时省略）| 补充词汇 |
| 对话构建 | conversation_builder | ✅ | 功能句型操练 |
| 综合练习 | practice | ✅ | 半自由填空 |
| 真实情景 | scenario | ✅ | 完整 Role-play |
| 课堂总结 | wrap_up | ✅ | 词汇/句型复盘 |

---

## 9. 防幻觉机制

```
Layer 1: 单元级约束（UNIT_SYSTEM_PROMPT + UNIT_OUTLINE_INSTRUCTION）
  → 话题边界、词汇难度天花板、口语任务定义、合规红线

Layer 2: 课程级约束（Lesson Generator Prompt）
  → 幻灯片类型、结构、模块顺序

Layer 3: 幻灯片级约束（SLIDE_CONTENT_TEMPLATES + 动态 LOCK）
  → 每个 slide 的字段格式和内容约束

Layer 4: Python 代码级强制（generate_all_slides + 词汇校验 + force-inject）
  → 不依赖 AI，直接覆盖/注入正确数据
```

| 问题 | 解决方案 |
|------|---------|
| AI 在大纲里填错词汇 key_points | 生成 outline schema 时预填真实词汇（LOCKED） |
| AI 大纲 key_points 仍出错 | `_fix_outline_key_points()` 无条件覆盖 |
| useful_language slide 漏教词 | 3次 retry + force-inject |
| title slide 幻觉 | title 完全不调 API，从 unit outline 直接构建 |
| slide 标题被 AI 重命名 | 生成后遍历强制覆盖（TITLE_MAP） |
| 内容触碰合规红线 | 生成端 prompt 红线 + QA 端致命红线检查 |

---

## 10. 错误处理与重试策略

```
Level 1 — API 级（generate_slide_content）
  触发: JSONDecodeError / Exception（含429）/ VOCAB LOCK 违规
  策略: sleep(15×attempt)，最多 3 次

Level 2 — Slide 级（generate_all_slides）
  触发: 并行第一轮有 slide 返回 None
  策略: 串行重试，max_retries=3
  仍失败: 关键模块 → RuntimeError；非关键 → WARN 继续

Level 3 — 单课级（utils.generate_lesson）
  触发: RuntimeError from Level 2
  策略: 重走完整 4 步管道，最多 3 次

Level 4 — Unit 级（auto_runner）
  触发: 部分 lesson 失败
  策略: 继续生成剩余课，最后报告 success_count/total

Level 5 — QA 级（qa_tester.call_ai）
  触发: 429 限流
  策略: sleep(30×attempt)，最多 3 次
```

---

## 11. 配置说明

所有配置集中在 `config.py`：

| 配置项 | 说明 |
|--------|------|
| `AI_BASE_URL` | OpenAI 兼容代理地址 |
| `AI_MODEL` | 生成模型 |
| `AI_TEMPERATURE` | 1.0（生成）/ 0.7（规划）/ 0.3（润色+QA）|
| `OUTPUT_DIR` | 输出目录（相对于脚本所在目录）|
| `LEVELS` | `["A1","A2","B1","B2","C1"]` |
| `THEME` | 颜色/字体/字号 dict，驱动 slide_renderer.py 全部 CSS |

---

## 12. 输出结构

```
output/Unit_B2_0417_1559_Salary_Negotiation/
├── unit_outline.json
├── L1_Understanding_the_Initial_Offer_B2.json / .html / .pdf
├── L2_Preparing_Your_Value_Proposition_B2.json / .html / .pdf
│   ...
└── _qa/
    ├── outline_qa_0417_161018.txt
    ├── lesson_qa_L1_0417_161027.txt
    ├── lesson_qa_L2_0417_161046.txt
    └── lesson_qa_L5_0417_161041.txt
```

---

## 13. 依赖与环境

```bash
pip install openai playwright openpyxl
playwright install chromium
```

Python 3.10+（使用 `str | None` 联合类型语法）

| 命令 | 用途 |
|------|------|
| `python main.py` | 交互式，支持单课或 Unit 模式 |
| `python auto_runner.py` | 全自动，随机选题 + 完整生成 + QA |
| `python qa_tester.py [目录]` | 对已有 Unit 目录执行 QA |
