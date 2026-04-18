# 51Talk ESL Lesson Generator

AI-powered tool for generating complete ESL lesson slide decks (HTML + PDF) for 51Talk adult learners in Saudi Arabia.

## Requirements

- Python 3.10+
- OpenAI-compatible API key (configured in `config.py`)

```bash
pip install openai playwright openpyxl
playwright install chromium
```

## Quick Start

### Interactive mode
```bash
python main.py
```

### Auto runner (non-interactive, random topic + QA)
```bash
python auto_runner.py
```

### QA only (test existing unit)
```bash
python qa_tester.py [unit_folder_path]
```

## Modes

### Mode 1: Single Lesson (`main.py` → option 1)
Provide a blueprint string directly. Output: `output/<name>_<level>.json/html/pdf`

### Mode 2: Full Unit (`main.py` → option 2)
1. Select CEFR level (A1–C1)
2. Describe the unit, chat with AI to refine
3. Type `proceed` when ready
4. AI generates 6–10 lesson outline + each lesson automatically

### Mode 3: Auto Runner (`auto_runner.py`)
Picks random level + topic from pool of 75 topics, generates full unit, runs QA automatically.

## File Structure

```
tp_generator/
├── auto_runner.py         # Non-interactive autonomous runner
├── main.py                # Interactive CLI entry point
├── config.py              # API config, OpenAI client singleton, theme, levels
├── content_processor.py   # AI orchestration (outline, slides, polish, unit planning)
├── slide_renderer.py      # HTML rendering (logo embedded as base64) + PDF export
├── qa_tester.py           # Dual-layer QA (programmatic + AI) + Excel logging
├── utils.py               # Shared utilities (safe_name, retry, create_unit_dir, generate_lesson)
├── 51talklogo.png         # Logo asset (embedded into HTML/PDF at build time)
├── prompts/               # All prompt files (never hardcoded in Python)
│   ├── common_*.md        # Shared prompts (unit, slides, polish, QA, teacher context)
│   └── {Level} *.md       # Per-level generator, polisher, QA prompts
├── output/                # All generated output (not version-controlled)
│   ├── preview_final.html # HTML/CSS/JS template (source for slide_renderer)
│   ├── qa_log.xlsx        # Cumulative QA log across all runs
│   ├── _debug/            # Raw AI responses for debugging
│   └── Unit_{Level}_{Date}_{Name}/
│       ├── unit_outline.json
│       ├── L{N}_{Name}_{Level}.json / .html / .pdf
│       └── _qa/           # QA reports per unit
└── DOCS/                  # Documentation
    ├── README.md
    ├── ARCHITECTURE.md
    ├── FLOWCHART.md
    └── CHANGELOG.md
```

## Content Compliance

All generated content is subject to Middle East content compliance rules (Saudi Arabian market):
- No non-Islamic religions, holidays, or symbols
- No alcohol, pork, or gambling references
- No dating/romance, LGBTQ, or sexual content
- No Israel-related or terrorist organization content
- No magic, astrology, evolution, or occult references

See `🛑 中东青少内容审核红线指南（实习生版）.md` for the full red-line guide.

## QA System

Every run automatically executes a dual-layer QA:
1. **Programmatic checks** — module completeness, banned modules, vocabulary fidelity, written-task red-line
2. **AI evaluation** — CEFR alignment, teacher friendliness, CCQ quality, 25-min capacity, Middle East compliance

Results are saved to `output/qa_log.xlsx` and per-unit `_qa/` folders.

## Version

Current version: **v3.2** — see `DOCS/CHANGELOG.md` for full history.

Pass rate trend: 0% (v0.x) → 38% (v2.0) → 71% (v2.5) → 100% (v2.8+, 9 consecutive passes)
