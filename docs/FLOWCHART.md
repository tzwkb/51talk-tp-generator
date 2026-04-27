# 程序流程图

> 版本：v3.2 | 更新日期：2026-04-17

---

## 入口：两种运行模式

```
用户
 ├─ python main.py        → 交互式 CLI
 └─ python auto_runner.py → 自动批量运行（随机选 level + topic）
```

---

## 模式一：单课生成

```
用户输入 blueprint 字符串 + CEFR 级别
  │
  ▼
generate_all_slides(level, blueprint_str)
  │
  ├─ [1] _extract_blueprint_vocab(blueprint)
  │       → vocab=["word1","word2",...], funcs=["chunk1","chunk2",...]
  │
  ├─ [2] generate_outline(level, blueprint_str)
  │       ├─ 加载 {level} Lesson Generator.md（截断到 # Action 前）
  │       ├─ 将真实词汇预填入 JSON Schema（LOCKED）
  │       ├─ API 调用 → outline JSON（最多 3 次 retry）
  │       └─ _fix_outline_key_points() 无条件覆盖 key_points
  │
  ├─ [3] 并行生成每张幻灯片 ThreadPoolExecutor(max_workers=3)
  │       每个 slide metadata → generate_slide_content()
  │           ├─ title slide → 直接从 bp_fields 构建（不调 API）
  │           ├─ 注入 TEACHER_PROFILE_NOTE + LEVEL_DESIGN_RULES
  │           ├─ 注入动态 LOCK（VOCABULARY / FUNCTIONAL LANGUAGE / TOPIC / SCENARIO / RECAP）
  │           ├─ API 调用 → slide JSON
  │           └─ 词汇验证（useful_language）→ 幻觉/缺失 → 重试 → force-inject
  │
  ├─ [4] 失败 slide 串行重试（max 3 次）
  │       关键模块缺失 → RuntimeError → Lesson 级重试
  │
  └─ [5] TITLE_MAP 强制修正所有幻灯片标题
  │
  ▼
polish_content(slides)
  ThreadPoolExecutor(max_workers=3)
  每张 slide → _polish_single_slide() → 改善英文，不改结构/词汇
  失败 → fallback 到原始 slide
  │
  ▼
build_html(slides)          slide_renderer.py
  每个 slide dict → render_*() → HTML 字符串
  拼装完整 HTML（CSS + JS + base64 logo）
  │
  ▼
export_pdf(html_path, pdf_path)
  Playwright headless Chromium
  → 打开 HTML → networkidle → fitSlideBody() → 导出 PDF（1920×1080）
  │
  ▼
输出：output/{name}_{level}.json / .html / .pdf
```

---

## 模式二：整单元生成

```
用户输入单元描述（或 auto_runner 随机选 level + topic）
  │
  ▼
chat_unit_planning() / _auto_chat_unit_planning()
  ├─ [system: UNIT_SYSTEM_PROMPT]  沙特背景 + 1对1限制 + 合规红线
  ├─ [user: 主题描述]
  ├─ AI 多轮对话（可能追问细节）
  └─ 用户输入 "proceed" 或 AI 输出 [READY TO GENERATE]
  │
  ▼
generate_unit_outline(messages, level)
  ├─ 追加 UNIT_OUTLINE_INSTRUCTION 到 messages
  ├─ API 调用 → unit outline JSON（JSONDecodeError 也触发 retry，最多 3 次）
  └─ 保存 unit_outline.json + _debug 文件
  │
  ▼
create_unit_dir()  →  output/Unit_{级别}_{时间戳}_{主题}/
  │
  ▼
for each lesson in outline["lessons"]:
  │
  └─ generate_lesson(level, lesson, outline, unit_dir)   utils.py
       外层最多重试 3 次，每次走完完整 4 步：
       [1] generate_all_slides()  →  slides list
       [2] polish_content()       →  润色
       [3] 保存 JSON
       [4] build_html() → export_pdf()
  │
  ▼
QA 测试（自动运行）
  │
  ├─ test_outline(unit_dir)
  │     ├─ programmatic_check_outline()   程序化校验（无 API）
  │     └─ AI 评审（OUTLINE_QA_PROMPT）
  │           6 个维度：口语导向 / CEFR匹配 / 交际句型 / 逻辑连贯 / 格式规范 / 中东合规⚡
  │
  ├─ test_lessons(unit_dir)
  │     随机抽取 min(3, 总课数) 个 lesson
  │     ├─ programmatic_check_lesson()   程序化校验
  │     └─ 并行 AI 评审（LESSON_QA_PROMPT，3 workers）
  │           6 个维度：大纲忠实度 / 容量结构 / CCQ质量 / 交际语块 / 级别匹配 / 中东合规⚡
  │
  └─ append_qa_log()  →  output/qa_log.xlsx 追加一行
  │
  ▼
输出：
  output/Unit_{级别}_{时间戳}_{主题}/
    unit_outline.json
    L1_{课名}_{级别}.json / .html / .pdf
    L2_...
    _qa/
      outline_qa_{时间戳}.txt
      lesson_qa_L{N}_{时间戳}.txt  （每抽查课一份）
```

---

## 数据结构流转

```
blueprint_str / lesson dict
  │
  ▼ generate_outline()
outline: list[dict]   ← 8个 slide 的结构描述
  [
    {"type": "title",              "unit": "...", "lesson": "...", "objective": "..."},
    {"type": "warm_up",            "key_points": ["topic hint"]},
    {"type": "useful_language_1",  "key_points": ["word1", "word2"]},   ← LOCKED
    {"type": "useful_language_2",  "key_points": ["word3", "word4"]},   ← LOCKED
    {"type": "conversation_builder","key_points": ["chunk1", "chunk2"]},← LOCKED
    {"type": "practice",           "key_points": ["topic"]},
    {"type": "scenario",           "key_points": ["role A", "role B"]},
    {"type": "wrap_up",            "key_points": ["vocab+chunk recap"]}
  ]
  │
  ▼ generate_slide_content() × N（并行）
slides: list[dict]   ← 完整幻灯片内容（8个 slide 对象）
  │
  ▼ polish_content()
slides: list[dict]   ← 同结构，英文表达更自然
  │
  ▼ build_html()
html: str            ← 完整 HTML 页面（1920×1080px）
  │
  ▼ export_pdf()
*.pdf                ← 最终交付文件
```

---

## 合规检查流

```
生成端（防止生成违规内容）
  common_unit_prompts.md → UNIT_SYSTEM_PROMPT
    └─ 7条完整红线注入到 Unit 规划 System Prompt
         ⛔ 非伊斯兰宗教 / 哈拉姆 / 神秘主义 / 社会禁区 / 政治 / 非伊斯兰节日
         ⚠️ 中等风险替换建议

审核端（QA 时验证合规）
  common_qa_prompts.md → OUTLINE_QA_PROMPT + LESSON_QA_PROMPT
    └─ 第 6 维度"中东内容合规" ⚡ 致命红线
         触碰任何一条 → 直接判不合格 → 🔴 打回重做
```

---

## 防幻觉约束层

```
blueprint
  └─ _extract_blueprint_vocab()
       ↓ vocab list, funcs list
       ├─ generate_outline() 时：硬编码进 prompt schema（AI 看到的是已填好的值）
       ├─ _fix_outline_key_points()：生成后无条件覆盖（不信任 AI 输出）
       └─ generate_slide_content() 时：注入 VOCABULARY LOCK / FUNCTIONAL LANGUAGE LOCK

TITLE_MAP（模块级常量）
  └─ generate_all_slides() 末尾：强制修正所有幻灯片标题

词汇验证（generate_slide_content 内）
  └─ 检查 AI 生成的 words[] 是否与 key_points 完全匹配
       幻觉词（多出来的）→ 加严 prompt 重试
       缺失词（少了的）→ 加严 prompt 重试
       3 次后仍违规 → Python force-inject
```
