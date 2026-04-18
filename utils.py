# ============================================================
# utils.py — Shared utilities for 51Talk Lesson Generator
# ============================================================

import re
import time
from datetime import datetime
from pathlib import Path

from config import OUTPUT_DIR


# ── Shared constants ──────────────────────────────────────

DEBUG_DIR = Path(OUTPUT_DIR) / "_debug"


# ── Text helpers ──────────────────────────────────────────

def safe_name(text: str, max_len: int = 40) -> str:
    """Sanitize text for use as filename: keep ASCII alphanums and hyphens only."""
    s = re.sub(r'[^a-zA-Z0-9\-]+', '_', text[:max_len])
    return s.strip('_')


# ── Retry helper ──────────────────────────────────────────

def retry_with_backoff(fn, *, max_retries: int = 3, base_wait: int = 30, retry_on=None):
    """Call fn() with linear backoff retry on failure.

    Args:
        fn: Callable to execute (no args). Use lambda for parameterized calls.
        max_retries: Maximum number of attempts.
        base_wait: Base wait time in seconds (multiplied by attempt number).
        retry_on: Optional function(exception) -> bool. If provided, only retry
                  when it returns True. If None, retry on all exceptions.
    Returns:
        The return value of fn() on success.
    Raises:
        The last exception if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            should_retry = retry_on(e) if retry_on else True
            if should_retry and attempt < max_retries - 1:
                wait = base_wait * (attempt + 1)
                print(f"  [RETRY] {type(e).__name__}, waiting {wait}s ({attempt+1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise


# ── Unit directory creation ───────────────────────────────

def create_unit_dir(outline: dict, level: str) -> Path:
    """Create and return the unit output directory."""
    unit_name_safe = safe_name(
        outline.get("unit_name") or outline.get("overarching_objective", "Unit")
    )
    timestamp = datetime.now().strftime("%m%d_%H%M")
    unit_dir = Path(OUTPUT_DIR) / f"Unit_{level}_{timestamp}_{unit_name_safe}"
    unit_dir.mkdir(parents=True, exist_ok=True)
    return unit_dir


def ensure_debug_dir() -> Path:
    """Ensure _debug directory exists and return its path."""
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    return DEBUG_DIR


# ── Lesson generation pipeline ────────────────────────────

def generate_lesson(level: str, lesson: dict, outline: dict, unit_dir: Path) -> bool:
    """Generate a single lesson: slides → polish → JSON → HTML → PDF.
    Returns True on success, False on failure after 3 attempts.
    """
    from content_processor import generate_all_slides, polish_content
    from slide_renderer import build_html, export_pdf
    import json

    n = lesson.get("lesson_number", "?")
    name = lesson.get("lesson_name", "")

    for attempt in range(3):
        try:
            print(f"  [1/4] Generating slides..." + (f" (retry {attempt})" if attempt else ""))
            slides = generate_all_slides(level, lesson, outline)

            print(f"  [2/4] Polishing content...")
            slides = polish_content(slides)

            base_name = f"L{n}_{safe_name(name)}_{level}"

            print(f"  [3/4] Saving JSON...")
            json_path = unit_dir / f"{base_name}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(slides, f, ensure_ascii=False, indent=2)

            print(f"  [4/4] Rendering HTML + PDF...")
            html = build_html(slides)
            html_path = unit_dir / f"{base_name}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            export_pdf(str(html_path), str(unit_dir / f"{base_name}.pdf"))

            print(f"  [DONE] Lesson {n} completed!")
            return True

        except Exception as e:
            if attempt < 2:
                print(f"  [WARN] Attempt {attempt+1} failed: {e}, retrying...")
            else:
                print(f"  [FAIL] Lesson {n} failed after 3 attempts: {e}")
                import traceback
                traceback.print_exc()

    return False
