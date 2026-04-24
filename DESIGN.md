# 51Talk Lesson Generator — UI Design Specification

> **Project**: tp_generator Web Interface
> **Type**: Internal SaaS Demo Tool
> **Audience**: Leadership demo + internal content designers
> **Language**: English / Arabic bilingual UI
> **Vibe**: AI-native, premium ed-tech, clean & confident

---

## 1. Design Philosophy

**"AI as a co-pilot, not a black box."**

Every screen should make the AI feel tangible — typing indicators, real-time progress, streaming logs. The UI must look like a polished product, not a script wrapper.

- **Density**: Medium. Generous whitespace, no clutter.
- **Motion**: Purposeful. Animations communicate state changes (AI thinking, progress advancing, files arriving).
- **Hierarchy**: Step-driven wizard as the hero flow. Dashboard secondary.

---

## 2. Brand Foundation

### 2.1 Logo & Lockup
- **Primary logo**: 51Talk wordmark (top-left nav)
- **Lockup variant**: "51Talk Lesson Studio" for the web app title
- **Logo placement**: Fixed top-left, 24px height, white on dark nav

### 2.2 Color System

| Token | Hex | Usage |
|-------|-----|-------|
| **Primary** | `#2563EB` | CTAs, active states, links, progress bars, AI avatar ring |
| **Primary Light** | `#EFF6FF` | Hover backgrounds, badge fills |
| **Primary Dark** | `#1E3A8A` | Top navigation bar background |
| **Success** | `#10B981` | Done states, checkmarks, success toasts |
| **Warning** | `#F59E0B` | Fallback selections, manual overrides |
| **Error** | `#EF4444` | Failures, validation errors |
| **Surface** | `#F8FAFC` | Page background |
| **Card** | `#FFFFFF` | Content cards |
| **Text Primary** | `#0F172A` | Headings, primary text |
| **Text Secondary** | `#64748B` | Descriptions, placeholders |
| **Border** | `#E2E8F0` | Card borders, dividers |
| **Dark Surface** | `#0F172A` | Log panel background, dark mode accents |

### 2.3 Typography
- **Heading**: Inter 600/700
- **Body**: Inter 400/500
- **Mono**: JetBrains Mono (for logs, code, file names)
- **Scale**:
  - H1: 36px / 1.2
  - H2: 20px / 1.3
  - Body: 14px / 1.6
  - Caption: 12px / 1.5
  - Log: 12px mono / 1.6

### 2.4 Border & Shadow
- **Card radius**: 16px
- **Button radius**: 8px (pill for tags: 999px)
- **Card shadow**: `0 4px 20px rgba(0,0,0,0.06)`
- **Hover shadow**: `0 8px 30px rgba(37,99,235,0.12)`

---

## 3. Global Components

### 3.1 Top Navigation Bar
- **Height**: 56px
- **Background**: `#1E3A8A` (solid, no blur)
- **Left**: 51Talk logo + app name "Lesson Studio"
- **Right**: Language toggle (EN / AR), Settings icon (gear)
- **Sticky**: Yes, z-index 50

### 3.2 Step Indicator (Wizard Only)
- **Style**: Horizontal steps with connecting line
- **Active step**: Primary blue circle + bold label
- **Completed step**: Green check circle + muted label
- **Future step**: Gray empty circle + muted label
- **Animation**: Step completion triggers a subtle "pop" scale (1 to 1.1 to 1) on the circle

### 3.3 AI Avatar
- **Shape**: Circular, 32px
- **Style**: Blue gradient ring (`#2563EB` to `#3B82F6`), robot icon inside
- **States**:
  - Idle: Static
  - Thinking: Slow pulse glow (box-shadow animation, 2s loop)
  - Typing: Quick bounce on icon

### 3.4 Primary Button
- **Default**: `bg-primary text-white rounded-lg px-6 py-2.5`
- **Hover**: Darken 8%, lift shadow
- **Loading**: Spinner replaces text, disabled pointer

### 3.5 Card Container
- **Padding**: 32px
- **Background**: White
- **Border**: 1px `#E2E8F0`
- **Radius**: 16px

---

## 4. Page Specifications

---

### Page A: Dashboard (Home)

**Purpose**: Entry point. Shows history + quick actions.

**Layout**:
```
[Nav Bar]
[Hero Banner: "Create AI-powered lesson materials in minutes"]
[Quick Action Cards: 2 columns]
[Recent Units Grid: 3 columns]
```

#### Hero Banner
- **Height**: ~200px
- **Background**: Soft gradient from `#EFF6FF` to `#FFFFFF`
- **Left**: H1 + subheading + "Create New Unit" CTA button
- **Right**: Abstract illustration — floating slides/cards in 3D perspective (AI-generated isometric illustration)

#### Quick Action Cards (2-up)
| Card | Icon | Title | Description |
|------|------|-------|-------------|
| Left | DocumentCopy (blue) | Generate Full Unit | "6-10 lessons with AI planning chat" |
| Right | Document (emerald) | Quick Single Lesson | "Fast blueprint-to-slide generation" |
- **Hover**: Card lifts, shadow deepens, icon scales 1.1

#### Recent Units Grid
- **Card per unit**:
  - Top strip: Level badge (A1-C1, color-coded)
  - Title: Unit name (truncated 2 lines)
  - Meta: `6 lessons - 2 hours ago`
  - File chips: HTML | PDF | JSON
- **Empty state**: Centered illustration + "No units yet. Create your first one above."
- **Load more**: Infinite scroll or pagination

---

### Page B: Unit Wizard (5 Steps)

**Purpose**: The hero flow. Generate a complete unit from idea to download.

#### Step 1 — Demand Input
**Layout**:
```
[Step Indicator: 1 active]
[Card]
  H2: "Describe your teaching needs"
  Textarea (4 rows, placeholder with example)
  Template Chips (horizontal scroll on mobile)
  [Back] [Next]
```

**Textarea**:
- Placeholder: "e.g. Absolute beginners who need to ask for directions at the airport..."
- Focus: Blue border glow
- Counter: "0/500" bottom-right

**Template Chips**:
- Pill-shaped tags below textarea
- Examples: "Airport directions", "Restaurant ordering", "Hotel check-in"...
- Click: Auto-fills textarea + slight flash animation on text

**Buttons**:
- Back: Ghost button, returns to Dashboard
- Next: Primary, disabled until textarea has content

#### Step 2 — Level Recommendation
**Layout**:
```
[Step Indicator: 2 active]
[Card]
  H2: "AI Recommended Level"
  [Analyze Animation]
  [Recommendation Card]
  [Manual Override: 5 level cards]
  [Back] [Next]
```

**Analyze Animation**:
- Shown for ~2 seconds while API call runs
- Centered: AI avatar with pulsing ring + "AI is analyzing your description..."
- Below: 3 shimmer placeholder bars (skeleton loading)

**Recommendation Card**:
- Large centered card, blue gradient background (`#EFF6FF` to `#DBEAFE`)
- Big level badge: "A1" in 48px bold blue
- Reason text below in secondary color
- "Looks good" checkmark animation when revealed

**Manual Override**:
- 5 cards in a row (A1, A2, B1, B2, C1)
- Each: level letter + short descriptor
- Selected: blue border + light blue fill
- Hover: slight lift

#### Step 3 — Planning Chat
**Layout**:
```
[Step Indicator: 3 active]
[Card]
  H2: "Unit Planning Chat"
  [Chat Box: ~320px height, scrollable]
  [Input Row: text input + Send + Proceed buttons]
  [Back] [Start Generation]
```

**Chat Box**:
- Light gray background (`#FAFAFA`), rounded 12px
- AI messages: left-aligned, white bubble, blue avatar ring
- User messages: right-aligned, blue bubble, white text
- Typing indicator: 3 bouncing dots when waiting

**Input Row**:
- Text input: "Type your reply or click Proceed"
- Send button: Primary
- Proceed button: Success green (shortcut for "proceed")

**Start Generation button**:
- Disabled until `ready_to_generate = true`
- When enabled: pulses gently to draw attention

#### Step 4 — Generating
**Layout**:
```
[Step Indicator: 4 active]
[Card]
  H2: "Generating Unit..."
  [Progress Bar: full width, striped]
  [Status Text]
  [Log Panel: ~240px, dark terminal style]
```

**Progress Bar**:
- Height: 16px
- Striped animation while in progress
- Color transitions: blue (generating) -> green (done)

**Status Text**:
- Dynamic: "Lesson 3/6: Checking In"
- Below: smaller text showing current sub-step (outline, slides, polish, render)

**Log Panel**:
- Background: `#0F172A`
- Text: `#E2E8F0` mono
- Auto-scroll to bottom
- Each new line fades in (opacity 0 to 1, 200ms)
- Bilingual lines displayed as-is (English + Arabic)

#### Step 5 — Result
**Layout**:
```
[Step Indicator: 5 completed]
[Card]
  H2: "Generation Complete"
  [Unit Summary]
  [File Grid]
  [Preview Button] [Download All]
```

**Unit Summary**:
- Unit name + level badge + success ratio
- "6/6 lessons generated successfully"

**File Grid**:
- Cards per file: icon + filename + type badge
- Types: JSON (gray), HTML (blue), PDF (red)
- Click: Opens preview or download

**Preview Modal**:
- Full-width modal (90% viewport)
- Iframe loading the HTML slide inside
- Dark backdrop

---

### Page C: Quick Single Lesson

**Purpose**: Fast-track for single lesson generation.

**Layout**:
```
[Nav Bar]
[Card]
  H2: "Quick Single Lesson"
  [Form]
    Level Dropdown
    Blueprint Textarea (6 rows)
    [Generate Button]
  [Result Area: appears after generation]
```

**Form**:
- Level: Dropdown selector (A1-C1)
- Blueprint: Large textarea with structured placeholder:
  ```
  Lesson: Airport Directions
  Vocabulary: gate, terminal, customs
  Functional Language: Where is... / How do I get to...
  Topic: Airport
  ```

**Result Area**:
- Appears below form after generation
- File cards (same style as Unit Wizard result)
- HTML preview button

---

### Page D: Settings

**Purpose**: Configure AI key, brand, output preferences.

**Layout**:
```
[Nav Bar]
[Card]
  H2: "Settings"
  [Tabs: AI / Brand / Output]
```

**AI Tab**:
- API Base URL input
- API Key input (password type, show/hide toggle)
- Model selector dropdown
- Temperature slider (0-2)

**Brand Tab**:
- Logo upload (drag & drop zone)
- Logo text input
- Logo subtitle input
- Primary color picker

**Output Tab**:
- Output directory path
- Toggle: HTML output
- Toggle: PDF output

---

## 5. Animation & Motion Specs

### 5.1 Page Transitions
- **Fade**: 200ms ease-in-out opacity
- **Slide**: Wizard steps slide horizontally (300ms ease-out)

### 5.2 Micro-interactions
| Element | Trigger | Animation |
|---------|---------|-----------|
| Card | Hover | translateY(-2px), shadow deepens, 200ms |
| Button | Click | Scale 0.97, 100ms |
| AI Avatar | Thinking | Box-shadow pulse (0 0 0 0 rgba(37,99,235,0.4) to 0 0 0 8px rgba(37,99,235,0)), 2s infinite |
| Progress bar | In progress | Striped gradient animation (1s linear infinite) |
| Log line | Append | opacity 0 to 1, 200ms |
| File card | Appear | Scale 0.95 to 1 + opacity, stagger 50ms per card |

### 5.3 Loading States
- **Skeleton**: Shimmer gradient (`#F1F5F9` to `#E2E8F0` to `#F1F5F9`), 1.5s loop
- **Spinner**: Primary blue, 16px, 1s rotate
- **Button loading**: Spinner replaces text, opacity 0.7

---

## 6. Responsive Breakpoints

| Breakpoint | Layout Changes |
|------------|----------------|
| Desktop (>=1024px) | Full layout, 3-col dashboard grid, 5 level cards in row |
| Tablet (768-1023px) | 2-col dashboard grid, level cards wrap to 3+2 |
| Mobile (<768px) | Single column, step indicator becomes vertical dots, chat full-width |

---

## 7. Assets Needed

### 7.1 Icons (Lucide / Heroicons)
- Document, DocumentCopy, Settings, Send, Download, Eye, Check, ChevronRight, Loader2, Bot, User

### 7.2 Illustrations (AI-Generated)
1. **Hero illustration**: Isometric floating lesson slides, blue gradient, clean vector style
2. **Empty state**: Friendly robot holding an empty folder, blue tones
3. **Success state**: Checkmark burst with confetti particles (subtle)

### 7.3 Logo Files
- `51Talk_logo_white.svg` (for dark nav)
- `51Talk_logo_color.svg` (for light backgrounds)

---

## 8. Accessibility Notes

- All interactive elements minimum 44x44px touch target
- Color contrast ratio >= 4.5:1 for body text
- Focus rings: 2px solid `#2563EB` with 2px offset
- Log panel: Respect `prefers-reduced-motion` (disable fade-in)

---

## 9. Deliverables for Frontend Dev

After design is approved, deliver:
1. **Figma file** (or AI-generated equivalent) with all screens at desktop + mobile
2. **Exported assets**: Icons as SVG, illustrations as PNG/SVG
3. **Color tokens** as CSS variables or design tokens JSON
4. **This document** as the functional spec reference
