"""
Hard post-processing: detect and replace cultural taboo content in lesson JSON.
Runs after AI generation, before QA. Logs all substitutions made.

Usage:
    from sanitizer import sanitize_lesson, sanitize_file
    cleaned_data, changes = sanitize_lesson(lesson_data)
    changes = sanitize_file("output/lesson.json")
"""

import json
import re
from pathlib import Path

# (regex_pattern, replacement, category)
# Order matters: multi-word patterns before single-word.
TABOO_RULES: list[tuple[str, str, str]] = [
    # Pork products — multi-word first
    (r"\bpork chop\b",   "chicken",         "pork"),
    (r"\bpork\b",        "chicken",         "pork"),
    (r"\bbacon\b",       "chicken",         "pork"),
    (r"\bham\b",         "chicken",         "pork"),
    (r"\bsausage\b",     "chicken",         "pork"),
    (r"\bpig\b",         "chicken",         "pork"),
    (r"\bribs\b",        "grilled chicken", "pork"),

    # Alcohol not already in SENSITIVE_PHRASES
    (r"\bcocktail\b",    "juice",           "alcohol"),
    (r"\bchampagne\b",   "sparkling water", "alcohol"),

    # Revealing clothing
    (r"\bbikini\b",      "casual clothing", "clothing"),
    (r"\blingerie\b",    "clothing",        "clothing"),

    # Celebrations / non-Islamic holidays — multi-word first
    (r"\bbirthday cake\b",  "celebration cake",    "holiday"),
    (r"\bbirthday party\b", "gathering",            "holiday"),
    (r"\bbirthday\b",       "milestone",            "holiday"),
    (r"\bchristmas tree\b", "decorative tree",      "holiday"),
    (r"\bchristmas\b",      "end-of-year holiday",  "holiday"),
    (r"\bhalloween\b",      "cultural festival",    "holiday"),
    (r"\beaster\b",         "spring holiday",       "holiday"),
    (r"\bvalentine\b",      "appreciation day",     "holiday"),
    (r"\bsanta\b",          "gift-giver",           "holiday"),

    # Non-Islamic religion symbols
    (r"\bchurch\b",         "place of worship",    "religion"),
    (r"\bbible\b",          "scripture",           "religion"),
    (r"\brabbi\b",          "religious leader",    "religion"),
    (r"\bbuddha\b",         "historical figure",   "religion"),
]

_COMPILED = [
    (re.compile(pat, re.IGNORECASE), repl, cat)
    for pat, repl, cat in TABOO_RULES
]


def _sanitize_string(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    for pattern, replacement, category in _COMPILED:
        new_text, n = pattern.subn(replacement, text)
        if n > 0:
            changes.append(f"[{category}] {pattern.pattern!r} x{n} → '{replacement}'")
            text = new_text
    return text, changes


def _walk(obj) -> tuple[object, list[str]]:
    if isinstance(obj, str):
        return _sanitize_string(obj)
    if isinstance(obj, list):
        result, all_changes = [], []
        for item in obj:
            cleaned, changes = _walk(item)
            result.append(cleaned)
            all_changes.extend(changes)
        return result, all_changes
    if isinstance(obj, dict):
        result, all_changes = {}, []
        for k, v in obj.items():
            cleaned, changes = _walk(v)
            result[k] = cleaned
            all_changes.extend(changes)
        return result, all_changes
    return obj, []


def sanitize_lesson(lesson_data: list[dict]) -> tuple[list[dict], list[str]]:
    """Sanitize a lesson slide list. Returns (cleaned_data, list_of_changes)."""
    return _walk(lesson_data)


def sanitize_file(json_path: str | Path) -> list[str]:
    """Read a lesson JSON file, sanitize it, overwrite in place. Returns list of changes."""
    path = Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    cleaned, changes = sanitize_lesson(data)
    if changes:
        path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[SANITIZER] {path.name}: {len(changes)} substitution(s)")
        for c in changes:
            print(f"  {c}")
    else:
        print(f"[SANITIZER] {path.name}: clean")
    return changes


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python sanitizer.py <lesson.json> [...]")
        sys.exit(1)
    for arg in sys.argv[1:]:
        sanitize_file(arg)
