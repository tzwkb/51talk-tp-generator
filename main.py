# ============================================================
# main.py — 51Talk Lesson Generator
# ============================================================

import json
from pathlib import Path

from config import OUTPUT_DIR, LEVELS
from content_processor import (
    generate_all_slides, polish_content,
    chat_unit_planning, generate_unit_outline, lesson_to_blueprint,
)
from slide_renderer import build_html, export_pdf
from utils import safe_name, create_unit_dir, ensure_debug_dir, generate_lesson


def _select_level() -> str | None:
    print("\nSelect lesson level:")
    for i, level in enumerate(LEVELS, 1):
        print(f"  {i}. {level}")
    choice = input("Enter number (1-5): ").strip()
    if not choice.isdigit() or int(choice) not in range(1, 6):
        print("Invalid choice.")
        return None
    return LEVELS[int(choice) - 1]


def run_single_lesson():
    print("\n" + "="*60)
    print("  51Talk Lesson Generator (Single Lesson Mode)")
    print("="*60)

    level = _select_level()
    if not level:
        return

    print(f"\nEnter lesson blueprint ({level} level):")
    print("(Include: Unit/Lesson name, vocabulary, grammar, topic)")
    blueprint = input("Blueprint: ").strip()
    if not blueprint:
        print("Blueprint cannot be empty.")
        return

    out = Path(OUTPUT_DIR)
    out.mkdir(exist_ok=True)
    name = safe_name(blueprint)

    try:
        slides = generate_all_slides(level, blueprint)
        slides = polish_content(slides)

        json_path = out / f"{name}_{level}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(slides, f, ensure_ascii=False, indent=2)
        print(f"\n  [OK] JSON: {json_path}")

        html = build_html(slides)
        html_path = out / f"{name}_{level}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  [OK] HTML: {html_path}")

        export_pdf(str(html_path), str(out / f"{name}_{level}.pdf"))
        print(f"\n  [DONE] Output: {out.resolve()}")

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        import traceback
        traceback.print_exc()

    print("="*60 + "\n")


def run_unit():
    print("\n" + "="*60)
    print("  51Talk Unit Generator (6-10 Lessons)")
    print("="*60)

    level = _select_level()
    if not level:
        return

    print(f"\nDescribe your unit ({level} level):")
    print("Include: unit theme, number of lessons, any specific vocab or grammar goals.")
    unit_desc = input("> ").strip()
    if not unit_desc:
        print("Unit description cannot be empty.")
        return

    messages = chat_unit_planning(level, unit_desc)

    try:
        outline = generate_unit_outline(messages, level)
    except Exception as e:
        print(f"\n[ERROR] Could not generate unit outline: {e}")
        return

    unit_dir = create_unit_dir(outline, level)

    with open(unit_dir / "unit_outline.json", "w", encoding="utf-8") as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Unit outline saved: {unit_dir / 'unit_outline.json'}")

    total = len(outline["lessons"])
    print(f"\n{'='*60}")
    print(f"  Unit: {outline.get('overarching_objective','')[:60]} (Level: {level})  |  {total} lessons")
    for lesson in outline["lessons"]:
        print(f"    L{lesson['lesson_number']}: {lesson['lesson_name']}")
    print(f"{'='*60}\n")

    debug_dir = ensure_debug_dir()
    success_count = 0

    for lesson in outline["lessons"]:
        n = lesson.get("lesson_number", "?")
        name = lesson.get("lesson_name", "")
        print(f"\n{'─'*60}")
        print(f"  Lesson {n}/{total}: {name}")
        print(f"  Progress: [{'█' * n}{'░' * (total - n)}] {n}/{total}")
        print(f"{'─'*60}")

        blueprint = lesson_to_blueprint(lesson, outline)
        print(f"  Blueprint:\n{blueprint}\n")
        with open(debug_dir / f"lesson_{n}_blueprint.txt", "w", encoding="utf-8") as f:
            f.write(blueprint)

        if generate_lesson(level, lesson, outline, unit_dir):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"  DONE: {success_count}/{total} lessons generated.")
    print(f"  Output: {unit_dir.resolve()}")
    print(f"{'='*60}\n")

    run_qa = input("Run QA tests on this unit? (y/n): ").strip().lower()
    if run_qa == "y":
        from qa_tester import test_outline, test_lessons, append_qa_log
        outline_result = test_outline(unit_dir)
        lesson_results = test_lessons(unit_dir)
        append_qa_log(unit_dir, outline_result, lesson_results)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  51Talk Lesson Generator")
    print("="*60)
    print("\nSelect mode:")
    print("  1. Generate single lesson")
    print("  2. Generate full unit (6-10 lessons)")

    mode = input("\nEnter mode (1 or 2): ").strip()

    if mode == "1":
        run_single_lesson()
    elif mode == "2":
        run_unit()
    else:
        print("Invalid choice.")
