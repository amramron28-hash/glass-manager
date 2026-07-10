# config.py

# ===== المعايير الثلاثة الافتراضية لزجاج حماية الشاشة =====
DEFAULT_SCREEN_SIZE = "6.5"       # المعيار 1: المقاس الرقمي الافتراضي لزجاج الحماية
DEFAULT_PANEL_NAME = "Notch"      # المعيار 2: شكل الشاشة الفعلي (نوتش، ثقب، أو منحنية)
DEFAULT_SENSOR_NAME = "Virtual"   # المعيار 3: مستشعر التقارب لضمان عدم الحجب

# ===== إعدادات النظام والتحديث =====
STATS_REFRESH_TTL = 3             # وقت صلاحية الكاش المؤقت للإحصائيات بالثواني
REFRESH_INTERVAL_SEC = 30         # فاصل التحديث التلقائي للواجهة (تم رفعه من 5 إلى 30 ثانية لتقليل الحمل)

# ===== ألوان الواجهة =====
COLORS = {
    "exact": "#2ecc71",
    "plus": "#3498db",
    "minus": "#e67e22",
    "foundation": "#9b59b6",
    "plan2_btn": "#00bfff",
    "plan3_btn": "#e67e22",
}

# ===== معرفات عناصر الواجهة (IDs) =====
IDS = {
    "search_query": "search_query",
    "selected_trigger": "selected_model_trigger",
    "close_drawer_trigger": "btn_close_drawer_trigger",
    "btn_settings": "btn_settings",
    "p2_search": "p2_search",
    "p3_search": "p3_search",
    "merge_p2": "btn_learn_and_merge",
    "merge_p3": "btn_learn_and_merge_p3",
    "foundation": "btn_foundation",
    "trigger_p2": "trigger_plan_2",
    "trigger_p3": "trigger_plan_3",
    "execute_plan2_search": "execute_plan2_search",
    "confirm_merge_to_group": "confirm_merge_to_group",
    "open_plan3_emergency": "open_plan3_emergency",
    "show_add_panel": "show_add_panel",
    "show_add_sensor": "show_add_sensor",
}
