# ============================================================
# auto_runner.py — Non-interactive runner for autonomous loops
# Usage: python auto_runner.py
# Randomly picks level + topic, generates a full unit, runs QA
# ============================================================

import json
import random
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import LEVELS, AI_MODEL, client
from content_processor import (
    generate_unit_outline, lesson_to_blueprint,
    UNIT_SYSTEM_PROMPT,
)
from slide_renderer import build_html, export_pdf
from qa_tester import test_outline, test_lessons, append_qa_log
from utils import safe_name, retry_with_backoff, create_unit_dir, ensure_debug_dir, generate_lesson


# ── Unit planning (non-interactive) ──────────────────────

def _auto_chat_unit_planning(level: str, unit_desc: str) -> list[dict]:
    """Non-interactive version of chat_unit_planning: sends description then 'proceed'."""
    messages = [
        {"role": "system", "content": UNIT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Level: {level}\n\nUnit description:\n{unit_desc}"},
    ]

    def _call():
        response = client.chat.completions.create(
            model=AI_MODEL, messages=messages, temperature=0.7, max_tokens=1024,
        )
        return response.choices[0].message.content.strip()

    ai_reply = retry_with_backoff(_call)
    messages.append({"role": "assistant", "content": ai_reply})
    messages.append({"role": "user", "content": "proceed"})
    return messages


# ── Random topic pool (one per CEFR level) ────────────────

RANDOM_TOPICS = {
    "A1": [
        "Introduce yourself and your family",
        "Talk about your daily routine",
        "Order food at a restaurant",
        "Ask for directions in a new city",
        "Talk about your hobbies",
        "Describe your favorite food and drinks",
        "Talk about the weather and seasons",
        "Go shopping for clothes",
        "Make a phone call to book an appointment",
        "Describe your classroom or office",
        "Talk about your favorite holiday or celebration",
        "Describe people you know (appearance and personality)",
        "Talk about transportation you use every day",
        "Visit the doctor and describe how you feel",
        "Talk about your weekend plans",
    ],
    "A2": [
        "Make plans with a friend",
        "Talk about your job and workplace",
        "Describe your home and neighborhood",
        "Shopping and returning items",
        "Talk about past experiences and travel",
        "Describe a memorable event from your childhood",
        "Give and follow simple instructions for a recipe",
        "Check in at a hotel and ask about facilities",
        "Talk about your education and school life",
        "Discuss your favorite TV show or movie",
        "Compare life in the city vs the countryside",
        "Report a problem to a landlord or building manager",
        "Plan a birthday party or small event",
        "Talk about sports and fitness activities",
        "Describe a typical workday from morning to evening",
    ],
    "B1": [
        "Handle a flight delay or travel disruption",
        "Express opinions in a team meeting",
        "Describe a problem and suggest solutions",
        "Talk about health and lifestyle habits",
        "Make a complaint and negotiate a resolution",
        "Discuss the advantages and disadvantages of social media",
        "Give advice to a friend about a career change",
        "Describe an important decision you made and why",
        "Talk about environmental issues in your city",
        "Explain a process or how something works",
        "Discuss cultural differences you have experienced",
        "Plan a group trip and divide responsibilities",
        "Talk about money management and saving habits",
        "Discuss work-life balance and stress management",
        "Describe a news story and give your opinion",
    ],
    "B2": [
        "Pitch a business idea to an investor",
        "Discuss ethical dilemmas in the workplace",
        "Lead a performance review conversation",
        "Negotiate a contract or deal",
        "Discuss current events and give opinions",
        "Debate the impact of AI on employment",
        "Discuss the pros and cons of studying abroad",
        "Handle a difficult conversation with a colleague",
        "Analyze a marketing campaign and suggest improvements",
        "Discuss generational differences in the workplace",
        "Debate whether universities should be free",
        "Present and defend a project proposal to a skeptical boss",
        "Discuss the future of electric vehicles and green energy",
        "Navigate a salary negotiation with HR",
        "Discuss the role of media in shaping public opinion",
    ],
    "C1": [
        "Debate the pros and cons of remote work culture",
        "Give a persuasive presentation on a social issue",
        "Navigate a cross-cultural business negotiation",
        "Discuss abstract concepts in philosophy or ethics",
        "Analyse and critique a business case study",
        "Debate the ethics of genetic engineering and designer babies",
        "Discuss the tension between economic growth and environmental protection",
        "Argue for or against universal basic income",
        "Critique a government policy and propose alternatives",
        "Discuss the impact of globalization on local cultures",
        "Debate whether privacy or security should take priority in the digital age",
        "Analyze the causes and solutions of wealth inequality",
        "Discuss the future of education: traditional vs online vs AI-powered",
        "Debate corporate social responsibility vs profit maximization",
        "Discuss the psychological effects of social media on society",
    ],
}


def auto_run():
    level = random.choice(LEVELS)
    topic = random.choice(RANDOM_TOPICS[level])

    print("\n" + "="*60)
    print("  AUTO RUNNER — 51Talk Unit Generator")
    print("="*60)
    print(f"  Level : {level}")
    print(f"  Topic : {topic}")
    print("="*60 + "\n")

    messages = _auto_chat_unit_planning(level, topic)

    try:
        outline = generate_unit_outline(messages, level)
    except Exception as e:
        print(f"[ERROR] Could not generate unit outline: {e}")
        return None

    unit_dir = create_unit_dir(outline, level)

    with open(unit_dir / "unit_outline.json", "w", encoding="utf-8") as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)
    print(f"[OK] Unit outline saved: {unit_dir / 'unit_outline.json'}")

    debug_dir = ensure_debug_dir()
    total = len(outline["lessons"])
    success_count = 0

    for lesson in outline["lessons"]:
        n = lesson.get("lesson_number", "?")
        name = lesson.get("lesson_name", "")
        print(f"\n{'-'*60}")
        print(f"  Lesson {n}/{total}: {name}")
        print(f"{'-'*60}")

        blueprint = lesson_to_blueprint(lesson, outline)
        with open(debug_dir / f"lesson_{n}_blueprint.txt", "w", encoding="utf-8") as f:
            f.write(blueprint)

        if generate_lesson(level, lesson, outline, unit_dir):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"  Generation complete: {success_count}/{total} lessons")
    print(f"  Output: {unit_dir.resolve()}")
    print(f"{'='*60}\n")

    print("  Running QA tests automatically...\n")
    outline_result = test_outline(unit_dir)
    lesson_results = test_lessons(unit_dir)
    append_qa_log(unit_dir, outline_result, lesson_results)

    return unit_dir


if __name__ == "__main__":
    auto_run()
