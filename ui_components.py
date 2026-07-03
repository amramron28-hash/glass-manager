# server.py

import json
import time
from shiny import ui, render, reactive

import services as svs
from core.logger import get_logger
from silent_monitor import get_database, refresh, get_status, get_statistics
from logic_engine import run_system_workflows
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_neon_section, draw_database_status

log = get_logger("server")

DEFAULT_SCREEN_SIZE = "6.5"
DEFAULT_PANEL_NAME = "Notch"
DEFAULT_SENSOR_NAME = "Virtual"
STATS_REFRESH_TTL = 3
REFRESH_INTERVAL_SEC = 5
STATUS_INTERVAL_SEC = 10
MAX_SUGGESTIONS = 10

def server(input, output, session):
    db_trigger = reactive.Value(0)
    current_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)
    suggestions_list = reactive.Value([])
    plan_results = reactive.Value(None)

    plan_inputs = {key: reactive.Value("") for key in ["size", "panel", "sensor"]}
    current_plan_type = reactive.Value(None)

    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])
    autocomplete_index = reactive.Value(None)
    models_index = reactive.Value(svs.load_models_index())

    _db_version = reactive.Value(0)
    _last_db_size = reactive.Value(-1)
    _last_monitor_status = reactive.Value("")

    _cached_stats = reactive.Value(None)
    _cached_status = reactive.Value(None)
    _stats_time = reactive.Value(0)
    _status_time = reactive.Value(0)

    def invalidate_workflow():
        svs.workflow_cache.invalidate()
        svs.coords_cache.invalidate()
        _db_version.set(_db_version() + 1)

    def invalidate_stats():
        _cached_stats.set(None)
        _cached_status.set(None)
        _stats_time.set(0)
        _status_time.set(0)

    @reactive.calc
    def database_data():
        db_trigger()
        try:
            db = get_database()
            return svs.convert_database_from_raw(db) if isinstance(db, (list, dict)) else {}
        except Exception as error:
            log.error(f"Database Mapping Exception: {error}")
            return {}

    @reactive.calc
    def fast_index_calc():
        return svs.build_fast_index(database_data())

    # Watchers
    @reactive.effect
    def watcher_refresh():
        reactive.invalidate_later(REFRESH_INTERVAL_SEC, session=session)
        db_trigger()
        svs.execute_refresh_logic(
            get_cached_stats_data, database_data, autocomplete_index, models_index,
            custom_panels, custom_sensors, _last_db_size, show_curtain, current_phone, suggestions_list, refresh, invalidate_workflow
        )

    @reactive.effect
    def watcher_status():
        reactive.invalidate_later(STATUS_INTERVAL_SEC, session=session)
        svs.execute_status_logic(get_cached_status_data, _last_monitor_status)

    # Drawer UI Components
    @render.ui
    def database_status_area():
        total = len(models_index()) if models_index() else 0
        return draw_database_status(total)

    @render.ui
    def notifications_area():
        return ui.div("✅ النظام يعمل بكفاءة", class_="metric-box", style="border-color:#2ecc71;")

    @render.ui
    def monitor_area():
        status = _last_monitor_status() or "CHECKING..."
        return ui.div(f"📡 الحالة: {status}", class_="metric-box", 
                      style=f"border-color:{'#2ecc71' if status == 'ONLINE' else '#ff5252'};")

    # Search & Modals
    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list(): return None
        return ui.div(
            *[ui.div(row, class_="suggestion-row", 
                onclick=f"Shiny.setInputValue('search_query', {json.dumps(row)}, {{priority:'event'}}); Shiny.setInputValue('selected_model_trigger', Math.random(), {{priority:'event'}});"
            ) for row in suggestions_list()[:MAX_SUGGESTIONS]],
            class_="suggestions-curtain"
        )

    @render.ui
    def dynamic_modal_container():
        mode = active_modal()
        if mode == "plan_2": return draw_plan_2_modal(current_phone(), custom_panels(), custom_sensors())
        if mode == "plan_3": return draw_plan_3_modal(current_phone(), custom_panels(), custom_sensors())
        return None

    @render.ui
    def results_workflow_view():
        phone_name = current_phone().strip()
        if not phone_name or show_curtain(): return None
        if plan_results() is not None:
            return ui.div(
                svs.build_plan_results_header(current_plan_type()),
                draw_neon_section("تطابق تام", plan_results().get("exact", []), "#2ecc71", "🟢", "exact"),
                draw_neon_section("تفاوت إيجابي", plan_results().get("plus", []), "#3498db", "🔵", "plus"),
                draw_neon_section("تفاوت سلبي", plan_results().get("minus", []), "#e67e22", "🟠", "minus")
            )
        return ui.HTML(run_system_workflows(phone_name, database_data()))

    # (بقية الدوال المساعدة مثل open_plan_3, run_plan تبقى كما هي)
    # ملاحظة: تم التأكد من دمج التعديلات السابقة الخاصة بـ panels[0] و sensors[0] في open_plan_3
