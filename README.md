# 51Talk ESL Lesson Generator

English | [中文](README_ZH.md)


AI-powered tool for generating complete ESL lesson slide decks (HTML + PDF) for 51Talk adult learners in Saudi Arabia. Now with a full web interface.

## Features

- **Interactive CLI** — Single lesson or full unit generation with AI planning chat
- **Web Dashboard** — Browser-based UI with real-time progress, no build step
- **Unit Wizard** — 5-step flow: demand input → AI level analysis → planning chat → SSE generation → result download
- **Quick Lesson** — One-page form for fast single-lesson generation
- **Settings Panel** — Adjust API key, base URL, temperature, and output toggles from the UI
- **Session Resume** — Close browser mid-generation; reopen to auto-recover progress
- **Bilingual UI** — English / Arabic language switch on all pages
- **AI Level Recommendation** — Natural language input → CEFR level suggestion
- **Dual-layer QA** — Programmatic + AI evaluation with Excel logging

## Requirements

- Python 3.10+
- OpenAI-compatible API key (configured in `config.py` or via web Settings)

```bash
# Core dependencies
pip install openai playwright openpyxl
playwright install chromium

# Web interface dependencies
pip install -r requirements-web.txt
```

## Quick Start

### CLI Mode

```bash
# Interactive mode
python main.py

# Auto runner (non-interactive, random topic + QA)
python auto_runner.py

# QA only (test existing unit)
python qa_tester.py [unit_folder_path]
```

### Web Mode

```bash
python api.py
```

Then open `http://localhost:8000` in your browser.

- **Dashboard** (`/`) — Recent units, quick actions
- **Unit Wizard** (`/wizard.html`) — Full 5-step unit generation
- **Quick Lesson** (`/quick.html`) — Single lesson fast track
- **Settings** — Click the gear icon on the Dashboard to adjust API config

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze-level` | POST | AI recommends CEFR level from natural language description |
| `/api/unit/plan-chat` | POST | Multi-turn unit planning chat (session-based) |
| `/api/unit/generate` | POST | SSE stream — generates full unit with live progress + logs |
| `/api/lesson/generate` | POST | SSE stream — generates single lesson |
| `/api/units` | GET | List all generated units |
| `/api/settings` | GET / POST | Read / update runtime config (API key, URL, toggles) |
| `/api/session/{id}` | GET | Check session status for resume |

Full API spec: `DOCS/API.md`

## Modes

### Mode 1: Single Lesson (`main.py` → option 1 / Quick Lesson page)
Provide a blueprint string directly. Output: `output/<name>_<level>.json/html/pdf`

### Mode 2: Full Unit (`main.py` → option 2 / Unit Wizard page)
1. Describe teaching needs (AI recommends CEFR level)
2. Chat with AI to refine the unit plan
3. Click **Proceed** or type `proceed` when ready
4. AI generates 6–10 lesson outline + each lesson automatically

### Mode 3: Auto Runner (`auto_runner.py`)
Picks random level + topic from pool of 75 topics, generates full unit, runs QA automatically.

## File Structure

```
tp_generator/
├── api.py                  # FastAPI backend (REST + SSE)
├── main.py                 # Interactive CLI entry point
├── auto_runner.py          # Non-interactive autonomous runner
├── config.py               # API config, OpenAI client proxy, theme, levels
├── content_processor.py    # AI orchestration (outline, slides, polish, unit planning)
├── slide_renderer.py       # HTML rendering (logo embedded as base64) + PDF export
├── qa_tester.py            # Dual-layer QA (programmatic + AI) + Excel logging
├── utils.py                # Shared utilities (safe_name, retry, create_unit_dir, generate_lesson)
├── i18n.py                 # Bilingual string loader (EN/AR)
├── 51talklogo.png          # Logo asset (embedded into HTML/PDF at build time)
├── prompts/                # All prompt files (never hardcoded in Python)
│   ├── common_*.md         # Shared prompts (unit, slides, polish, QA, teacher context)
│   └── {Level} *.md        # Per-level generator, polisher, QA prompts
├── l10n/                   # UI translations
│   ├── en.json
│   └── ar.json
├── frontend/               # Web UI (vanilla HTML + Tailwind CSS)
│   ├── index.html          # Dashboard
│   ├── wizard.html         # 5-step Unit Wizard
│   ├── quick.html          # Quick Single Lesson
│   ├── i18n.js             # Shared i18n engine
│   ├── components.js       # Shared UI components (level selector, file grid, SSE)
│   └── 51talklogo.png      # Logo
├── output/                 # All generated output (not version-controlled)
│   ├── qa_log.xlsx         # Cumulative QA log across all runs
│   ├── _debug/             # Raw AI responses for debugging
│   └── Unit_{Level}_{Date}_{Name}/
│       ├── unit_outline.json
│       ├── L{N}_{Name}_{Level}.json / .html / .pdf
│       └── _qa/            # QA reports per unit
└── DOCS/                   # Documentation
    ├── API.md              # Full API specification
    ├── FRONTEND.md         # Frontend dev spec
    ├── ARCHITECTURE.md     # System architecture
    ├── DESIGN.md           # UI design tokens
    ├── FLOWCHART.md        # Data flow diagrams
    └── CHANGELOG.md        # Version history
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

Current version: **v3.3** — see `DOCS/CHANGELOG.md` for full history.

Pass rate trend: 0% (v0.x) → 38% (v2.0) → 71% (v2.5) → 100% (v2.8+, 9 consecutive passes)
