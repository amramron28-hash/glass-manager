# server.py

import json
import time
from shiny import ui, render, reactive

# استدعاء موحد ونظيف من البوابة الموحدة لمجلد الخدمات
import services as svs
from core.logger import get_logger
from database import add_model
from silent_monitor import get_database, refresh, get_status, get_statistics
from logic_engine import run_system_workflows
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, draw_warning_card,
    draw_technical_coords, draw_neon_section
)

log = get_logger("server")
STATS_TTL = 3


def server(input, output, session):
    # ===== State Management =====
    db_trigger = reactive.Value(0)
    current_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)
    suggestions_list = reactive.Value([])
    plan_results = reactive.Value(None)

    plan_inputs = {k: reactive.Value("") for k in ["size", "panel", "sensor"]}
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
        except Exception as e:
            log.error(f"DB Error: {e}")
            return {}

    @reactive.calc
    def fast_index_calc():
        return svs.build_fast_index(database_data())

    @reactive.calc
    def get_cached_stats_data():
        now = time.time()
        if now - _stats_time() < STATS_TTL and _cached_stats() is not None:
            return _cached_stats()
        try:
            s = get_statistics()
            _cached_stats.set(s)
            _stats_time.set(now)
            return s
        except Exception:
            return {}

    @reactive.calc
    def get_cached_status_data():
        now = time.time()
        if now - _status_time() < STATS_TTL and _cached_status() is not None:
            return _cached_status()
        try:
            s = get_status()
            _cached_status.set(s)
            _status_time.set(now)
            return s
        except Exception:
            return {}

    # ===== Watchers =====
    @reactive.effect
    def watcher_refresh():
        reactive.invalidate_later(5)
        db_trigger()
        try:
            stats = get_cached_stats_data()
            size = stats.get("phones", 0) if isinstance(stats, dict) else 0
            if size == 0:
                autocomplete_index.set(None)
                models_index.set([])
                custom_panels.set([])
                custom_sensors.set([])
                _last_db_size.set(0)
                return
            if _last_db_size() == size and autocomplete_index() is not None:
                if show_curtain():
                    q = current_phone()
                    t = autocomplete_index()
                    if q and t:
                        suggestions_list.set(t.search_prefix(q, 10))
                return
            _last_db_size.set(size)
            refresh()
            new_idx = svs.load_models_index()
            if autocomplete_index() is None or new_idx != models_index():
                models_index.set(new_idx)
                autocomplete_index.set(svs.build_autocomplete_index(new_idx))
                invalidate_workflow()
                p, s_list = svs.extract_panels_sensors(database_data())
                custom_panels.set(p)
                custom_sensors.set(s_list)
            if show_curtain():
                q = current_phone()
                t = autocomplete_index()
                if q and t:
                    suggestions_list.set(t.search_prefix(q, 10))
        except Exception as e:
            log.error(f"Refresh Err: {e}")

    @reactive.effect
    def watcher_status():
        reactive.invalidate_later(10)
        try:
            st = get_cached_status_data()
            cur = st.get("status", "UNKNOWN") if isinstance(st, dict) else "UNKNOWN"
            if cur != _last_monitor_status():
                _last_monitor_status.set(cur)
                log.warning(f"Monitor: {cur}") if cur != "ONLINE" else log.info("Monitor: ONLINE")
        except Exception as e:
            log.error(f"Status Err: {e}")

    # ===== Search & Autocomplete =====
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
        if not t:
            return
        m = t.search_prefix(q, 10)
        ex = t.contains_exact(q)
        if m and not ex:
            suggestions_list.set(m)
            show_curtain.set(True)
        else:
            suggestions_list.set([])
            show_curtain.set(False)

    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list():
            return None
        return ui.div(
            *[ui.div(
                i, class_="suggestion-row",
                onclick=f"Shiny.setInputValue('search_query', {json.dumps(i)}, {{priority:'event'}}); Shiny.setInputValue('selected_model_trigger', Math.random(), {{priority:'event'}});"
            ) for i in suggestions_list()],
            class_="suggestions-curtain"
        )

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def confirm_selection():
        show_curtain.set(False)
        current_phone.set(input.search_query().strip())
        invalidate_workflow()

    # ===== Plan Execution Layer =====
    def execute_mapped_plan(sz, pn, sn, pt):
        try:
            db = database_data()
            idx = fast_index_calc()
            
            output_data = svs.process_plan(sz, pn, sn, db, idx)
            
            for k, v in zip(["size", "panel", "sensor"], [sz, pn, sn]):
                plan_inputs[k].set(str(v).strip())
            current_plan_type.set(pt)
            
            if output_data:
                plan_results.set(output_data["results"])
            else:
                plan_results.set(None)
        except Exception as e:
            log.error(f"Execution plan error: {e}", exc_info=True)
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
        if not plan_inputs["size"]():
            plan_inputs["size"].set("6.5")
        if not plan_inputs["panel"]():
            plan_inputs["panel"].set(custom_panels()[0] if custom_panels() else "OLED")
        if not plan_inputs["sensor"]():
            plan_inputs["sensor"].set(custom_sensors()[0] if custom_sensors() else "Virtual")

    @reactive.effect
    @reactive.event(input.p2_search)
    def run_plan_2():
        sz, pn, sn = input.p2_size(), input.p2_panel(), input.p2_sensor()
        if sz is not None and pn not in (None, "", "__empty__") and sn not in (None, "", "__empty__"):
            active_modal.set(None)
            execute_mapped_plan(sz, pn, sn, "plan_2")

    @reactive.effect
    @reactive.event(input.p3_search)
    def run_plan_3():
        sz, pn, sn = input.p3_size(), input.p3_panel(), input.p3_sensor()
        if sz is not None and pn not in (None, "", "__empty__") and sn not in (None, "", "__empty__"):
            active_modal.set(None)
            execute_mapped_plan(sz, pn, sn, "plan_3")

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

    # ===== Modals UI Triggers & Handlers (إصلاح وإكمال الجزء المقطوع) =====
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
