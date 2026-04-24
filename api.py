# ============================================================
# api.py — FastAPI backend for 51Talk Lesson Generator
# ============================================================

import asyncio
import io
import json
import queue
import threading
import uuid
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import OUTPUT_DIR, LEVELS, AI_MODEL, client
from content_processor import (
    generate_unit_outline,
    analyze_level,
    UNIT_SYSTEM_PROMPT,
    PROCEED_KEYWORDS,
)
from utils import create_unit_dir, generate_lesson

# ── FastAPI app ─────────────────────────────────────────────

app = FastAPI(title="51Talk Lesson Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# ── Pydantic models ─────────────────────────────────────────

class AnalyzeLevelRequest(BaseModel):
    description: str


class AnalyzeLevelResponse(BaseModel):
    level: str
    reason: str


class PlanChatRequest(BaseModel):
    session_id: Optional[str] = None
    level: Optional[str] = None
    unit_desc: Optional[str] = None
    user_input: Optional[str] = None


class PlanChatResponse(BaseModel):
    session_id: str
    ai_reply: str
    ready_to_generate: bool


class GenerateUnitRequest(BaseModel):
    session_id: str


class LessonGenerateRequest(BaseModel):
    level: str
    blueprint: str


# ── Session store (in-memory) ───────────────────────────────

_sessions: dict[str, dict] = {}
_generate_lock = threading.Lock()


def _create_session(level: str, unit_desc: str) -> str:
    sid = str(uuid.uuid4())
    _sessions[sid] = {
        "level": level,
        "unit_desc": unit_desc,
        "messages": [
            {"role": "system", "content": UNIT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Level: {level}\n\nUnit description:\n{unit_desc}"},
        ],
        "created_at": datetime.now(),
        "ready": False,
    }
    return sid


def _get_session(sid: str) -> dict:
    if sid not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return _sessions[sid]


# ── Print → SSE adapter ─────────────────────────────────────

class LogInterceptor(io.TextIOBase):
    """Captures stdout writes and pushes them into a Queue as log events."""

    def __init__(self, q: queue.Queue):
        self.q = q
        self._buf = ""

    def write(self, s: str) -> int:
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self.q.put(("log", line))
        return len(s)

    def flush(self):
        if self._buf:
            self.q.put(("log", self._buf))
            self._buf = ""


# ── SSE generator helper ────────────────────────────────────

async def _sse_event_generator(q: queue.Queue):
    """Consume queue items and yield SSE formatted strings."""
    while True:
        try:
            item = await asyncio.to_thread(q.get, timeout=0.5)
            etype, data = item
            if etype == "log":
                yield f"event: log\ndata: {json.dumps({'line': data}, ensure_ascii=False)}\n\n"
            elif etype == "progress":
                yield f"event: progress\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
            elif etype == "complete":
                yield f"event: complete\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                break
            elif etype == "error":
                yield f"event: error\ndata: {json.dumps({'message': data}, ensure_ascii=False)}\n\n"
                break
        except queue.Empty:
            yield ":keepalive\n\n"


# ── API endpoints ───────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/analyze-level", response_model=AnalyzeLevelResponse)
async def analyze_level_endpoint(req: AnalyzeLevelRequest):
    level, reason = analyze_level(req.description)
    return {"level": level, "reason": reason}


@app.post("/api/unit/plan-chat", response_model=PlanChatResponse)
async def unit_plan_chat(req: PlanChatRequest):
    if not req.session_id:
        if not req.level or not req.unit_desc:
            raise HTTPException(status_code=400, detail="level and unit_desc required for first turn")
        sid = _create_session(req.level, req.unit_desc)
        session = _sessions[sid]
    else:
        session = _get_session(req.session_id)
        sid = req.session_id
        if req.user_input:
            session["messages"].append({"role": "user", "content": req.user_input})

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=session["messages"],
        temperature=0.7,
        max_tokens=1024,
    )
    ai_reply = response.choices[0].message.content.strip()
    session["messages"].append({"role": "assistant", "content": ai_reply})

    ai_ready = "[READY TO GENERATE]" in ai_reply
    user_ready = (req.user_input or "").lower() in PROCEED_KEYWORDS
    if ai_ready or user_ready:
        session["ready"] = True

    return {
        "session_id": sid,
        "ai_reply": ai_reply,
        "ready_to_generate": session["ready"],
    }


@app.post("/api/unit/generate")
async def unit_generate(req: GenerateUnitRequest):
    session = _get_session(req.session_id)
    if not session.get("ready"):
        raise HTTPException(status_code=400, detail="Session not ready for generation")

    q: queue.Queue = queue.Queue()

    def _worker():
        try:
            with _generate_lock:
                level = session["level"]
                messages = session["messages"]

                interceptor = LogInterceptor(q)
                with redirect_stdout(interceptor):
                    outline = generate_unit_outline(messages, level)

                unit_dir = create_unit_dir(outline, level)
                with open(unit_dir / "unit_outline.json", "w", encoding="utf-8") as f:
                    json.dump(outline, f, ensure_ascii=False, indent=2)

                total = len(outline["lessons"])
                q.put(("progress", {
                    "event": "start",
                    "total": total,
                    "unit_name": outline.get("overarching_objective", ""),
                }))

                success_count = 0
                for lesson in outline["lessons"]:
                    n = lesson.get("lesson_number", "?")
                    name = lesson.get("lesson_name", "")

                    q.put(("progress", {
                        "event": "progress",
                        "lesson": n,
                        "total": total,
                        "name": name,
                        "status": "generating",
                    }))

                    interceptor = LogInterceptor(q)
                    with redirect_stdout(interceptor):
                        ok = generate_lesson(level, lesson, outline, unit_dir)
                    interceptor.flush()

                    q.put(("progress", {
                        "event": "progress",
                        "lesson": n,
                        "total": total,
                        "name": name,
                        "status": "done" if ok else "failed",
                    }))
                    if ok:
                        success_count += 1

                files = []
                for f in sorted(unit_dir.iterdir()):
                    if f.is_file() and f.suffix in (".json", ".html", ".pdf"):
                        files.append({
                            "name": f.name,
                            "path": f"/static/outputs/{unit_dir.name}/{f.name}",
                            "type": f.suffix.lstrip("."),
                        })

                q.put(("complete", {
                    "unit_id": unit_dir.name,
                    "unit_name": outline.get("overarching_objective", ""),
                    "level": level,
                    "success": success_count,
                    "total": total,
                    "files": files,
                }))
        except Exception as e:
            q.put(("error", str(e)))

    threading.Thread(target=_worker, daemon=True).start()
    return StreamingResponse(_sse_event_generator(q), media_type="text/event-stream")


@app.post("/api/lesson/generate")
async def lesson_generate(req: LessonGenerateRequest):
    q: queue.Queue = queue.Queue()

    def _worker():
        try:
            from content_processor import generate_all_slides, polish_content
            from slide_renderer import build_html, export_pdf
            from sanitizer import sanitize_lesson
            from utils import safe_name

            out = Path(OUTPUT_DIR)
            out.mkdir(exist_ok=True)
            name = safe_name(req.blueprint)

            q.put(("progress", {"event": "start", "total": 1, "name": name}))

            interceptor = LogInterceptor(q)
            with redirect_stdout(interceptor):
                slides = generate_all_slides(req.level, req.blueprint)
                slides = polish_content(slides)
                slides, _san = sanitize_lesson(slides)

                json_path = out / f"{name}_{req.level}.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(slides, f, ensure_ascii=False, indent=2)

                html = build_html(slides)
                html_path = out / f"{name}_{req.level}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html)

                export_pdf(str(html_path), str(out / f"{name}_{req.level}.pdf"))
            interceptor.flush()

            files = []
            for ext in [".json", ".html", ".pdf"]:
                fpath = out / f"{name}_{req.level}{ext}"
                if fpath.exists():
                    files.append({
                        "name": fpath.name,
                        "path": f"/static/outputs/{fpath.name}",
                        "type": ext.lstrip("."),
                    })

            q.put(("complete", {
                "lesson_name": name,
                "level": req.level,
                "files": files,
            }))
        except Exception as e:
            q.put(("error", str(e)))

    threading.Thread(target=_worker, daemon=True).start()
    return StreamingResponse(_sse_event_generator(q), media_type="text/event-stream")


@app.get("/api/units")
async def list_units():
    out = Path(OUTPUT_DIR)
    if not out.exists():
        return []

    units = []
    for d in sorted(out.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if d.is_dir() and d.name.startswith("Unit_"):
            outline_path = d / "unit_outline.json"
            unit_name = d.name
            level = ""
            lessons_count = 0
            if outline_path.exists():
                try:
                    outline = json.loads(outline_path.read_text(encoding="utf-8"))
                    unit_name = outline.get("overarching_objective", d.name)
                    level = outline.get("level", "")
                    lessons_count = len(outline.get("lessons", []))
                except Exception:
                    pass

            files = []
            for f in sorted(d.iterdir()):
                if f.is_file() and f.suffix in (".json", ".html", ".pdf"):
                    files.append({
                        "name": f.name,
                        "path": f"/static/outputs/{d.name}/{f.name}",
                        "type": f.suffix.lstrip("."),
                    })

            units.append({
                "id": d.name,
                "name": unit_name,
                "level": level,
                "lessons_count": lessons_count,
                "created_at": datetime.fromtimestamp(d.stat().st_mtime).isoformat(),
                "files": files,
            })
    return units


@app.get("/api/units/{unit_id}/files")
async def unit_files(unit_id: str):
    unit_dir = Path(OUTPUT_DIR) / unit_id
    if not unit_dir.exists():
        raise HTTPException(status_code=404, detail="Unit not found")

    files = []
    for f in sorted(unit_dir.iterdir()):
        if f.is_file():
            files.append({
                "name": f.name,
                "path": f"/static/outputs/{unit_id}/{f.name}",
                "type": f.suffix.lstrip(".") or "unknown",
            })
    return {"unit_id": unit_id, "files": files}


# ── Entrypoint ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
