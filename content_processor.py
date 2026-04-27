# ============================================================
# content_processor.py — 所有 AI 调用：prompt 加载、大纲生成、
#                         幻灯片生成、内容润色、Unit 规划
# ============================================================

import json
import re
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import config
from config import client
from i18n import _

_RE_VOCAB = re.compile(r'[Vv]ocabulary[:\s]+([^\n]+)')
_RE_FUNCS = re.compile(r'[Ff]unctional [Ll]anguage[:\s]+([^\n]+)')

_PARALLEL_WORKERS = 3

# ── Helpers ────────────────────────────────────────────────

def _strip_fences(raw: str) -> str:
    """Strip markdown code fences from AI response."""
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw


def _split_vocab(vocab: list[str]) -> tuple[list[str], list[str]]:
    """Split vocab list into (part1, part2) for useful_language slides.
    Returns (all_vocab, []) when len <= 2 (single slide), else splits roughly in half.
    """
    if len(vocab) <= 2:
        return vocab, []
    mid = 2 if len(vocab) <= 4 else len(vocab) // 2
    return vocab[:mid], vocab[mid:]


TITLE_MAP = {
    "useful_language_1": "Useful Language (Part 1)",
    "useful_language_2": "Useful Language (Part 2)",
    "practice": "Let's Practice",
    "conversation_builder": "Conversation Builder",
    "wrap_up": "Wrap-Up",
    "warm_up": "Warm Up",
    "scenario": "Real-World Scenario",
}

# ── Prompt 加载 ────────────────────────────────────────────

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_prompt_cache: dict[str, str] = {}


def _load_common_file(filename: str) -> str:
    """Load and cache a file from prompts/ folder."""
    if filename not in _prompt_cache:
        filepath = _PROMPTS_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        _prompt_cache[filename] = filepath.read_text(encoding="utf-8")
    return _prompt_cache[filename]


def _load_section(filename: str, section: str) -> str:
    """Load a named section from a multi-section .md file.
    Sections are delimited by '# SECTION_NAME' headers.
    Returns the text between the matching header and the next header (or EOF).
    """
    content = _load_common_file(filename)
    marker = f"# {section}"
    start = content.find(marker)
    if start == -1:
        raise ValueError(f"Section '{section}' not found in {filename}")
    start += len(marker)
    # Find next section header
    next_header = content.find("\n# ", start)
    if next_header == -1:
        return content[start:].strip()
    return content[start:next_header].strip()


def _load_slide_templates(filename: str) -> dict[str, str]:
    """Parse common_slide_templates.md into {slide_type: template_text} dict."""
    content = _load_common_file(filename)
    templates = {}
    # Split on '# slide_type' headers (handle both start-of-file and mid-file)
    parts = re.split(r'(?:^|\n)# (\w+)\n', content)
    # parts = ['', 'title', 'content...', 'warm_up', 'content...', ...]
    for i in range(1, len(parts), 2):
        slide_type = parts[i].strip()
        template_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        templates[slide_type] = template_text
    return templates


def _load_level_design_rules(filename: str) -> dict[str, str]:
    """Parse LEVEL_DESIGN_RULES section into {level: rule} dict."""
    section = _load_section(filename, "LEVEL_DESIGN_RULES")
    rules = {}
    for line in section.splitlines():
        line = line.strip()
        if line and ":" in line:
            level, rule = line.split(":", 1)
            rules[level.strip()] = rule.strip()
    return rules


def load_prompt(level: str, prompt_type: str) -> str:
    if level == "B2" and prompt_type == "Lesson Generator":
        filename = "B2 Content Generator.md"
    else:
        filename = f"{level} {prompt_type}.md"
    filepath = _PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    return filepath.read_text(encoding="utf-8")


# ── 从外部文件加载常量 ─────────────────────────────────────

SLIDE_CONTENT_TEMPLATES = _load_slide_templates("common_slide_templates.md")
LEVEL_DESIGN_RULES = _load_level_design_rules("common_teacher_context.md")
TEACHER_PROFILE_NOTE = _load_section("common_teacher_context.md", "TEACHER_PROFILE_NOTE")
UNIT_SYSTEM_PROMPT = _load_section("common_unit_prompts.md", "UNIT_SYSTEM_PROMPT")
UNIT_OUTLINE_INSTRUCTION = _load_section("common_unit_prompts.md", "UNIT_OUTLINE_INSTRUCTION")
_POLISH_PROMPT_TEMPLATE = _load_common_file("common_polish.md")

PROCEED_KEYWORDS = {"proceed", "generate", "ok", "go", "start", "yes", "ready", "done"}


# ── 单课大纲生成 ───────────────────────────────────────────

def generate_outline(level: str, blueprint_str: str, max_retries: int = 3) -> list[dict]:
    print(_("gen_outline", level=level))

    base_prompt = load_prompt(level, "Lesson Generator")
    for action_marker in ["# Action", "\nAction\n"]:
        if action_marker in base_prompt:
            base_prompt = base_prompt.split(action_marker)[0]
            break
    base_prompt = base_prompt.replace("[PASTE BLUEPRINT HERE]", blueprint_str)
    base_prompt = base_prompt.replace("[Insert Lesson Script Here]", blueprint_str)
    base_prompt = base_prompt.replace("[Insert Lesson Blueprint Here]", blueprint_str)

    # Vocab pre-filled in schema so AI can't invent wrong words.
    _vocab, _funcs = _extract_blueprint_vocab(blueprint_str)

    ul_slides_schema = ""
    if _vocab:
        ul1, ul2 = _split_vocab(_vocab)
        ul_slides_schema = f'    {{"type": "useful_language_1",   "key_points": {json.dumps(ul1)}}},\n'
        if ul2:
            ul_slides_schema += f'    {{"type": "useful_language_2",   "key_points": {json.dumps(ul2)}}},\n'
    else:
        # No vocab extracted — fall back to generic placeholders (AI fills them, fix later)
        ul_slides_schema = (
            '    {"type": "useful_language_1",   "key_points": ["word1", "word2"]},\n'
            '    {"type": "useful_language_2",   "key_points": ["word3", "word4"]},\n'
        )

    if _funcs:
        cb_schema = f'    {{"type": "conversation_builder","key_points": {json.dumps(_funcs)}}},\n'
    else:
        cb_schema = '    {"type": "conversation_builder","key_points": ["speaking chunk", "model sentence"]},\n'

    final_prompt = f"""{base_prompt}

# Action
Generate a JSON outline (NOT the full Markdown script).

This is a 25-minute 1-on-1 speaking class. The outline MUST have exactly this structure — no more, no fewer sections:

{{
  "slides": [
    {{"type": "title",               "unit": "...", "lesson": "...", "objective": "..."}},
    {{"type": "warm_up",             "key_points": ["topic hint", "1 discussion question"]}},
{ul_slides_schema}{cb_schema}    {{"type": "practice",            "key_points": ["discussion topic"]}},
    {{"type": "scenario",            "key_points": ["role A", "role B", "situation"]}},
    {{"type": "wrap_up",             "key_points": ["vocab recap", "chunk recap"]}}
  ]
}}

CRITICAL:
- Output ONLY valid JSON, no markdown, no explanation.
- Every slide must have a "type" field.
- The useful_language key_points above are LOCKED — copy them EXACTLY as shown. Do NOT change the words.
- The conversation_builder key_points above are LOCKED — copy them EXACTLY as shown. Do NOT change the phrases.
- DO NOT include grammar_focus, speaking_chain, quick_check, or any other section types.
- ONE-ON-ONE speaking class only — every section must have a student speaking turn.
- Fill in the "..." and placeholder fields (title, warm_up question, practice topic, scenario roles, etc.) based on the blueprint.
"""

    debug_dir = Path(config.OUTPUT_DIR) / "_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config.AI_MODEL,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=config.AI_TEMPERATURE,
                max_tokens=2048,
            )
            raw = response.choices[0].message.content
            if not raw or not raw.strip():
                if attempt < max_retries - 1:
                    print(_("warn_empty_retry", attempt=attempt+1, max=max_retries))
                    continue
                raise ValueError("API returned empty content after retries")

            raw = raw.strip()
            with open(debug_dir / f"outline_raw_attempt{attempt + 1}.txt", "w", encoding="utf-8") as f:
                f.write(raw)
            print(_("debug_saved", path=debug_dir / f"outline_raw_attempt{attempt + 1}.txt"))

            raw = _strip_fences(raw)
            outline = json.loads(raw)

            slides = outline["slides"]
            for slide in slides:
                if not isinstance(slide, dict) or "type" not in slide:
                    raise ValueError(f"Invalid slide format: {slide}")

            with open(debug_dir / "outline_parsed.json", "w", encoding="utf-8") as f:
                json.dump(outline, f, ensure_ascii=False, indent=2)
            print(_("outline_generated", n=len(slides)))
            return slides

        except Exception as e:
            if attempt < max_retries - 1:
                wait = 10 * (attempt + 1)
                print(_("warn_attempt_failed", attempt=attempt+1, type=type(e).__name__, msg=e, wait=wait))
                time.sleep(wait)
            else:
                print(_("error_failed_after", max=max_retries, e=e))
                raise


# ── CEFR 级别分析（自然语言 → AI 推荐）──────────────────────

def analyze_level(user_desc: str) -> tuple[str, str]:
    """让 AI 根据用户自然语言描述判断 CEFR 级别。
    Returns: (level, reason)
    """
    prompt = f"""You are a CEFR level assessment expert for English language teaching.
Analyze the user's requirement and pick exactly one level from A1, A2, B1, B2, C1.

User description:
{user_desc}

Respond ONLY in this format:
LEVEL: <A1|A2|B1|B2|C1>
REASON: <one-sentence explanation in Chinese>

Guidelines:
- A1: absolute beginner; greetings, daily routines, very basic phrases
- A2: elementary; simple routine tasks, past events, simple directions
- B1: intermediate; travel situations, experiences/ambitions, give reasons
- B2: upper-intermediate; fluent interaction, complex topics, detailed text
- C1: advanced; flexible use for social/academic/professional purposes
"""
    response = client.chat.completions.create(
        model=config.AI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=256,
    )
    content = response.choices[0].message.content.strip()

    level_match = re.search(r'LEVEL:\s*(A1|A2|B1|B2|C1)', content, re.IGNORECASE)
    reason_match = re.search(r'REASON:\s*(.+)', content, re.IGNORECASE)

    level = level_match.group(1).upper() if level_match else "B1"
    reason = reason_match.group(1).strip() if reason_match else "Default selection"
    return level, reason


# ── 幻灯片内容生成 ─────────────────────────────────────────

def generate_slide_content(level: str, slide_meta: dict, blueprint_str: str, context: str, unit: dict = None, bp_fields: dict = None, max_retries: int = 3) -> dict:
    slide_type = slide_meta.get("type", "")
    if not slide_type:
        print(_("warn_slide_meta_no_type", meta=slide_meta))
        return {"type": "unknown", "error": "Missing type field in slide_meta", "raw": slide_meta}
    template = SLIDE_CONTENT_TEMPLATES.get(slide_type, "")
    design_rule = LEVEL_DESIGN_RULES.get(level, "")

    # Use pre-computed fields if available, otherwise extract from string
    if bp_fields:
        bp_vocab = bp_fields["vocab"]
        bp_funcs_str = bp_fields["funcs_str"]
        bp_vocab_str = bp_fields["vocab_str"]
        bp_topic = bp_fields["topic"]
        bp_lesson_task = bp_fields["lesson_task"]
    else:
        bp_vocab_match = _RE_VOCAB.findall(blueprint_str)
        bp_funcs_match = _RE_FUNCS.findall(blueprint_str)
        bp_vocab = [w.strip() for w in bp_vocab_match[0].split(",")] if bp_vocab_match else []
        bp_funcs_str = bp_funcs_match[0].strip() if bp_funcs_match else ""
        bp_vocab_str = bp_vocab_match[0].replace(",", ", ").strip() if bp_vocab_match else ""
        bp_topic = next(
            (line.replace("Topic:", "").strip() for line in blueprint_str.splitlines() if line.startswith("Topic:")),
            ""
        )
        bp_lesson_task = next(
            (line.replace("This Lesson Task (speaking):", "").strip()
             for line in blueprint_str.splitlines() if line.startswith("This Lesson Task (speaking):")),
            ""
        )

    vocab_lock = ""
    if slide_type.startswith("useful_language"):
        words = slide_meta.get("key_points") or bp_vocab
        if words:
            n_words = len(words)
            vocab_lock = f"""VOCABULARY LOCK — MANDATORY, NO EXCEPTIONS:
You MUST teach EXACTLY {n_words} word(s): {words}
The "words" array in the JSON MUST contain EXACTLY {n_words} entries — one entry per word above.
Do NOT teach fewer words. Do NOT add extra words.
The "word" field in each entry MUST exactly match one of: {words}
Teaching a different number of words or using different words is a critical error.
"""
    elif slide_type == "conversation_builder":
        funcs = slide_meta.get("key_points") or (bp_funcs_str.split("/") if bp_funcs_str else [])
        if funcs:
            vocab_lock = f"""FUNCTIONAL LANGUAGE LOCK — MANDATORY, NO EXCEPTIONS:
You MUST base the linkers/phrases on these exact functional language items: {funcs}
Do NOT invent new phrases. Use only what is listed above.
"""
    elif slide_type == "warm_up":
        topic_hint = bp_topic or slide_meta.get("key_points", [""])[0]
        if topic_hint:
            vocab_lock = f"""WARM-UP TOPIC LOCK — MANDATORY:
This warm-up MUST be about: "{topic_hint}"
The question and starters MUST directly relate to this topic.
Do NOT generate questions about unrelated topics (phone apps, technology, etc.) unless they are part of this topic.

WARM-UP SINGLE QUESTION RULE — MANDATORY:
The "question" field MUST contain EXACTLY ONE question. Do NOT put two or more questions.
WRONG: "What do you think about X? If you could Y, would you Z?"
CORRECT: "What is the first thing that comes to your mind when you hear about X?"
Keep it short, open-ended, and easy to answer in 2-3 sentences. The warm-up must finish in under 3 minutes.
"""
    elif slide_type == "scenario":
        if bp_lesson_task:
            topic_hint = bp_topic or ""
            vocab_lock = f"""SCENARIO TASK LOCK — MANDATORY:
The scenario role-play MUST exactly follow this lesson task description:
"{bp_lesson_task}"
Set the roles (role_a, role_b), problem, mission, and start according to the above task.
Do NOT invent a different scenario topic, setting, or role-play situation.
ROLE CONSISTENCY — MANDATORY: The role_b description MUST be logically consistent with the problem and mission. For example, if the problem involves a "software partnership", role_b must be a "software vendor", NOT a "logistics vendor". Every detail in role_a, role_b, problem, mission, and start must refer to the SAME business/situation context.
TOPIC CONSISTENCY — MANDATORY: The scenario MUST stay within the same real-world context as the rest of this lesson: "{topic_hint}". Do NOT switch to an unrelated context (e.g. do NOT switch from travel planning to workplace/office scenarios, or from family topics to business topics).
"""
    elif slide_type == "wrap_up":
        if bp_vocab_str or bp_funcs_str:
            vocab_lock = f"""WRAP-UP RECAP LOCK — MANDATORY:
The "recap" array MUST contain EXACTLY these three items, in this format:
1. "vocab: {bp_vocab_str}"  ← list ALL vocabulary words from this lesson exactly as shown
2. "chunk: {bp_funcs_str}"  ← list ALL functional language phrases exactly as shown (these are the actual spoken chunks taught, NOT a description of the lesson task)
3. "skill: [one sentence describing the communicative skill practiced today]"
CRITICAL: The "chunk" entry MUST be the actual phrases (e.g. "I suggest we... / How about we... / I would recommend..."), NOT a description of what the student did in the task. Copy the functional language phrases exactly from the blueprint.
Do NOT omit any word or phrase from the recap. Do NOT substitute lesson task descriptions for actual phrases.

FINAL TASK SCOPE LOCK — MANDATORY:
The "final_task" field is a QUICK VERBAL SUMMARY — completable in under 30 seconds. It is NOT a new role-play, debate, or extended activity.
It MUST only use language explicitly taught in THIS lesson (vocabulary: {bp_vocab_str} / chunks: {bp_funcs_str}).
Do NOT assign a new scenario, debate, or task that requires more than 30 seconds.
Do NOT introduce new roles, characters, or situations not already covered in this lesson.
WRONG: "Participate in a formal debate where you argue for X against a traditional Saudi CEO..."
WRONG: "Role-play a full negotiation with your manager about..."
CORRECT: "In one sentence, tell me: which phrase from today would you use if [brief situation]?"
CORRECT: "Use one of today's chunks to respond to: [short prompt related to {bp_topic}]."
"""
    elif slide_type == "practice":
        topic_hint = bp_topic or slide_meta.get("key_points", [""])[0]
        if topic_hint:
            vocab_lock = f"""PRACTICE TOPIC LOCK — MANDATORY:
The practice slide MUST stay on topic: "{topic_hint}"
The teacher_question and student_guide frames MUST directly relate to this topic.
Do NOT switch to an unrelated topic (remote work, technology in general, etc.) unless the topic above specifically mentions it.
"""

    prompt = f"""
{TEACHER_PROFILE_NOTE}

LESSON DESIGN APPROACH FOR {level}:
{design_rule}

{vocab_lock}
You are generating a {slide_type} slide for a {level} ESL lesson.

Lesson blueprint: {blueprint_str}
Slide key points: {slide_meta.get('key_points', [])}
Context from previous slides: {context}

{template}

RULES:
- Output ONLY valid JSON, no markdown, no explanation
- Instructions must be simple enough for a B1-B2 Filipino teacher to follow immediately
- Max 3-4 interaction points per slide — this is a 25-minute lesson
- No large blocks of text to read aloud
- Follow the {level} design approach above
- NO leaked answers in check questions
- Do NOT use markdown formatting (**, __, ##, etc.) in any text fields — plain text only
- VOCABULARY: Only teach words explicitly listed in the blueprint vocabulary section
- TITLE LOCK: Do NOT rename slide titles. Use the exact title specified in the template (e.g. "Useful Language (Part 1)", "Useful Language (Part 2)", "Let's Practice", "Conversation Builder", etc.)
- CCQ QUALITY: For useful_language slides, "check" questions must be open-ended Wh- or choice questions — NEVER Yes/No questions
- EMOJI COMPLIANCE: NEVER use these emojis in any field: 🎂 🍰 🎁 🎄 🎅 🍺 🍻 🍷 🍸 🍹 🍾 🐷 🥓 🐖 💋 👙 🩲 🩳 🃏. Use neutral alternatives (e.g. for age/time use 📅 or 🔢, for celebration use ⭐ or 🌟).
- TITLE UNIT FIELD: The "unit" field in the title slide MUST describe the OVERALL UNIT objective (what students can do by the end of the whole unit), NOT the individual lesson objective. Copy it from the blueprint "Unit Objective" field exactly.
- PRACTICE SCAFFOLDING: The student_guide in practice slides MUST only contain sentence frames explicitly taught in the conversation_builder of THIS lesson. Do NOT add extra phrases not covered in this lesson.
- MIDDLE EAST COMPLIANCE (ABSOLUTE RED LINE): NEVER use any of the following in any field: "playing God", "play God", "act of God", "God's will", "Allah's will", "haram", "halal", "infidel", "kafir", "jihad", "pork", "alcohol", "beer", "wine", "liquor", "dating", "boyfriend", "girlfriend", "romance", "sex", "sexual", "nude", "Israel", "Zionist", "gay", "lesbian", "homosexual", "evolution", "Darwin", or references to non-Islamic religions (church, cross, Bible, rabbi, Buddha, Christmas). Replace any such expression with neutral ethical language (e.g. replace "playing God" with "crossing ethical boundaries"). ALSO: Do NOT invent or discuss controversial local government policies of any specific country.
- MOVIE/MEDIA EXAMPLES: When giving example movies or TV shows, ONLY use family-friendly globally recognized titles (e.g. Spider-Man, The Lion King, Avatar). NEVER use R-rated or violent titles (e.g. John Wick, Deadpool). NEVER use "romance movie" or "love story" as a genre example — use "comedy" or "documentary" instead.
- POLITICAL SENSITIVITY (ABSOLUTE RED LINE): NEVER invent or discuss controversial government policies, tax laws, or political decisions attributed to a specific country (especially Saudi Arabia, UAE, or any Middle East nation). Do NOT create scenarios involving "viral rumors about government policy", "controversial new laws", or political unrest. Use generic/global contexts instead (e.g. "a local company" instead of "Saudi businesses", "a new industry regulation" instead of "a new government tax policy").

Generate the JSON now.
"""
    expected_words = []
    if slide_type.startswith("useful_language"):
        expected_words = slide_meta.get("key_points") or bp_vocab
        expected_words = [w.strip().lower() for w in expected_words if w.strip()]

    # Per-slide-type token budget — avoids paying for 8192 on every call
    _TOKEN_BUDGET = {
        "title": 512, "warm_up": 1536, "wrap_up": 2048,
        "useful_language_1": 2048, "useful_language_2": 2048,
        "conversation_builder": 2560,
        "practice": 3072, "scenario": 3072,
    }
    slide_max_tokens = _TOKEN_BUDGET.get(slide_type, 2048)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.AI_TEMPERATURE,
                max_tokens=slide_max_tokens,
            )
            raw = response.choices[0].message.content
            if not raw or not raw.strip():
                raise ValueError("Empty response from API")
            raw = _strip_fences(raw.strip())
            if not raw:
                raise ValueError("Empty content after stripping fences")
            result = json.loads(raw)

            if expected_words and slide_type.startswith("useful_language"):
                taught = []
                words_data = result.get("words", [])
                for w in words_data:
                    if isinstance(w, dict):
                        taught.append(w.get("word", "").strip().lower())
                hallucinated = [w for w in taught if w and w not in expected_words]
                missing = [w for w in expected_words if w not in taught]
                if hallucinated or missing:
                    issues = []
                    if hallucinated:
                        issues.append(f"hallucinated words: {hallucinated}")
                    if missing:
                        issues.append(f"missing words: {missing}")
                    print(_("vocab_lock_issues", issues=", ".join(issues)))
                    if attempt < max_retries - 1:
                        print(_("vocab_lock_retry"))
                        extra_note = f"VOCAB LOCK VIOLATION on previous attempt:"
                        if hallucinated:
                            extra_note += f" Words {hallucinated} are NOT in the required list."
                        if missing:
                            extra_note += f" Words {missing} were MISSING — you must include ALL {len(expected_words)} words."
                        prompt_strict = prompt.replace(
                            "VOCABULARY LOCK — MANDATORY, NO EXCEPTIONS:",
                            f"{extra_note}\nVOCABULARY LOCK — MANDATORY, NO EXCEPTIONS:"
                        )
                        prompt = prompt_strict
                        continue
                    else:
                        print(_("vocab_lock_max"))
                        # Python force-inject: ensure every expected word has an entry
                        words_data = result.get("words", [])
                        taught_words = [w.get("word", "").strip().lower() for w in words_data if isinstance(w, dict)]
                        for missing_word in missing:
                            if missing_word not in taught_words:
                                words_data.append({
                                    "word": missing_word,
                                    "emoji": "📝",
                                    "definition": f"[auto-injected] {missing_word}",
                                    "example": f"Please review the definition of '{missing_word}'.",
                                    "check": f"Can you use '{missing_word}' in a sentence?"
                                })
                                print(_("vocab_lock_force", word=missing_word))
                        # Remove hallucinated words
                        if hallucinated:
                            words_data = [w for w in words_data if w.get("word", "").strip().lower() not in hallucinated]
                            print(_("vocab_lock_removed", words=hallucinated))
                        result["words"] = words_data

            return result

        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(_("warn_retry", attempt=attempt+1, max=max_retries, e=e))
            else:
                raise
        except Exception as e:
            # Handle 429 rate limit and other transient errors with backoff
            is_rate_limit = "429" in str(e) or "rate" in str(e).lower() or "upstream" in str(e).lower()
            if attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(_("warn_slide_gen", attempt=attempt+1, type=type(e).__name__, wait=wait))
                time.sleep(wait)
            else:
                raise


def _extract_blueprint_vocab(blueprint: str | dict) -> tuple[list[str], list[str]]:
    """Extract vocabulary and functional language from blueprint (str or dict)."""
    if isinstance(blueprint, dict):
        vocab = blueprint.get("vocabulary", [])
        fl = blueprint.get("functional_language", [])
        funcs = fl if isinstance(fl, list) else [w.strip() for w in fl.split("/") if w.strip()]
        return vocab, funcs
    vocab, funcs = [], []
    for line in blueprint.splitlines():
        if line.startswith("Vocabulary:"):
            vocab = [w.strip() for w in line.replace("Vocabulary:", "").split(",") if w.strip()]
        elif line.startswith("Functional Language:"):
            funcs = [w.strip() for w in line.replace("Functional Language:", "").split("/") if w.strip()]
    return vocab, funcs


def _fix_outline_key_points(outline: list[dict], vocab: list[str], funcs: list[str]) -> list[dict]:
    """Force-inject blueprint vocab into useful_language key_points and funcs into conversation_builder.
    AI output is never trusted for these fields — Python is the authoritative source of truth.
    """
    ul_slides = [s for s in outline if s.get("type", "").startswith("useful_language")]
    ul1, ul2 = _split_vocab(vocab)
    parts = [ul1, ul2] if ul2 else [ul1]
    for slide, assigned in zip(ul_slides, parts):
        if assigned:
            old = slide.get("key_points", [])
            slide["key_points"] = assigned
            if old != assigned:
                print(_("vocab_fix", stype=slide.get('type',''), old=old, new=assigned))
    for slide in outline:
        if slide.get("type") == "conversation_builder" and funcs:
            old = slide.get("key_points", [])
            slide["key_points"] = funcs
            if old != funcs:
                print(_("func_fix", old=old, new=funcs))
    return outline


def generate_all_slides(level: str, blueprint: str | dict, unit: dict = None) -> list[dict]:
    if isinstance(blueprint, dict) and unit is None:
        raise ValueError("unit parameter required when blueprint is a dict")

    # Normalize once: compute blueprint_str and structured fields at entry
    if isinstance(blueprint, dict):
        blueprint_str = lesson_to_blueprint(blueprint, unit)
        n = blueprint.get("lesson_number", "")
        lesson_name = blueprint.get("lesson_name", "")
        bp_fields = {
            "vocab": blueprint.get("vocabulary", []),
            "funcs_str": " / ".join(blueprint["functional_language"]) if isinstance(blueprint.get("functional_language"), list) else blueprint.get("functional_language", ""),
            "vocab_str": ", ".join(blueprint.get("vocabulary", [])),
            "topic": blueprint.get("topic", ""),
            "lesson_task": blueprint.get("lesson_task", ""),
            # Title slide fields — sourced from unit outline, never trusted from AI slide-level outline
            "lesson_number": n,
            "lesson_name": lesson_name,
            "lesson_label": f"Lesson {n}: {lesson_name}" if n and lesson_name else lesson_name,
            "objective": blueprint.get("objective", ""),
            "unit_name": unit.get("overarching_objective", "") if unit else "",
        }
    else:
        blueprint_str = blueprint
        bp_vocab_match = _RE_VOCAB.findall(blueprint)
        bp_funcs_match = _RE_FUNCS.findall(blueprint)
        # Parse lesson label from blueprint string: "Lesson L3/6: Dividing the Responsibilities"
        lesson_label = ""
        objective = ""
        for line in blueprint.splitlines():
            if line.startswith("Lesson L"):
                # "Lesson L3/6: Dividing the Responsibilities" -> "Lesson 3: Dividing the Responsibilities"
                rest = line[len("Lesson L"):]  # e.g. "3/6: Dividing the Responsibilities"
                num_part = rest.split("/")[0] if "/" in rest else ""
                name_part = rest.split(": ", 1)[1] if ": " in rest else rest
                lesson_label = f"Lesson {num_part}: {name_part}" if num_part else name_part
            elif line.startswith("This Lesson Objective:"):
                objective = line.replace("This Lesson Objective:", "").strip()
        bp_fields = {
            "vocab": [w.strip() for w in bp_vocab_match[0].split(",")] if bp_vocab_match else [],
            "funcs_str": bp_funcs_match[0].strip() if bp_funcs_match else "",
            "vocab_str": bp_vocab_match[0].replace(",", ", ").strip() if bp_vocab_match else "",
            "topic": next((line.replace("Topic:", "").strip() for line in blueprint.splitlines() if line.startswith("Topic:")), ""),
            "lesson_task": next((line.replace("This Lesson Task (speaking):", "").strip() for line in blueprint.splitlines() if line.startswith("This Lesson Task (speaking):")), ""),
            "lesson_label": lesson_label,
            "objective": objective,
            "unit_name": "",
        }

    vocab = bp_fields["vocab"]
    funcs_list = [w.strip() for w in bp_fields["funcs_str"].split("/") if w.strip()] if bp_fields["funcs_str"] else []
    outline = generate_outline(level, blueprint_str, max_retries=3)

    if vocab:
        outline = _fix_outline_key_points(outline, vocab, funcs_list)

    print(_("gen_slide_content"))

    slides = [None] * len(outline)
    failed_indices = []

    def _gen(i, meta):
        try:
            stype = meta.get("type", "")
            if not stype:
                print(_("warn_slide_missing_type", i=i+1, meta=meta))
                return i, {"type": "unknown", "error": "Missing type field", "raw": meta}, None
            print(_("generating_slide", i=i+1, total=len(outline), stype=stype))
            # Title slide: build directly from blueprint metadata — NEVER trust AI slide-level outline
            if stype == "title":
                title_slide = {
                    "type": "title",
                    "unit": bp_fields.get("unit_name", ""),
                    "lesson": bp_fields.get("lesson_label", ""),
                    "objective": bp_fields.get("objective", ""),
                    "emoji": "🎯",
                }
                return i, title_slide, None
            return i, generate_slide_content(level, meta, blueprint_str, blueprint_str, bp_fields=bp_fields), None
        except Exception as e:
            print(_("warn_slide_failed", i=i+1, e=e))
            return i, None, e

    with ThreadPoolExecutor(max_workers=_PARALLEL_WORKERS) as executor:
        for i, slide, _unused in [f.result() for f in [executor.submit(_gen, i, m) for i, m in enumerate(outline)]]:
            if slide:
                slides[i] = slide
            else:
                failed_indices.append(i)

    if failed_indices:
        print(_("retrying_failed", n=len(failed_indices)))
        for i in failed_indices:
            meta = outline[i]
            stype = meta.get("type", "")
            if not stype:
                print(_("warn_skip_retry_no_type", i=i+1))
                continue
            print(_("retry_slide", i=i+1, total=len(outline), stype=stype))
            try:
                slides[i] = generate_slide_content(level, meta, blueprint_str, blueprint_str, bp_fields=bp_fields, max_retries=3)
                print(_("retry_ok"))
            except Exception as e:
                print(_("retry_error", e=e))

    # ── Check for permanently failed slides ──
    permanently_failed = [(i, outline[i].get('type','UNKNOWN')) for i in range(len(outline)) if slides[i] is None]
    if permanently_failed:
        failed_types = [t for _unused, t in permanently_failed]
        # Critical modules that cannot be missing
        critical_types = {"useful_language_1", "conversation_builder", "practice", "scenario", "wrap_up"}
        missing_critical = [t for t in failed_types if t in critical_types]
        if missing_critical:
            raise RuntimeError(
                f"CRITICAL: {len(permanently_failed)} slide(s) failed permanently after all retries: "
                f"{failed_types}. Missing critical module(s): {missing_critical}. "
                f"Lesson cannot be used — aborting."
            )
        else:
            print(_("warn_noncritical", n=len(permanently_failed), types=failed_types))
            print(_("warn_lesson_incomplete"))

    # Force-correct slide titles — AI may rename slides regardless of TITLE LOCK prompt.
    for slide in slides:
        stype = slide.get("type") if slide else None
        if stype and stype in TITLE_MAP:
            correct_title = TITLE_MAP[stype]
            if slide.get("title") != correct_title:
                print(_("title_fix", stype=stype, old=slide.get('title'), new=correct_title))
                slide["title"] = correct_title

    final_slides = [s for s in slides if s is not None]
    final_types = {s.get("type") for s in final_slides}
    expected_count = len(outline)
    actual_count = len(final_slides)
    if actual_count < expected_count:
        missing_types = [outline[i].get('type', 'UNKNOWN') for i in range(len(outline)) if slides[i] is None]
        print(_("warn_missing_slides", actual=actual_count, expected=expected_count, types=missing_types))
    return final_slides


# ── 内容润色 ───────────────────────────────────────────────

def _polish_single_slide(slide: dict, max_retries: int = 2) -> dict:
    """Polish a single slide's text content. Returns original slide on any failure."""
    slide_json = json.dumps(slide, indent=2, ensure_ascii=False)
    prompt = _POLISH_PROMPT_TEMPLATE.replace("{{SLIDE_JSON}}", slide_json)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=4096,
            )
            raw = response.choices[0].message.content
            if not raw or not raw.strip():
                raise ValueError("Empty response from API")
            raw = _strip_fences(raw.strip())
            if not raw:
                raise ValueError("Empty content after stripping fences")
            polished = json.loads(raw)
            if polished.get("type") != slide.get("type"):
                raise ValueError(f"Type changed: {slide.get('type')} → {polished.get('type')}")
            return polished
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 5 * (attempt + 1)
                print(_("warn_polish_retry", attempt=attempt+1, max=max_retries, type=type(e).__name__, msg=e, wait=wait))
                time.sleep(wait)
            else:
                raise


def polish_content(slides: list[dict]) -> list[dict]:
    print(_("polishing"))

    results = [None] * len(slides)
    failed = []

    def _polish(i, slide):
        try:
            return i, _polish_single_slide(slide), None
        except Exception as e:
            return i, None, e

    with ThreadPoolExecutor(max_workers=_PARALLEL_WORKERS) as executor:
        for i, polished, err in [f.result() for f in [executor.submit(_polish, i, s) for i, s in enumerate(slides)]]:
            if polished is not None:
                results[i] = polished
            else:
                print(_("warn_polish_failed", i=i+1, err=err))
                results[i] = slides[i]
                failed.append(i)

    if not failed:
        print(_("ok_polish_all"))
    else:
        print(_("ok_polish_partial", ok=len(slides)-len(failed), total=len(slides)))

    return results


# ── Unit 规划 ──────────────────────────────────────────────

def chat_unit_planning(level: str, unit_desc: str) -> list[dict]:
    print("\n" + "="*60)
    print(_("unit_planning_chat"))
    print(_("proceed_hint"))
    print("="*60)

    messages = [
        {"role": "system", "content": UNIT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Level: {level}\n\nUnit description:\n{unit_desc}"},
    ]

    while True:
        print(_("ai_thinking"))
        response = client.chat.completions.create(
            model=config.AI_MODEL, messages=messages, temperature=0.7, max_tokens=1024,
        )
        ai_reply = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": ai_reply})
        print(_("ai_prefix", reply=ai_reply))

        ai_ready = "[READY TO GENERATE]" in ai_reply
        user_input = input(_("you_prompt")).strip() or "proceed"

        messages.append({"role": "user", "content": user_input})
        if user_input.lower() in PROCEED_KEYWORDS or ai_ready:
            print(_("starting_outline"))
            break

    return messages


def generate_unit_outline(messages: list[dict], level: str) -> dict:
    import time as _time
    print(_("generating_outline_json"))
    gen_messages = messages + [{"role": "user", "content": UNIT_OUTLINE_INSTRUCTION}]

    debug_dir = Path(config.OUTPUT_DIR) / "_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    with open(debug_dir / "unit_chat_history.json", "w", encoding="utf-8") as f:
        json.dump(gen_messages, f, ensure_ascii=False, indent=2)
    print(_("debug_saved", path=debug_dir / "unit_chat_history.json"))

    # Retry on timeout/429/truncated JSON — up to 3 full attempts
    outline = None
    for _attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=config.AI_MODEL, messages=gen_messages, temperature=0.7, max_tokens=8192,
            )
            raw = response.choices[0].message.content.strip()
        except Exception as e:
            if _attempt < 2:
                _wait = 30 * (_attempt + 1)
                print(_("retry_outline", type=type(e).__name__, wait=_wait))
                _time.sleep(_wait)
                continue
            else:
                raise

        with open(debug_dir / "unit_outline_raw.txt", "w", encoding="utf-8") as f:
            f.write(raw)
        print(_("debug_saved", path=debug_dir / "unit_outline_raw.txt"))

        raw_clean = _strip_fences(raw)
        try:
            outline = json.loads(raw_clean)
            break  # success
        except json.JSONDecodeError:
            # Try to extract the first complete JSON object (handles trailing text)
            try:
                decoder = json.JSONDecoder()
                outline, _idx = decoder.raw_decode(raw_clean.strip())
                break  # success
            except json.JSONDecodeError as e2:
                if _attempt < 2:
                    _wait = 10 * (_attempt + 1)
                    print(_("retry_outline_truncated", e=e2, wait=_wait))
                    _time.sleep(_wait)
                else:
                    print(_("error_outline_parse", e=e2, raw=raw[:500]))
                    raise e2

    if outline is None:
        raise RuntimeError("generate_unit_outline: no valid outline after retries")

    if "lessons" not in outline or not outline["lessons"]:
        raise ValueError("Unit outline missing or empty 'lessons'")
    if not outline.get("level"):
        outline["level"] = level

    with open(debug_dir / "unit_outline_parsed.json", "w", encoding="utf-8") as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)

    print(_("unit_outline_summary", name=outline.get('unit_name','?'), n=len(outline['lessons'])))
    return outline


def lesson_to_blueprint(lesson: dict, unit: dict) -> str:
    vocab_str = ", ".join(lesson.get("vocabulary", []))
    n = lesson.get("lesson_number", "?")
    total = unit.get("total_lessons", "?")
    fl = lesson.get("functional_language", "")
    if isinstance(fl, list):
        fl_str = " / ".join(fl)
    else:
        fl_str = fl
    return (
        f"Lesson L{n}/{total}: {lesson.get('lesson_name','')}\n"
        f"Unit Goal: {unit.get('overarching_objective','')}\n"
        f"Final Task: {unit.get('final_task','')}\n"
        f"This Lesson Objective: {lesson.get('objective','')}\n"
        f"This Lesson Task (speaking): {lesson.get('lesson_task','')}\n"
        f"Vocabulary: {vocab_str}\n"
        f"Functional Language: {fl_str}\n"
        f"Topic: {lesson.get('topic','')}"
    )
