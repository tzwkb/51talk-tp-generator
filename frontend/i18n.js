const UI_I18N = {
  en: {
    brand: "Lesson Studio",
    hero_title: "Create AI-powered lesson materials in minutes",
    hero_sub: "Seamlessly generate unit outlines, interactive slides, and printable PDFs.",
    hero_cta: "+ Create New Unit",
    card_full_title: "Generate Full Unit",
    card_full_desc: "6-10 lessons with AI planning chat. Perfect for complete curriculums.",
    card_quick_title: "Quick Single Lesson",
    card_quick_desc: "Fast blueprint-to-slide generation. Bypass the session chat.",
    recent_title: "Recent Units",
    refresh: "Refresh",
    loading: "Loading...",
    loading_wait: "Please wait",
    no_units: "No units yet. Create your first one above.",
    load_error: "Failed to load units. Is the backend running?",
    just_now: "just now",
    minutes_ago: "m ago",
    hours_ago: "h ago",
    days_ago: "d ago",
    unknown: "unknown",
    lessons: "lessons",
    untitled: "Untitled",
    lang_switch: "AR",
    back_dashboard: "Back to Dashboard",
    wizard_title: "Unit Wizard",
    wizard_desc: "5-step generation flow is under construction.",
    quick_title: "Quick Single Lesson",
    quick_desc: "Fast blueprint generation is under construction.",
    wizard_step1_title: "Describe your teaching needs",
    level_selection: "Level Selection",
    unit_planning_chat: "Unit Planning Chat",
    generating_unit: "Generating Unit...",
    generation_complete: "Generation Complete",
    unit_files: "Unit Files",
    create_another: "Create Another",
    btn_back: "Back",
    btn_next: "Next \u2192",
    btn_generate: "Start Generation",
    analyzing: "AI is analyzing your description...",
    chat_placeholder: "Type your reply or click Proceed...",
    btn_proceed: "Proceed",
    preview: "Preview HTML",
    download: "Download",
    quick_level_label: "Target CEFR Level",
    quick_blueprint_label: "Lesson Blueprint",
    generate_material: "Generate Material",
    generating: "Generating...",
    ready: "Ready",
    please_enter_blueprint: "Please enter a blueprint."
  },
  ar: {
    brand: "استوديو الدروس",
    hero_title: "أنشئ مواد دروس مدعومة بالذكاء الاصطناعي في دقائق",
    hero_sub: "إنشاء مخططات الوحدات والشرائح التفاعلية وملفات PDF القابلة للطباعة بسلاسة.",
    hero_cta: "+ إنشاء وحدة جديدة",
    card_full_title: "إنشاء وحدة كاملة",
    card_full_desc: "6-10 دروس مع دردشة تخطيط بالذكاء الاصطناعي. مثالي للمناهج الكاملة.",
    card_quick_title: "درس سريع واحد",
    card_quick_desc: "إنشاء سريع من مخطط إلى شريحة. تخطي دردشة الجلسة.",
    recent_title: "الوحدات الأخيرة",
    refresh: "تحديث",
    loading: "جاري التحميل...",
    loading_wait: "يرجى الانتظار",
    no_units: "لا توجد وحدات بعد. أنشئ وحدةك الأولى أعلاه.",
    load_error: "فشل تحميل الوحدات. هل الخادم يعمل؟",
    just_now: "الآن",
    minutes_ago: "د",
    hours_ago: "س",
    days_ago: "ي",
    unknown: "غير معروف",
    lessons: "دروس",
    untitled: "بدون عنوان",
    lang_switch: "EN",
    back_dashboard: "العودة إلى لوحة التحكم",
    wizard_title: "معالج الوحدة",
    wizard_desc: "تدفق الإنشاء بخطوات قيد الإنشاء.",
    quick_title: "درس سريع واحد",
    quick_desc: "الإنشاء السريع للمخطط قيد الإنشاء.",
    wizard_step1_title: "صف احتياجاتك التعليمية",
    level_selection: "اختيار المستوى",
    unit_planning_chat: "دردشة تخطيط الوحدة",
    generating_unit: "جاري إنشاء الوحدة...",
    generation_complete: "اكتمل الإنشاء",
    unit_files: "ملفات الوحدة",
    create_another: "إنشاء وحدة أخرى",
    btn_back: "رجوع",
    btn_next: "\u2190 التالي",
    btn_generate: "بدء التوليد",
    analyzing: "الذكاء الاصطناعي يحلل وصفك...",
    chat_placeholder: "اكتب ردك أو انقر على متابعة...",
    btn_proceed: "متابعة",
    preview: "معاينة HTML",
    download: "تحميل",
    quick_level_label: "المستوى المستهدف CEFR",
    quick_blueprint_label: "مخطط الدرس",
    generate_material: "إنشاء المادة",
    generating: "جاري الإنشاء...",
    ready: "جاهز",
    please_enter_blueprint: "يرجى إدخال مخطط الدرس."
  }
};

function t(key) {
  const lang = window.__currentLang || 'en';
  return UI_I18N[lang]?.[key] ?? UI_I18N['en']?.[key] ?? key;
}

function applyI18n(lang) {
  window.__currentLang = lang;
  document.documentElement.lang = lang;
  document.body.dir = lang === 'ar' ? 'rtl' : 'ltr';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const val = UI_I18N[lang][key];
    if (!val) return;
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      el.placeholder = val;
    } else {
      el.innerHTML = val;
    }
  });

  const switchBtn = document.getElementById('lang-switch');
  if (switchBtn) switchBtn.textContent = UI_I18N[lang].lang_switch;

  localStorage.setItem('appLang', lang);
  window.dispatchEvent(new CustomEvent('langchange', { detail: lang }));
}

function toggleLang() {
  const current = localStorage.getItem('appLang') || 'en';
  applyI18n(current === 'en' ? 'ar' : 'en');
}

function initI18n() {
  const saved = localStorage.getItem('appLang') || 'en';
  applyI18n(saved);
}

document.addEventListener('DOMContentLoaded', initI18n);
