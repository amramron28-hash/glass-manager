import json
import time
from shiny import ui, render, reactive

# الاستيرادات من مشروعك الأصلي (تأكد أن المسارات مطابقة لمجلداتك)
from services.search_service import build_autocomplete_index
from services.plan_engine import compute_plan_matches
from services.index_service import extract_panels_sensors
from services.cache_service import workflow_cache
from core.logger import get_logger

from database import add_model
from silent_monitor import get_database, refresh, get_status, get_cached_status
from logic_engine import run_system_workflows
# استيراد الدوال كما هي موجودة في ملف ui_components.py الخاص بك
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, draw_warning_card,
    draw_technical_coords, draw_neon_section, draw_database_status,
    draw_monitor_component, draw_notifications
)

log = get_logger("server")

def server(input, output, session):
    # 1. تعريف الحالة (State Management)
    current_phone = reactive.Value("")
    active_modal = reactive.Value(None)
    suggestions_list = reactive.Value([])
    show_curtain = reactive.Value(False)
    
    # تحميل الفهرس (مطابق للمرجع)
    def load_index():
        try:
            with open("models_index.txt", "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except: return []

    autocomplete_index = reactive.Value(build_autocomplete_index(load_index()))

    # 2. البحث (Search & Autocomplete)
    @reactive.effect
    @reactive.event(input.search_query)
    def handle_search():
        q = input.search_query().strip()
        current_phone.set(q)
        if not q:
            suggestions_list.set([])
            show_curtain.set(False)
            return
        t = autocomplete_index()
        if t:
            m = t.search_prefix(q, 10)
            suggestions_list.set(m)
            show_curtain.set(len(m) > 0)

    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list(): return None
        return ui.div(*[ui.div(
            i, class_="suggestion-row",
            onclick=f"Shiny.setInputValue('search_query', {json.dumps(i)}, {{priority:'event'}});"
        ) for i in suggestions_list()], class_="suggestions-curtain")

    # 3. النافذة المنبثقة والخطط (Modals & Plans)
    @render.ui
    def modal_layer():
        m = active_modal()
        if not m: return None
        db = get_database()
        panels, sensors = extract_panels_sensors(db)
        if m == "plan_2": return draw_plan_2_modal(current_phone(), panels, sensors)
        if m == "plan_3": return draw_plan_3_modal(current_phone(), panels, sensors)
        return None

    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def _(): active_modal.set("plan_2")

    @reactive.effect
    @reactive.event(input.trigger_plan_3)
    def _(): active_modal.set("plan_3")

    # 4. النتائج والواجهة (UI Rendering)
    @render.ui
    def results_area():
        # هنا يتم ربط المنطق الفعلي الذي يظهر البطاقات
        return ui.HTML(run_system_workflows(current_phone(), get_database()))

    @render.ui
    def database_status_area():
        db = get_database()
        total = sum(len(d.get("models", [])) for p in db.values() for s in p.values() for d in s.values() if isinstance(d, dict))
        return draw_database_status(total)

    @render.ui
    def monitor_area():
        return draw_monitor_component(get_cached_status())

    @render.ui
    def notifications_area():
        return draw_notifications(get_cached_status())

    # 5. الإعدادات والدرج (Drawer)
    @reactive.effect
    @reactive.event(input.btn_settings)
    async def _(): await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def _(): await session.send_custom_message("toggle_drawer", "close")
