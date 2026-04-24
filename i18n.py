# ============================================================
# i18n.py — Locale loader (reads l10n/*.json)
# ============================================================

import json
from pathlib import Path

_L10N_DIR = Path(__file__).parent / "l10n"
_LOCALES: dict[str, dict[str, str]] = {}


def _load_locale(code: str) -> dict[str, str]:
    path = _L10N_DIR / f"{code}.json"
    if not path.exists():
        raise FileNotFoundError(f"Locale file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_loaded(code: str) -> None:
    if code not in _LOCALES:
        _LOCALES[code] = _load_locale(code)


def _(key: str, **kwargs) -> str:
    """Return bilingual EN/AR string."""
    _ensure_loaded("en")
    _ensure_loaded("ar")
    en = _LOCALES["en"].get(key, key)
    ar = _LOCALES["ar"].get(key, "")
    if kwargs:
        en = en.format(**kwargs)
        ar = ar.format(**kwargs)
    if ar:
        return f"{en}\n  {ar}"
    return en
