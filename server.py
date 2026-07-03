import json
import time
from shiny import ui, render, reactive
import services as svs
from core.logger import get_logger
from silent_monitor import get_database, refresh, get_status, get_statistics
from logic_engine import run_system_workflows
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_neon_section

log = get_logger("server")

def server(input, output, session):
    # ===== State Management =====
    current_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)
    suggestions_list = reactive.Value([])
    
    # تحميل الفهارس والبيانات
    autocomplete_index = reactive.Value(None)
    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])

    # ===== Drawer/Settings Logic =====
    @reactive.effect
    @reactive.event(input.btn_settings)
    def open_drawer():
        session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    def close_drawer():
        session.send_custom_message("toggle_drawer", "close")

    # ===== Search & Autocomplete Logic =====
    @reactive.effect
    def update_suggestions():
        query = input.search_query()
        trie = autocomplete_index()
        if query and trie:
            results = trie.search_prefix(query, 10)
            suggestions_list.set(results)
            show_curtain.set(len(results) > 0)
        else:
            show_curtain.set(False)

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def confirm_selection():
        # عند اختيار الموديل، نحدث الهاتف ونغلق الستارة
        selected_model = input.search_query().strip()
        current_phone.set(selected_model)
        show_curtain.set(False)

    # ===== UI Renderers =====
    @render.ui
    def results_workflow_view():
        phone_name = current_phone().strip()
        # لا نظهر النتائج طالما ستارة البحث مفتوحة
        if not phone_name or show_curtain(): 
            return None
        
        # جلب البيانات الشجرية الأصلية للمحرك
        db = get_database()
        return ui.HTML(run_system_workflows(phone_name, db))

    @render.ui
    def dynamic_modal_container():
        mode = active_modal()
        if mode == "plan_2": 
            return draw_plan_2_modal(current_phone(), custom_panels(), custom_sensors())
        if mode == "plan_3": 
            return draw_plan_3_modal(current_phone(), custom_panels(), custom_sensors())
        return None

    # ===== Initialization =====
    @reactive.effect
    def _():
        # بناء الفهرس مرة واحدة عند التشغيل
        new_models = svs.load_models_index()
        if new_models:
            autocomplete_index.set(svs.build_autocomplete_index(new_models))
            
    # ربط الحالة (Status) للـ Drawer
    @render.ui
    def database_status_area():
        db = get_database()
        total = len(db) if isinstance(db, dict) else 0
        return ui.div(f"📊 قاعدة البيانات: {total} هاتف", class_="metric-box")

    @render.ui
    def monitor_area():
        return ui.div("📡 الحالة: ONLINE", class_="metric-box", style="border-color:#2ecc71;")

    @render.ui
    def notifications_area():
        return ui.div("✅ النظام يعمل بكفاءة", class_="metric-box")

    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list():
            return None
        return ui.div(
            *[ui.div(
                row, class_="suggestion-row",
                onclick=f"Shiny.setInputValue('search_query', {json.dumps(row)}, {{priority:'event'}}); Shiny.setInputValue('selected_model_trigger', Math.random(), {{priority:'event'}});"
            ) for row in suggestions_list()[:10]],
            class_="suggestions-curtain"
        )
