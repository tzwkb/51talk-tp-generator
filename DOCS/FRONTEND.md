# 51Talk Lesson Studio — Frontend Specification

> **Scope**: Dashboard (done) + Unit Wizard (todo) + Quick Lesson (todo)  
> **Tech**: Vanilla HTML, Tailwind CSS CDN, Phosphor Icons, native JS. No build step.  
> **Backend**: FastAPI (`api.py`), SSE streaming for generation.

---

## 1. Tech Stack & Constraints

| Layer | Choice | Notes |
|-------|--------|-------|
| Markup | HTML5 | One file per page. Shared nav copied or injected via JS. |
| CSS | Tailwind CSS CDN + inline config | Custom colors/fonts defined in `<script>tailwind.config</script>`. |
| Icons | Phosphor Icons CDN | `ph ph-*` classes. Use `ph-duotone` for hero accents. |
| Fonts | Inter + JetBrains Mono | Google Fonts CDN. |
| i18n | `frontend/i18n.js` | `localStorage` persists `appLang` (`en` / `ar`). AR sets `dir="rtl"`. |
| State | In-memory JS objects | No framework. Use plain objects + DOM updates. |
| API transport | `fetch` + `EventSource` | POST for chat/analyze; SSE (`EventSource`) for generation streams. |

**Constraint**: No bundler. Every page is self-contained except `i18n.js`, which all pages import.

---

## 2. Shared Infrastructure

### 2.1 Static Asset Serving
`api.py` mounts `frontend/` at `/` via `StaticFiles(directory="frontend", html=True)`.
- `/` → `frontend/index.html` (root route still handled by `@app.get("/")`)
- `/i18n.js` → `frontend/i18n.js`
- `/51talklogo.png` → `frontend/51talklogo.png`
- `/wizard.html`, `/quick.html` → served directly

Use absolute paths in HTML: `src="/51talklogo.png"`, `href="/i18n.js"`.

### 2.2 Navigation Bar (all pages)
```
[51Talk Logo] [Lesson Studio]          [AR] [Home or Gear]
```
- Height: 56px, bg: `#1E3A8A`, sticky top, z-50.
- Language toggle button: `id="lang-switch"`, `onclick="toggleLang()"`.
- Home icon on wizard/quick pages links to `/`.

### 2.3 i18n Contract (`i18n.js`)
Global API:
- `toggleLang()` — switches `en` ↔ `ar`, persists to `localStorage`, fires `langchange` event.
- `applyI18n(lang)` — sets `document.documentElement.lang`, `document.body.dir`, updates all `[data-i18n]` elements.
- `t(key)` — returns translated string for current language.

All user-visible text MUST have `data-i18n="<key>"`. Dynamic text in JS uses `t('key')`.

---

## 3. Pages

### Page 1: Dashboard (`index.html`) — EXISTING

**Purpose**: Entry point. History + quick actions.

**Sections**:
1. **Hero**: Gradient banner, H1, subheading, CTA to Wizard.
2. **Quick Actions**: 2 cards (Full Unit → `/wizard.html`, Quick Lesson → `/quick.html`).
3. **Recent Units**: Grid fetched from `GET /api/units`.
   - Badge: level (A1–C1), color-coded.
   - Meta: `{lessons_count} lessons • {timeAgo}`.
   - File chips: JSON | HTML | PDF.
   - Empty state + error state handled.

**API used**:
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/units` | GET | Load recent units on mount + refresh. |

---

### Page 2: Unit Wizard (`wizard.html`) — TODO

**Purpose**: 5-step flow to generate a complete unit (6–10 lessons) with AI planning chat.

#### Step 1 — Demand Input
- **Step indicator**: horizontal 5 steps. Step 1 active (blue), 2–5 gray.
- **Card**:
  - H2: `t('wizard_step1_title')` — "Describe your teaching needs"
  - Textarea (4 rows), placeholder with example, max 500 chars, live counter.
  - Template chips below: clickable pills that auto-fill textarea.
  - Buttons: "Back to Dashboard" (ghost, `/`) + "Next →" (primary, disabled until textarea has content).

**State stored**: `wizardState.desc`.

#### Step 2 — Level Recommendation
- **Step indicator**: step 2 active.
- **Analyzing state** (auto-play on mount):
  - Pulsing robot icon + "AI is analyzing..." + 3 skeleton bars.
  - Calls `POST /api/analyze-level` with `{description: wizardState.desc}`.
- **Result card** (replaces analyzing state on success):
  - Large badge showing recommended level (A1–C1).
  - Reason text.
  - Manual override: 5 selectable level cards (A1–C1). Clicking updates selection.
- **Buttons**: "Back" + "Next →".

**API used**:
| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/api/analyze-level` | POST | `{"description": "..."}` | `{"level": "A1", "reason": "..."}` |

**State stored**: `wizardState.level` (AI recommendation or manual override).

#### Step 3 — Planning Chat
- **Step indicator**: step 3 active.
- **Chat box** (~320px height, scrollable, light gray bg):
  - AI messages: left, white bubble, robot avatar.
  - User messages: right, blue bubble.
  - Typing indicator while awaiting response.
- **Input row**:
  - Text input + Send button (primary).
  - "Proceed" button (success green). Sends literal `"proceed"` as user input.
- **Start Generation** button:
  - Disabled until `ready_to_generate === true`.
  - When enabled: subtle pulse animation.
  - Clicking advances to Step 4 and triggers generation.

**API used**:
| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/api/unit/plan-chat` | POST | First turn: `{"level": "A1", "unit_desc": "..."}`  
Follow-up: `{"session_id": "...", "user_input": "..."}` | `{"session_id": "...", "ai_reply": "...", "ready_to_generate": false}` |

**State stored**: `wizardState.sessionId`, `wizardState.messages[]`, `wizardState.ready`.

**Behavior**:
- First "Next" from Step 2 opens chat with `{level, unit_desc}`.
- Each user message appends to chat, sends to API, renders AI reply.
- When `ready_to_generate` becomes `true`, enable "Start Generation".

#### Step 4 — Generating
- **Step indicator**: step 4 active.
- **Progress bar**: full-width, striped animation, 16px height.
- **Status text**: dynamic. e.g. "Lesson 3/6: Checking In".
- **Sub-status**: smaller text showing stage (outline → slides → polish → render).
- **Log panel**: ~240px height, dark terminal style (`bg-[#0F172A] text-[#E2E8F0] font-mono text-xs`), auto-scroll, new lines fade in.
- No buttons — user waits.

**API used**:
| Endpoint | Method | Body | Transport |
|----------|--------|------|-----------|
| `/api/unit/generate` | POST | `{"session_id": "..."}` | SSE (`text/event-stream`) |

**SSE event types**:
| Event | Data fields | UI action |
|-------|-------------|-----------|
| `start` | `total`, `unit_name` | Reset progress bar, show status. |
| `progress` | `lesson`, `total`, `name`, `status` | Update progress bar + status text. |
| `log` | `line` | Append to log panel (auto-scroll). |
| `complete` | `unit_id`, `unit_name`, `level`, `success`, `total`, `files[]` | Store result, advance to Step 5. |
| `error` | `message` | Show error in log + alert. |

**State stored**: `wizardState.result` (populated on `complete`).

#### Step 5 — Result
- **Step indicator**: all 5 steps completed (green checks).
- **Summary card**: Unit name + level badge + "{success}/{total} lessons generated successfully".
- **File grid**: cards per file (icon + filename + type badge).
  - JSON: gray badge. HTML: blue. PDF: red.
  - Click: open in new tab (`/static/outputs/...`).
- **Buttons**: "Preview HTML" (opens modal/iframe) + "Download All" + "Generate Another" (resets wizard to Step 1).

**No API call** — uses `wizardState.result.files`.

---

### Page 3: Quick Single Lesson (`quick.html`) — TODO

**Purpose**: One-page form → generate → result. No session chat.

**Layout**:
1. **Form card**:
   - H2: `t('quick_title')` — "Quick Single Lesson"
   - **Level selector**: horizontal row of 5 cards (A1–C1), same style as Wizard Step 2. Single-select.
   - **Blueprint textarea**: 6 rows, structured placeholder:
     ```
     Lesson: Airport Directions
     Vocabulary: gate, terminal, customs
     Functional Language: Where is... / How do I get to...
     Topic: Airport
     ```
   - "Generate" button: primary, full width inside card, disabled until level + blueprint filled.
2. **Progress area** (appears after click):
   - Same striped progress bar + status text + log panel as Wizard Step 4.
3. **Result area** (appears after `complete`):
   - File grid (same component as Wizard Step 5).
   - "Preview HTML" + "Download" buttons.

**API used**:
| Endpoint | Method | Body | Transport |
|----------|--------|------|-----------|
| `/api/lesson/generate` | POST | `{"level": "A1", "blueprint": "..."}` | SSE |

**SSE events**: same structure as `/api/unit/generate` (`start`, `progress`, `log`, `complete`, `error`), but `total` is always `1`.

---

## 4. API Summary Table

| Endpoint | Method | Request Body | Response / Stream | Used By |
|----------|--------|--------------|-------------------|---------|
| `GET /api/health` | — | — | `{"status": "ok"}` | Optional heartbeat |
| `POST /api/analyze-level` | JSON | `{"description": "..."}` | `{"level", "reason"}` | Wizard Step 2 |
| `POST /api/unit/plan-chat` | JSON | `{"session_id"?, "level"?, "unit_desc"?, "user_input"?}` | `{"session_id", "ai_reply", "ready_to_generate"}` | Wizard Step 3 |
| `POST /api/unit/generate` | JSON | `{"session_id": "..."}` | SSE: `start`, `progress`, `log`, `complete`, `error` | Wizard Step 4 |
| `POST /api/lesson/generate` | JSON | `{"level": "...", "blueprint": "..."}` | SSE: `start`, `progress`, `log`, `complete`, `error` | Quick Lesson |
| `GET /api/units` | — | — | Array of unit objects | Dashboard |
| `GET /api/units/{id}/files` | — | — | `{"unit_id", "files[]"}` | Optional detail view |

---

## 5. State Management (Recommended)

Because there is no framework, use a simple module pattern per page:

```javascript
// wizard.html inline or wizard.js
const API_BASE = window.location.origin;
const wizardState = {
  step: 1,
  desc: '',
  level: '',
  sessionId: null,
  messages: [],
  ready: false,
  result: null,
};

function goStep(n) { /* hide/show sections, update step indicator */ }
function sendChat(userInput) { /* POST /api/unit/plan-chat */ }
function startGeneration() { /* POST /api/unit/generate + EventSource */ }
```

**Rules**:
- Do NOT use `localStorage` for wizard state (page refresh should reset).
- Keep DOM updates explicit (no virtual DOM).
- Destroy `EventSource` on `complete` or `error`.

---

## 6. Component Reuse

Extract these into shared behavior rather than copy-pasting:

| Component | Location | Reused By |
|-----------|----------|-----------|
| Nav bar | Inline in each HTML | All pages |
| i18n engine | `i18n.js` | All pages |
| Level selector cards | JS function | Wizard Step 2, Quick Lesson |
| Progress bar + log panel | JS function + CSS | Wizard Step 4, Quick Lesson |
| File result grid | JS function | Wizard Step 5, Quick Lesson |
| Time ago formatter | `index.html` script | Dashboard (copy to util if needed) |

Suggested shared file (optional): `frontend/components.js` — pure functions that return HTML strings and attach events.

---

## 7. Responsive Behavior

| Breakpoint | Changes |
|------------|---------|
| `>= 1024px` | Full layouts. Dashboard 3-col. Level cards 5-in-row. |
| `768–1023px` | Dashboard 2-col. Level cards wrap 3+2. |
| `< 768px` | Single column. Step indicator becomes compact dots. Chat full-width. Log panel collapses to 160px. |

---

## 8. Accessibility Checklist

- [ ] Touch targets >= 44×44px.
- [ ] Focus rings: `focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2`.
- [ ] Textarea/buttons have associated labels.
- [ ] Log panel respects `prefers-reduced-motion` (disable fade-in).
- [ ] Color contrast >= 4.5:1 for body text.

---

## 9. File Structure (Target)

```
frontend/
├── index.html          # Dashboard (EXISTING)
├── wizard.html         # Unit Wizard (TODO)
├── quick.html          # Quick Single Lesson (TODO)
├── i18n.js             # Shared i18n engine (EXISTING)
├── components.js       # Optional shared renderers (TODO)
└── 51talklogo.png      # Logo asset (EXISTING)
```

---

## 10. Open Decisions

1. **Settings page** (`settings.html`) — Out of scope for now. Backend currently reads config from `config.py`; no API to mutate settings at runtime.
2. **Preview modal** — Wizard Step 5 / Quick result: open HTML in iframe modal vs new tab? Recommendation: new tab for simplicity, modal if demo polish required.
3. **Download All** — Backend does not have a ZIP endpoint. Options:
   - Frontend triggers multiple `fetch` + JSZip (adds dependency).
   - Defer; offer individual downloads only.
