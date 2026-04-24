# ============================================================
# i18n.py — Bilingual EN/AR CLI strings
# ============================================================

_STRINGS: dict[str, tuple[str, str]] = {
    # main.py
    "select_mode": ("Select mode:", "اختر الوضع:"),
    "mode_single": ("  1. Generate single lesson", "  1. إنشاء درس واحد"),
    "mode_unit": ("  2. Generate full unit (6-10 lessons)", "  2. إنشاء وحدة كاملة (6-10 دروس)"),
    "enter_mode": ("Enter mode (1 or 2):", "أدخل الوضع (1 أو 2):"),
    "invalid_choice": ("Invalid choice.", "اختيار غير صالح."),
    "title_main": ("  51Talk Lesson Generator", "  51Talk مولد الدروس"),
    "title_single": ("  51Talk Lesson Generator (Single Lesson Mode)", "  51Talk مولد الدروس (وضع الدرس الواحد)"),
    "ask_desc": ("Describe your teaching needs (topic, target student level, context — AI will recommend the level):", "صِف احتياجاتك التعليمية (الموضوع، مستوى الطلاب المستهدف، السياق — سيوصي الذكاء الاصطناعي بالمستوى تلقائيًا):"),
    "ai_analyzing": ("[AI analyzing...]", "[جاري التحليل بالذكاء الاصطناعي...]"),
    "ai_recommended": ("  AI recommends level: {level}", "  المستوى الموصى به: {level}"),
    "ai_reason": ("  Reason: {reason}", "  السبب: {reason}"),
    "fallback_manual": ("  Fallback to manual selection:", "  الرجوع إلى الاختيار اليدوي:"),
    "enter_number_15": ("  Enter number (1-5): ", "  أدخل الرقم (1-5): "),
    "confirm_level": ("  Confirm (Enter=use {level} / type 1-5 or A1/C1 to change): ", "  تأكيد (Enter=استخدام {level} / أدخل 1-5 أو A1/C1 لتعديل): "),
    "desc_empty": ("Description cannot be empty.", "لا يمكن أن يكون الوصف فارغًا."),
    "enter_blueprint": ("Enter lesson blueprint ({level} level):", "أدخل مخطط الدرس (مستوى {level}):"),
    "blueprint_hint": ("(Include: Unit/Lesson name, vocabulary, grammar, topic)", "(تضمين: اسم الوحدة/الدرس، المفردات، القواعد، الموضوع)"),
    "blueprint_prompt": ("Blueprint: ", "المخطط: "),
    "blueprint_empty": ("Blueprint cannot be empty.", "لا يمكن أن يكون المخطط فارغًا."),
    "sanitizer_subs": ("  [SANITIZER] {n} substitution(s): {subs}", "  [المعقّم] {n} استبدال(ات): {subs}"),
    "ok_json": ("  [OK] JSON: {path}", "  [موافق] JSON: {path}"),
    "ok_html": ("  [OK] HTML: {path}", "  [موافق] HTML: {path}"),
    "done_output": ("  [DONE] Output: {path}", "  [تم] الإخراج: {path}"),
    "error": ("  [ERROR] {e}", "  [خطأ] {e}"),
    "title_unit": ("  51Talk Unit Generator (6-10 Lessons)", "  51Talk مولد الوحدات (6-10 دروس)"),
    "describe_unit": ("Describe your unit ({level} level):", "صِف وحدة التعلم الخاصة بك (مستوى {level}):"),
    "unit_hint": ("Include: unit theme, number of lessons, any specific vocab or grammar goals.", "تضمين: موضوع الوحدة، عدد الدروس، أي أهداف مفردات أو قواعد محددة."),
    "unit_desc_empty": ("Unit description cannot be empty.", "لا يمكن أن يكون وصف الوحدة فارغًا."),
    "error_outline": ("[ERROR] Could not generate unit outline: {e}", "[خطأ] تعذر إنشاء مخطط الوحدة: {e}"),
    "ok_outline_saved": ("[OK] Unit outline saved: {path}", "[موافق] تم حفظ مخطط الوحدة: {path}"),
    "unit_header": ("  Unit: {obj} (Level: {level})  |  {total} lessons", "  الوحدة: {obj} (المستوى: {level})  |  {total} دروس"),
    "lesson_header": ("  Lesson {n}/{total}: {name}", "  الدرس {n}/{total}: {name}"),
    "progress": ("  Progress: [{bar}] {n}/{total}", "  التقدم: [{bar}] {n}/{total}"),
    "blueprint_label": ("  Blueprint:\n{bp}\n", "  المخطط:\n{bp}\n"),
    "done_lessons": ("  DONE: {success}/{total} lessons generated.", "  تم: {success}/{total} دروس تم إنشاؤها."),
    "output_path": ("  Output: {path}", "  الإخراج: {path}"),
    "run_qa_prompt": ("Run QA tests on this unit? (y/n): ", "تشغيل اختبارات ضمان الجودة على هذه الوحدة؟ (y/n): "),

    # content_processor.py
    "gen_outline": ("[1/3] Generating outline ({level} level)...", "[1/3] جاري إنشاء المخطط (مستوى {level})..."),
    "warn_empty_retry": ("  [WARN] Empty response, retrying ({attempt}/{max})...", "  [تحذير] استجابة فارغة، إعادة المحاولة ({attempt}/{max})..."),
    "debug_saved": ("  [DEBUG] Saved to {path}", "  [تصحيح] تم الحفظ في {path}"),
    "outline_generated": ("  Outline generated: {n} slides", "  تم إنشاء المخطط: {n} شريحة"),
    "warn_attempt_failed": ("  [WARN] Attempt {attempt} failed ({type}: {msg}), waiting {wait}s...", "  [تحذير] المحاولة {attempt} فشلت ({type}: {msg})، الانتظار {wait} ثانية..."),
    "error_failed_after": ("  [ERROR] Failed after {max} attempts: {e}", "  [خطأ] فشل بعد {max} محاولات: {e}"),
    "vocab_lock_issues": ("    [VOCAB LOCK] Issues detected — {issues}", "    [قفل المفردات] تم اكتشاف مشكلات — {issues}"),
    "vocab_lock_retry": ("    [VOCAB LOCK] Retrying with stricter prompt...", "    [قفل المفردات] إعادة المحاولة بتعليمات أكثر صرامة..."),
    "vocab_lock_max": ("    [VOCAB LOCK] Max retries reached — force-injecting missing words", "    [قفل المفردات] تم استنفاد المحاولات — إجبار إدراج الكلمات المفقودة"),
    "vocab_lock_force": ("    [VOCAB LOCK] Force-injected: '{word}'", "    [قفل المفردات] تم الإدراج بالإجبار: '{word}'"),
    "vocab_lock_removed": ("    [VOCAB LOCK] Removed hallucinated: {words}", "    [قفل المفردات] تمت إزالة الوهمية: {words}"),
    "warn_retry": ("    [WARN] Retry {attempt}/{max}: {e}", "    [تحذير] إعادة المحاولة {attempt}/{max}: {e}"),
    "warn_slide_gen": ("    [WARN] Slide gen attempt {attempt} failed ({type}), waiting {wait}s...", "    [تحذير] محاولة إنشاء الشريحة {attempt} فشلت ({type})، الانتظار {wait} ثانية..."),
    "vocab_fix": ("  [VOCAB FIX] {stype}: {old} → {new}", "  [إصلاح المفردات] {stype}: {old} → {new}"),
    "func_fix": ("  [FUNC FIX] conversation_builder: {old} → {new}", "  [إصلاح الوظائف] conversation_builder: {old} → {new}"),
    "gen_slide_content": ("\n[2/3] Generating slide content (parallel)...", "\n[2/3] جاري إنشاء محتوى الشرائح (بالتوازي)..."),
    "generating_slide": ("  Generating slide {i}/{total}: {stype}", "  جاري إنشاء الشريحة {i}/{total}: {stype}"),
    "warn_slide_failed": ("    [WARN] Slide {i} failed: {e}", "    [تحذير] فشلت الشريحة {i}: {e}"),
    "retrying_failed": ("\n  Retrying {n} failed slides...", "\n  إعادة محاولة {n} شرائح فاشلة..."),
    "retry_slide": ("  Retry slide {i}/{total}: {stype}", "  إعادة محاولة الشريحة {i}/{total}: {stype}"),
    "retry_ok": ("    [OK] Retry succeeded", "    [موافق] نجحت إعادة المحاولة"),
    "retry_error": ("    [ERROR] Retry failed: {e}", "    [خطأ] فشلت إعادة المحاولة: {e}"),
    "warn_noncritical": ("\n  [WARN] {n} non-critical slide(s) failed permanently: {types}", "\n  [تحذير] {n} شريحة غير حرجة فشلت بشكل دائم: {types}"),
    "warn_lesson_incomplete": ("         Lesson will proceed but may be incomplete.", "         سيستمر الدرس ولكن قد يكون غير مكتمل."),
    "title_fix": ("  [TITLE FIX] {stype}: \"{old}\" → \"{new}\"", "  [إصلاح العنوان] {stype}: \"{old}\" → \"{new}\""),
    "warn_missing_slides": ("\n  [WARN] Returning {actual}/{expected} slides (missing: {types})", "\n  [تحذير] إرجاع {actual}/{expected} شريحة (مفقودة: {types})"),
    "warn_polish_retry": ("  [WARN] Polish retry {attempt}/{max} ({type}: {msg}), waiting {wait}s...", "  [تحذير] إعادة محاولة التلميع {attempt}/{max} ({type}: {msg})، الانتظار {wait} ثانية..."),
    "polishing": ("\n[3/3] Polishing content...", "\n[3/3] جاري تلميع المحتوى..."),
    "warn_polish_failed": ("  [WARN] Slide {i} polish failed ({err}), using original", "  [تحذير] فشل تلميع الشريحة {i} ({err})، استخدام النسخة الأصلية"),
    "ok_polish_all": ("  [OK] Polish applied successfully", "  [موافق] تم تطبيق التلميع بنجاح"),
    "ok_polish_partial": ("  [OK] Polish applied ({ok}/{total} slides polished)", "  [موافق] تم تطبيق التلميع ({ok}/{total} شريحة تم تلميعها)"),
    "unit_planning_chat": ("  Unit Planning Chat", "  دردشة تخطيط الوحدة"),
    "proceed_hint": ("  Type 'proceed' (or ok/go/start/yes) when ready to generate.", "  اكتب 'proceed' (أو ok/go/start/yes) عندما تكون جاهزًا للإنشاء."),
    "ai_thinking": ("\n[AI thinking...]\n", "\n[الذكاء الاصطناعي يفكر...]\n"),
    "ai_prefix": ("AI: {reply}\n", "الذكاء الاصطناعي: {reply}\n"),
    "you_prompt": ("You: ", "أنت: "),
    "starting_outline": ("\n[Starting outline generation...]\n", "\n[بدء إنشاء المخطط...]\n"),
    "generating_outline_json": ("[Generating unit outline JSON...]", "[جاري إنشاء مخطط الوحدة JSON...]"),
    "retry_outline": ("  [RETRY] generate_unit_outline failed ({type}), waiting {wait}s...", "  [إعادة المحاولة] فشل generate_unit_outline ({type})، الانتظار {wait} ثانية..."),
    "retry_outline_truncated": ("  [RETRY] unit outline JSON truncated ({e}), waiting {wait}s...", "  [إعادة المحاولة] مخطط الوحدة JSON مقطوع ({e})، الانتظار {wait} ثانية..."),
    "error_outline_parse": ("  [ERROR] Failed to parse unit outline JSON after 3 attempts: {e}\n  Raw (first 500):\n{raw}", "  [خطأ] فشل تحليل مخطط الوحدة JSON بعد 3 محاولات: {e}\n  النص الخام (أول 500):\n{raw}"),
    "unit_outline_summary": ("  Unit outline: {name} | {n} lessons", "  مخطط الوحدة: {name} | {n} دروس"),

    # utils.py
    "retry_wait": ("  [RETRY] {type}, waiting {wait}s ({attempt}/{max})...", "  [إعادة المحاولة] {type}، الانتظار {wait} ثانية ({attempt}/{max})..."),
    "step_gen_slides": ("  [1/4] Generating slides...{retry}", "  [1/4] جاري إنشاء الشرائح...{retry}"),
    "step_polish": ("  [2/4] Polishing content...", "  [2/4] جاري تلميع المحتوى..."),
    "step_save_json": ("  [3/4] Saving JSON...", "  [3/4] جاري حفظ JSON..."),
    "step_render": ("  [4/4] Rendering HTML + PDF...", "  [4/4] جاري تصيير HTML + PDF..."),
    "done_lesson": ("  [DONE] Lesson {n} completed!", "  [تم] اكتمل الدرس {n}!"),
    "fail_lesson": ("  [FAIL] Lesson {n} failed after 3 attempts: {e}", "  [فشل] فشل الدرس {n} بعد 3 محاولات: {e}"),

    # auto_runner.py
    "auto_runner_title": ("  AUTO RUNNER — 51Talk Unit Generator", "  التشغيل التلقائي — 51Talk مولد الوحدات"),
    "level_label": ("  Level : {level}", "  المستوى : {level}"),
    "topic_label": ("  Topic : {topic}", "  الموضوع : {topic}"),
    "gen_complete": ("  Generation complete: {success}/{total} lessons", "  اكتمل الإنشاء: {success}/{total} دروس"),
    "running_qa_auto": ("  Running QA tests automatically...\n", "  تشغيل اختبارات ضمان الجودة تلقائيًا...\n"),

    # qa_tester.py
    "test1_title": ("  TEST 1: Unit Outline QA", "  الاختبار 1: ضمان جودة مخطط الوحدة"),
    "error_outline_not_found": ("  [ERROR] unit_outline.json not found in {path}", "  [خطأ] لم يتم العثور على unit_outline.json في {path}"),
    "prog_issues_found": ("\n  ⚙️ Programmatic check found issues:", "\n  ⚙️ اكتشاف الفحص الآلي مشكلات:"),
    "prog_pass": ("\n  ⚙️ Programmatic check: ✅ All passed", "\n  ⚙️ الفحص الآلي: ✅ جميعها نجحت"),
    "ai_eval_outline": ("  [AI] Evaluating outline...", "  [الذكاء الاصطناعي] جاري تقييم المخطط..."),
    "test2_title": ("  TEST 2: Lesson Content QA (ALL lessons)", "  الاختبار 2: ضمان جودة محتوى الدرس (جميع الدروس)"),
    "error_no_lesson_json": ("  [ERROR] No lesson JSON files found", "  [خطأ] لم يتم العثور على ملفات JSON للدروس"),
    "prog_lesson_issues": ("\n  ⚙️ {fname} programmatic check found issues:", "\n  ⚙️ {fname} اكتشاف الفحص الآلي مشكلات:"),
    "prog_lesson_pass": ("\n  ⚙️ {fname} programmatic check: ✅ All passed", "\n  ⚙️ {fname} الفحص الآلي: ✅ جميعها نجحت"),
    "ai_eval_lesson": ("\n  [AI] Evaluating {fname}...", "\n  [الذكاء الاصطناعي] جاري تقييم {fname}..."),
    "rate_limit": ("  [RATE LIMIT] 429 error, waiting {wait}s before retry ({attempt}/{max})...", "  [حدود المعدل] خطأ 429، الانتظار {wait} ثانية قبل إعادة المحاولة ({attempt}/{max})..."),
    "ok_saved": ("  [OK] Saved: {path}", "  [موافق] تم الحفظ: {path}"),
    "warn_excel_open": ("\n  [WARN] qa_log.xlsx is open in Excel. Saved to: {name}", "\n  [تحذير] qa_log.xlsx مفتوح في Excel. تم الحفظ في: {name}"),
    "ok_qa_log": ("\n  [OK] QA log updated: {path}", "\n  [موافق] تم تحديث سجل ضمان الجودة: {path}"),
    "result": ("  Result: {passed}", "  النتيجة: {passed}"),
    "unit_folder": ("\nUnit folder: {path}", "\nمجلد الوحدة: {path}"),
    "qa_complete": ("  QA complete. Results saved to _qa/ folder.", "  اكتمل ضمان الجودة. تم حفظ النتائج في مجلد _qa/."),

    # sanitizer.py
    "sanitizer_clean": ("[SANITIZER] {name}: clean", "[المعقّم] {name}: نظيف"),
    "sanitizer_usage": ("Usage: python sanitizer.py <lesson.json> [...]", "الاستخدام: python sanitizer.py <lesson.json> [...]"),

    # slide_renderer.py
    "ok_pdf_exported": ("  [OK] PDF exported: {path}", "  [موافق] تم تصدير PDF: {path}"),
    "warn_pdf_skip": ("  [WARN] PDF export skipped: playwright not installed", "  [تحذير] تم تخطي تصدير PDF: playwright غير مثبت"),
    "warn_pdf_fail": ("  [WARN] PDF export failed: {e}", "  [تحذير] فشل تصدير PDF: {e}"),
    "ok_pdf_flatten": ("  [OK] PDF flattened to image-based ({dpi} DPI)", "  [موافق] تم تحويل PDF إلى صورة ({dpi} DPI)"),
    "warn_flatten_skip": ("  [WARN] PDF flatten skipped: pymupdf not installed (pip install pymupdf)", "  [تحذير] تم تخطي تحويل PDF: pymupdf غير مثبت (pip install pymupdf)"),
    "warn_flatten_fail": ("  [WARN] PDF flatten failed: {e}", "  [تحذير] فشل تحويل PDF: {e}"),
}


def _(key: str, **kwargs) -> str:
    """Return bilingual EN/AR string."""
    en, ar = _STRINGS.get(key, (key, ""))
    if kwargs:
        en = en.format(**kwargs)
        ar = ar.format(**kwargs)
    if ar:
        return f"{en}\n  {ar}"
    return en
