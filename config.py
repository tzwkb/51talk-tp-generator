# ============================================================
# config.py — 51Talk 课件生成器配置文件
# ============================================================
from pathlib import Path
from openai import OpenAI

# ── AI 模型配置 ──────────────────────────────────────────────
import os
_env = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env):
    for _line in open(_env, encoding="utf-8"):
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

AI_BASE_URL    = os.environ.get("AI_BASE_URL", "https://api.vectorengine.ai/v1")
AI_API_KEY     = os.environ.get("AI_API_KEY", "")
AI_MODEL       = os.environ.get("AI_MODEL", "gemini-3.1-pro-preview")
AI_TEMPERATURE = float(os.environ.get("AI_TEMPERATURE", "1.0"))

if not AI_API_KEY:
    raise RuntimeError("AI_API_KEY not set. Copy .env.example to .env and fill in your key.")

# ── OpenAI client (dynamic proxy) ───────────────────────────
class _ClientProxy:
    _real = None
    def __getattr__(self, name):
        if self._real is None:
            self._real = OpenAI(base_url=AI_BASE_URL, api_key=AI_API_KEY, timeout=120.0)
        return getattr(self._real, name)

client = _ClientProxy()

def update_client():
    """Recreate the underlying OpenAI client with current config values."""
    client._real = OpenAI(base_url=AI_BASE_URL, api_key=AI_API_KEY, timeout=120.0)

# ── 品牌配置 ──────────────────────────────────────────────────
LOGO_TEXT   = "51Talk"                       # 右上角 Logo 文字
LOGO_SUB    = "Adults"                       # Logo 副标题（如 "Adults" / "Kids"）

# ── 输出配置 ──────────────────────────────────────────────────
OUTPUT_DIR  = str(Path(__file__).parent / "output")
OUTPUT_HTML = True                           # 是否同时保存 HTML（方便调试样式）
OUTPUT_PDF  = True                           # 是否导出 PDF

# ── 课件配置 ──────────────────────────────────────────────────
LEVELS = ["A1", "A2", "B1", "B2", "C1"]     # 支持的 CEFR 等级

# ── 样式配置（51Talk 风格色彩体系）─────────────────────────────
THEME = {
    "bg_color":           "#ffffff",   # 页面背景
    "title_color":        "#1a1a2e",   # 标题颜色
    "accent_color":       "#2563eb",   # 蓝色强调（关键词/边框）
    "card_bg":            "#f3f4f6",   # 灰色卡片背景
    "info_card_bg":       "#dbeafe",   # 浅蓝信息卡背景
    "blockquote_border":  "#2563eb",   # 左边框引用块颜色
    "logo_bg":            "#2563eb",   # Logo 背景色
    "logo_text_color":    "#facc15",   # Logo 文字颜色（黄色）
    "font_family":        "Arial, 'Helvetica Neue', sans-serif",
    "title_size":         "28px",
    "subtitle_size":      "18px",
    "body_size":          "16px",
}
