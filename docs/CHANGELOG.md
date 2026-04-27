# CHANGELOG — 51Talk Lesson Generator

格式：每次改动追加一条记录，最新在最上方。

---

## 2026-04-20

### v3.3 — 文化禁忌检测全面加固：关键词补全 + 硬后处理 sanitizer

**来源**：合规审查 — 发现 `bikini`、`birthday`、`bacon`、`cocktail`、`church` 等词未进入程序化关键词列表，仅靠 Emoji 封禁或 AI 语义审查，存在漏网风险；且现有架构缺少"检测到就自动替换"的后处理层

| 改动 | 位置 | 说明 |
|------|------|------|
| 补全 `SENSITIVE_PHRASES` 列表 | `qa_tester.py:62` | 新增 14 个漏网词：`bikini` `lingerie` `bacon` `sausage` `pork chop` `cocktail` `champagne` `birthday` `christmas` `halloween` `santa` `valentine` `church` `bible` `rabbi` `buddha`；`ham`/`pig`/`cross`/`easter` 因子串误匹配风险高，改由 sanitizer 词边界规则处理 |
| 新建 `sanitizer.py` | `sanitizer.py`（新） | 硬后处理模块，基于 `\b` 词边界正则，覆盖猪肉制品、酒精、裸露服装、非伊斯兰节日、非伊斯兰宗教符号共 5 类 22 条规则；检测到即替换为中性词并打印日志；支持 `sanitize_lesson(data)` 和 `sanitize_file(path)` 两种调用方式 |

**关键词覆盖对比**：

| 禁忌类别 | 改前 | 改后 |
|---------|------|------|
| 猪肉制品 | 仅 `pork` | `pork` `pork chop` `bacon` `sausage` + sanitizer 覆盖 `ham` `pig` `ribs` |
| 酒精 | `beer` `wine` `liquor` `alcohol` `drunk` | +`cocktail` `champagne` |
| 服装 | 仅 Emoji 👙 | +`bikini` `lingerie` |
| 非伊斯兰节日 | 无 | `birthday` `christmas` `halloween` `santa` `valentine` + sanitizer 覆盖 `easter` |
| 宗教符号 | 无 | `church` `bible` `rabbi` `buddha` + sanitizer 覆盖 `cross` |

**后处理流程**：sanitizer 在 AI 生成后、写出 JSON / QA 前运行，自动替换违禁词为中性词，全程打印 `[SANITIZER]` 日志；QA 程序化扫描作为第二道保障

| 接入 `sanitize_lesson` 到主生成流程 | `utils.py:generate_lesson`、`main.py:run_single_lesson` | polish 之后、写 JSON 之前调用；有替换时打印 `[SANITIZER] N substitution(s)` |

**改动文件**：`qa_tester.py`、`sanitizer.py`（新增）、`utils.py`、`main.py`

---

## 2026-04-17

### v3.2 — 中东内容合规红线全面加入 Prompt 体系

**来源**：合规审查 — 发现 `common_unit_prompts.md` 的禁止话题只有一行不完整的描述，`common_qa_prompts.md` 的 QA prompt 完全没有文化合规检查维度

| 改动 | 位置 | 说明 |
|------|------|------|
| 替换不完整的 `Forbidden topics` 一行 | `prompts/common_unit_prompts.md` | 扩展为 7 条完整红线：非伊斯兰宗教、哈拉姆内容、反宗教/神秘主义、社会禁区、政治禁区、非伊斯兰节日、中等风险替换建议 |
| 新增第 6 维度"中东内容合规" | `prompts/common_qa_prompts.md` → OUTLINE_QA_PROMPT | 标记为 ⚡ 致命红线，触碰任何一条直接判不合格 |
| 新增第 6 维度"中东内容合规" | `prompts/common_qa_prompts.md` → LESSON_QA_PROMPT | 同上，覆盖脚本中的话题、词汇、场景、例句 |

**效果**：生成端（Generator）和审核端（QA）均有完整合规约束，形成双重保障

**改动文件**：`prompts/common_unit_prompts.md`、`prompts/common_qa_prompts.md`

---

### v3.2 QA 验证报告（第十八次运行：B2 薪资谈判，0417_1559）

**运行结果**：✅ **Pass** — 全部 6 课生成成功，Outline 100分、抽查 3 课 98/100/98 分

| 测试项 | 程序化校验 | AI QA 评分 | 结果 |
|--------|-----------|-----------|------|
| Outline | ✅ 全部通过 | 100（亮点：沙特本土化极佳，Vision 2030 融入，B2 词汇精准） | Pass |
| L1 Understanding the Initial Offer | ✅ 全部通过 | 98（建议：allowance CCQ 改为二选一格式） | Pass |
| L2 Preparing Your Value Proposition | ✅ 全部通过 | 98（建议：competitive CCQ 改为开放式问题） | Pass |
| L5 Handling Pushback from HR | ✅ 全部通过 | 100 | Pass |
| L3/L4/L6 | ✅ 全部通过 | 未 QA | — |

**中东合规验证**：QA 报告首次明确标注"中东合规性：100% 符合"，新加的红线规则在 QA 报告中生效

**运行稳定性**：全程零 JSONDecodeError，零 429，6/6 课一次性全部成功

**结论**：Pass。连续**十轮 Pass**（第9–18轮），v3.2 版本稳定。

---

### 文件清理

删除以下无用文件：
- `_css.txt` / `_gfonts.txt` / `_js.txt` / `_logo_src.txt` / `logo_b64.txt` — 构建临时文件
- `build_renderer.py` / `write_renderer.py` — 一次性构建脚本
- `check_general_english.py` — 未被主流程引用的独立脚本
- `scripts/backfill_qa_log.py` + `scripts/` 目录 — 一次性历史数据回填工具
- `output/preview_v4.html` / `output/headers.txt` / `output/qa_*.txt` / `output/qa_log_dump.*` — 调试临时文件

---

## 2026-04-15

### v3.1 — Final Lesson 词汇复现规则强化（A1/A2）

**来源**：第16次（A2 购物）、第17次（A1 节日）Outline QA 均指出最终课词汇漂移

| 改动 | 位置 | 说明 |
|------|------|------|
| 新增 `FINAL LESSON VOCABULARY RULE` | `prompts/common_unit_prompts.md` | 最终课 vocabulary 应以复现前5课词汇为主，允许引入最多2个新词，禁止大量引入新词 |

**改动文件**：`prompts/common_unit_prompts.md`

---

### v3.1 QA 验证报告（第十七次运行：A1 节日与庆典，0415_1234）

**运行结果**：✅ **Pass** — 全部 6 课生成成功，Outline 95分、抽查 3 课 100/100/98 分

**结论**：Pass。连续**九轮 Pass**（第9–17轮）。

---

### v3.0 — useful_language teacher_instructions 字段强制规范化

**来源**：第13、14次运行 AI QA 连续两次指出 `teacher_instructions` 字段缺失或格式不一致

| 改动 | 位置 | 说明 |
|------|------|------|
| `useful_language_1/2` 模板新增 `teacher_instructions` 字段 | `prompts/common_slide_templates.md` | 强制 4 步固定数组格式，新增 TEACHER INSTRUCTIONS LOCK |

**改动文件**：`prompts/common_slide_templates.md`

---

### v3.0 QA 验证报告（第十六次运行：A2 购物与退换货，0415_1222）

**运行结果**：✅ **Pass** — 全部 6 课生成成功，Outline 95分、抽查 3 课全部 100 分

**结论**：Pass。连续**八轮 Pass**（第9–16轮）。

---

### v3.0 QA 验证报告（第十五次运行：A2 喜爱的电视节目/电影，0415_1202）

**运行结果**：✅ **Pass** — 全部 6 课生成成功，Outline 100分、抽查 3 课全部 100 分

**结论**：Pass。连续**七轮 Pass**（第9–15轮）。

---

## 2026-04-14

### v2.9 — unit outline JSON 截断重试修复

**来源**：第十一次运行（B1 解释流程）unit outline JSON 截断导致整个 Unit 直接中断

| 改动 | 位置 | 说明 |
|------|------|------|
| API 调用和 JSON 解析统一纳入同一 retry 循环 | `generate_unit_outline()` | JSONDecodeError 同样触发 sleep 后重新调 API，最多 3 次 |

**改动文件**：`content_processor.py`

---

### v2.8 — title slide 元数据来源修正

**来源**：第八次运行（B1 家庭旅行）L3/L4 QA 95分 Fail — title 字段被 AI slide-level outline 覆盖

| 改动 | 位置 | 说明 |
|------|------|------|
| title slide 数据改为 100% 来自 `bp_fields` | `generate_all_slides()` | 绝不信任 AI slide-level outline 的 meta 字段 |

**改动文件**：`content_processor.py`

---

## 2026-04-13

### v2.7 — NameError 修复（`taught` 变量初始化恢复）

**改动文件**：`content_processor.py`（1行修复）

---

### v2.6 — 429 限流缓解：降低并发数 + 滑点重试退避

| 改动 | 说明 |
|------|------|
| `_PARALLEL_WORKERS` 从 5 → 3 | 减少集中触发 429 的概率 |
| slide/outline 生成新增 backoff retry | sleep(15×attempt) / sleep(10×attempt) |

**改动文件**：`content_processor.py`

---

### v2.5 — title slide Python 直接生成（跳过 API 调用）

**改动文件**：`content_processor.py`

---

### v2.4 — warm_up bug 修复 + 重复规则清理

**改动文件**：`content_processor.py`、`prompts/common_unit_prompts.md`

---

### v2.3 — 最终课 lesson_task 引导规则加强

**改动文件**：`prompts/common_unit_prompts.md`

---

### v2.2 — wrap_up final_task 超载修复

**改动文件**：`prompts/common_slide_templates.md`、`content_processor.py`

---

## 2026-04-12

### v2.1 — 代码重构：消除重复、统一架构

新增 `utils.py`，统一 OpenAI client 单例，blueprint 规范化，各文件精简。总代码行数 -307 行。

**改动文件**：`config.py`、`utils.py`(新)、`content_processor.py`、`qa_tester.py`、`auto_runner.py`、`main.py`

---

### v2.0 — Prompt 统一外置

~20,000 字符 prompt 从 Python 代码中提取到 `prompts/` 文件夹，新增 5 个 `common_*.md` 文件。

**改动文件**：`content_processor.py`、`qa_tester.py`、新增 5 个 `prompts/common_*.md`

---

## 2026-04-10

### v1.18 — Warm-up 单问题规则 + auto_runner/generate_unit_outline 超时重试

**改动文件**：`content_processor.py`、`auto_runner.py`

---

### v1.16 — 项目结构整理 + QA 程序化校验层

新增 `programmatic_check_outline()` 和 `programmatic_check_lesson()`，在 AI QA 之前先做硬性检查。

**改动文件**：`config.py`、`content_processor.py`、`qa_tester.py`

---

### v1.15 — Wrap-up Final Task 幻觉修复 + B1 词汇上限 + L6 闭环强制

**改动文件**：`content_processor.py`

---

## 2026-04-09

### v1.14 — 词汇漏教 Python 强制补全

**改动文件**：`content_processor.py`

---

## 2026-04-08

### v1.13 — CCQ 规则强化 + Practice 模板修复

**改动文件**：`content_processor.py`

---

### v1.11 — polish 改为逐 slide 并行处理

**改动文件**：`content_processor.py`

---

### v1.0 — QA 测试系统 + Excel 日志

新增 `qa_tester.py`，两轮 QA：大纲质量评估 + 随机3课内容评估，结果写入 `qa_log.xlsx`。

---

## 2026-04-03

### v0.1 — 初始项目结构
- 原始 `main.py` 单文件，949 行，支持单课生成

### v0.5 — 模块拆分
- 拆分为 `content_processor.py` / `slide_renderer.py` / `main.py`

### v1.0 — QA 系统上线
- 新增 `qa_tester.py` + `qa_log.xlsx`
