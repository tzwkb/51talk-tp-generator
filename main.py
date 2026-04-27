# ============================================================
# main.py — 51Talk Lesson Generator
# ============================================================

import json
from pathlib import Path

import config
from config import LEVELS
from content_processor import (
    generate_all_slides, polish_content,
    chat_unit_planning, generate_unit_outline, lesson_to_blueprint,
    analyze_level,
)
from slide_renderer import build_html, export_pdf
from utils import safe_name, create_unit_dir, ensure_debug_dir, generate_lesson
from i18n import _


def _select_level() -> tuple[str | None, str]:
    print(_("ask_desc"))
    user_desc = input("> ").strip()
    if not user_desc:
        print(_("desc_empty"))
        return None, ""

    print(_("ai_analyzing"))
    try:
        level, reason = analyze_level(user_desc)
        print(_("ai_recommended", level=level))
        print(_("ai_reason", reason=reason))
    except Exception as e:
        print(f"  [WARN] AI level analysis failed: {e}")
        level = None

    if level is None or level not in LEVELS:
        print(_("fallback_manual"))
        for i, lv in enumerate(LEVELS, 1):
            print(f"  {i}. {lv}")
        choice = input(_("enter_number_15")).strip()
        if not choice.isdigit() or int(choice) not in range(1, 6):
            print(_("invalid_choice"))
            return None, user_desc
        level = LEVELS[int(choice) - 1]
    else:
        confirm = input(_("confirm_level", level=level)).strip().upper()
        if confirm in LEVELS:
            level = confirm
        elif confirm.isdigit() and int(confirm) in range(1, 6):
            level = LEVELS[int(confirm) - 1]
        elif confirm != "":
            print(_("invalid_choice"))
            return None, user_desc

    return level, user_desc


def run_single_lesson():
    print("\n" + "="*60)
    print(_("title_single"))
    print("="*60)

    level, _unused = _select_level()
    if not level:
        return

    print(_("enter_blueprint", level=level))
    print(_("blueprint_hint"))
    blueprint = input(_("blueprint_prompt")).strip()
    if not blueprint:
        print(_("blueprint_empty"))
        return

    out = Path(config.OUTPUT_DIR)
    out.mkdir(exist_ok=True)
    name = safe_name(blueprint)

    try:
        slides = generate_all_slides(level, blueprint)
        slides = polish_content(slides)

        from sanitizer import sanitize_lesson
        slides, _san = sanitize_lesson(slides)
        if _san:
            print(_("sanitizer_subs", n=len(_san), subs="; ".join(_san)))

        json_path = out / f"{name}_{level}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(slides, f, ensure_ascii=False, indent=2)
        print(_("ok_json", path=json_path))

        html = build_html(slides)
        html_path = out / f"{name}_{level}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(_("ok_html", path=html_path))

        export_pdf(str(html_path), str(out / f"{name}_{level}.pdf"))
        print(_("done_output", path=out.resolve()))

    except Exception as e:
        print(_("error", e=e))
        import traceback
        traceback.print_exc()

    print("="*60 + "\n")


def run_unit():
    print("\n" + "="*60)
    print(_("title_unit"))
    print("="*60)

    level, unit_desc = _select_level()
    if not level:
        return

    if not unit_desc:
        print(_("describe_unit", level=level))
        print(_("unit_hint"))
        unit_desc = input("> ").strip()
        if not unit_desc:
            print(_("unit_desc_empty"))
            return

    messages = chat_unit_planning(level, unit_desc)

    try:
        outline = generate_unit_outline(messages, level)
    except Exception as e:
        print(_("error_outline", e=e))
        return

    unit_dir = create_unit_dir(outline, level)

    with open(unit_dir / "unit_outline.json", "w", encoding="utf-8") as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)
    print(_("ok_outline_saved", path=unit_dir / "unit_outline.json"))

    total = len(outline["lessons"])
    print(f"\n{'='*60}")
    obj = outline.get("overarching_objective", "")[:60]
    print(_("unit_header", obj=obj, level=level, total=total))
    for lesson in outline["lessons"]:
        print(f"    L{lesson['lesson_number']}: {lesson['lesson_name']}")
    print(f"{'='*60}\n")

    debug_dir = ensure_debug_dir()
    success_count = 0

    for lesson in outline["lessons"]:
        n = lesson.get("lesson_number", "?")
        name = lesson.get("lesson_name", "")
        print(f"\n{'─'*60}")
        print(_("lesson_header", n=n, total=total, name=name))
        bar = "█" * n + "░" * (total - n)
        print(_("progress", bar=bar, n=n, total=total))
        print(f"{'─'*60}")

        blueprint = lesson_to_blueprint(lesson, outline)
        print(_("blueprint_label", bp=blueprint))
        with open(debug_dir / f"lesson_{n}_blueprint.txt", "w", encoding="utf-8") as f:
            f.write(blueprint)

        if generate_lesson(level, lesson, outline, unit_dir):
            success_count += 1

    print(f"\n{'='*60}")
    print(_("done_lessons", success=success_count, total=total))
    print(_("output_path", path=unit_dir.resolve()))
    print(f"{'='*60}\n")

    run_qa = input(_("run_qa_prompt")).strip().lower()
    if run_qa == "y":
        from qa_tester import test_outline, test_lessons, append_qa_log
        outline_result = test_outline(unit_dir)
        lesson_results = test_lessons(unit_dir)
        append_qa_log(unit_dir, outline_result, lesson_results)


if __name__ == "__main__":
    print("\n" + "="*60)
    print(_("title_main"))
    print("="*60)
    print(_("select_mode"))
    print(_("mode_single"))
    print(_("mode_unit"))

    mode = input(_("enter_mode")).strip()

    if mode == "1":
        run_single_lesson()
    elif mode == "2":
        run_unit()
    else:
        print(_("invalid_choice"))
