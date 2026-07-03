# server.py (الجزء الأول من قطعتين - الإعدادات مدمجة محلياً لمنع الأخطاء)

import json
import time
from shiny import ui, render, reactive

# استدعاء الخدمات الموحدة والثوابت المستقرة
import services as svs
from core.logger import get_logger
from silent_monitor import get_database, refresh, get_status, get_statistics
from logic_engine import run_system_workflows
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_neon_section

log = get_logger("server")

# دمج إعدادات وثوابت زجاج الحماية محلياً لضمان الإقلاع الفوري ومنع كسر الكود
DEFAULT_SCREEN_SIZE = "6.5"
DEFAULT_PANEL_NAME = "Notch"
DEFAULT_SENSOR_NAME = "Virtual"
STATS_REFRESH_TTL = 3
REFRESH_INTERVAL_SEC = 5
STATUS_INTERVAL_SEC = 10
MAX_SUGGESTIONS = 10


def server(input, output, session):
    # ===== State Management =====
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

    # ===== Data Layer =====
    @reactive.calc
    def database_data():
        db_trigger()
        try:
            db = get_database()
            if isinstance(db, dict):
                return db
            return svs.convert_database_from_raw(db) if isinstance(db, list) else {}
        except (TypeError, ValueError, KeyError, AttributeError, IndexError) as error:
            log.error(f"Database Mapping Exception Caught: {error}")
            return {}

    @reactive.calc
    def fast_index_calc():
        return svs.build_fast_index(database_data())

    @reactive.calc
    def get_cached_stats_data():
        now = time.time()
        if now - _stats_time() < STATS_REFRESH_TTL and _cached_stats() is not None:
            return _cached_stats()
        try:
            statistics = get_statistics()
            _cached_stats.set(statistics)
            _stats_time.set(now)
            return statistics
        except (RuntimeError, KeyError, AttributeError, IndexError):
            return {}

    @reactive.calc
    def get_cached_status_data():
        now = time.time()
        if now - _status_time() < STATS_REFRESH_TTL and _cached_status() is not None:
            return _cached_status()
        try:
            status = get_status()
            _cached_status.set(status)
            _status_time.set(now)
            return status
        except (RuntimeError, KeyError, AttributeError, IndexError):
            return {}

    # ===== Watchers =====
    @reactive.effect
    def watcher_refresh():
        reactive.invalidate_later(REFRESH_INTERVAL_SEC)  # استدعاء محلي نقي وآمن
        db_trigger()
        svs.execute_refresh_logic(
            get_cached_stats_data, database_data, autocomplete_index, models_index,
            custom_panels, custom_sensors, _last_db_size, show_curtain, current_phone, suggestions_list, refresh, invalidate_workflow
        )

    @reactive.effect
    def watcher_status():
        reactive.invalidate_later(STATUS_INTERVAL_SEC)   # استدعاء محلي نقي وآمن
        svs.execute_status_logic(get_cached_status_data, _last_monitor_status)

    # ===== Search & Autocomplete =====
    @reactive.effect
    @reactive.event(input.search_query)
    def handle_search():
        svs.process_search_query(
            input.search_query(), current_phone, suggestions_list, show_curtain, autocomplete_index
        )

    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list():
            return None
        return ui.div(
            *[ui.div(
                row, class_="suggestion-row",
                onclick=f"Shiny.setInputValue('search_query', {json.dumps(row)}, {{priority:'event'}}); Shiny.setInputValue('selected_model_trigger', Math.random(), {{priority:'event'}});"
            ) for row in suggestions_list()[:MAX_SUGGESTIONS]],  # تحديد الاقتراحات محلياً
            class_="suggestions-curtain"
        )

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def confirm_selection():
        show_curtain.set(False)
        current_phone.set(input.search_query().strip())
        invalidate_workflow()
    # ===== Unified Plan Logic =====
    def run_plan(screen_size, panel_name, sensor_name, plan_type):
        try:
            db = database_data()
            idx = fast_index_calc()
            
            output_data = svs.process_plan(screen_size, panel_name, sensor_name, db, idx, plan_type)
            
            for key, val in zip(["size", "panel", "sensor"], [screen_size, panel_name, sensor_name]):
                plan_inputs[key].set(str(val).strip())
            current_plan_type.set(plan_type)
            
            if isinstance(output_data, dict):
                plan_results.set(output_data.get("results"))
            else:
                plan_results.set(None)
        except (ValueError, TypeError, KeyError, AttributeError, IndexError) as error:
            log.error(f"Unified run_plan Execution Exception: {error}")
            plan_results.set(None)

    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def open_plan_2():
        active_modal.set("plan_2")
        current_plan_type.set("plan_2")
        plan_results.set(None)

    @reactive.effect
    @reactive.event(input.trigger_plan_3)
    def open_plan_3():
        active_modal.set("plan_3")
        current_plan_type.set("plan_3")
        plan_results.set(None)
        
        # الاعتماد على معايير زجاج الحماية المعرفة محلياً في الجزء الأول بدقة كاملة
        if not plan_inputs["size"]():
            plan_inputs["size"].set(DEFAULT_SCREEN_SIZE)
        if not plan_inputs["panel"]():
            plan_inputs["panel"].set(custom_panels() if custom_panels() else DEFAULT_PANEL_NAME)
        if not plan_inputs["sensor"]():
            plan_inputs["sensor"].set(custom_sensors() if custom_sensors() else DEFAULT_SENSOR_NAME)

    @reactive.effect
    @reactive.event(input.p2_search)
    def trigger_run_plan_2():
        screen_size, panel_name, sensor_name = input.p2_size(), input.p2_panel(), input.p2_sensor()
        if screen_size is not None and panel_name not in (None, "", "__empty__") and sensor_name not in (None, "", "__empty__"):
            active_modal.set(None)
            run_plan(screen_size, panel_name, sensor_name, "plan_2")

    @reactive.effect
    @reactive.event(input.p3_search)
    def trigger_run_plan_3():
        screen_size, panel_name, sensor_name = input.p3_size(), input.p3_panel(), input.p3_sensor()
        if screen_size is not None and panel_name not in (None, "", "__empty__") and sensor_name not in (None, "", "__empty__"):
            active_modal.set(None)
            run_plan(screen_size, panel_name, sensor_name, "plan_3")

    # ===== Save & Reset Pipeline =====
    def trigger_reset_ui():
        svs.reset_ui(
            session, current_phone, show_curtain, suggestions_list,
            plan_results, current_plan_type, active_modal, plan_inputs, invalidate_workflow
        )

    def trigger_save_model(action_name):
        success = svs.perform_save(
            current_phone(), plan_inputs["size"](), plan_inputs["panel"](), plan_inputs["sensor"](), action_name
        )
        if success:
            invalidate_stats()
            db_trigger.set(db_trigger() + 1)
            trigger_reset_ui()

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge)
    def learn_p2():
        trigger_save_model("Merge P2")

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge_p3)
    def learn_p3():
        trigger_save_model("Merge P3")

    @reactive.effect
    @reactive.event(input.btn_foundation)
    def foundation():
        trigger_save_model("Foundation")

    # ===== Modals UI Triggers & Handlers =====
    @reactive.effect
    @reactive.event(input.show_add_panel)
    def handle_show_add_panel_event():
        svs.handle_show_add_panel(show_curtain, suggestions_list)

    @reactive.effect
    @reactive.event(input.show_add_sensor)
    def handle_show_add_sensor_event():
        svs.handle_show_add_sensor(show_curtain, suggestions_list)

    @reactive.effect
    @reactive.event(input.btn_confirm_add_panel)
    def confirm_add_panel_event():
        svs.confirm_add_panel(input, custom_panels, invalidate_workflow)

    @reactive.effect
    @reactive.event(input.btn_confirm_add_sensor)
    def confirm_add_sensor_event():
        svs.confirm_add_sensor(input, custom_sensors, invalidate_workflow)

    @reactive.effect
    @reactive.event(input.btn_cancel_add)
    def cancel_add_event():
        svs.cancel_add()

    # ===== Render Output View Components =====
    @render.ui
    def dynamic_modal_container():
        mode = active_modal()
        if mode == "plan_2":
            return draw_plan_2_modal(current_phone(), custom_panels(), custom_sensors())
        if mode == "plan_3":
            return draw_plan_3_modal(current_phone(), custom_panels(), custom_sensors())
        return None

    @render.ui
    def results_workflow_view():
        phone_name = current_phone().strip()
        if not phone_name or show_curtain():
            return None
        
        results_cache = plan_results()
        if results_cache is not None:
            plan_type = current_plan_type()
            return ui.div(
                svs.build_plan_results_header(plan_type),
                draw_neon_section("تطابق تام ومباشر", results_cache.get("exact", []), "#2ecc71", "🟢", "exact"),
                draw_neon_section("أكبر بقليل ضمن التفاوت", results_cache.get("plus", []), "#3498db", "🔵", "plus"),
                draw_neon_section("أصغر قليلاً ضمن التفاوت", results_cache.get("minus", []), "#e67e22", "🟠", "minus")
            )
            
        database = database_data()
        return ui.HTML(run_system_workflows(phone_name, database))
