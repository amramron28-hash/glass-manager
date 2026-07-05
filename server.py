from shiny import reactive, render, ui
import logging
import json

import services as svs
from logic_engine import run_system_workflows
from silent_monitor import get_database, refresh
from ui_components import (
    draw_plan_2_modal,
    draw_plan_3_modal,
    draw_settings_modal
)

logger = logging.getLogger("ui_debug")


def server(input, output, session):

    # =========================
    # STATE MACHINE (FIXED)
    # =========================
    modal_state = reactive.Value(None)
    suggestions_state = reactive.Value(False)
    workflow_state = reactive.Value({})
    last_query = reactive.Value("")
    lock = reactive.Value(False)

    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})

    autocomplete_index = {"index": None}
    initialized = reactive.Value(False)

    # =========================
    # INIT
    # =========================
    @reactive.effect
    def _init():

        if initialized():
            return

        try:
            refresh()
            db = get_database()

            if isinstance(db, dict):
                p, s = svs.extract_panels_sensors(db)
                panels_cache.set(p or {})
                sensors_cache.set(s or {})

                autocomplete_index["index"] = svs.build_autocomplete_index(
                    svs.load_models_index()
                )

            initialized.set(True)
            logger.info("SYSTEM READY")

        except Exception as e:
            logger.error(f"INIT ERROR: {e}")

    # =========================
    # SEARCH ENGINE (STATE MACHINE CORE FIX)
    # =========================
    @reactive.effect
    def search_engine():

        q = input.search_query()

        if not q:
            suggestions_state.set(False)
            modal_state.set(None)
            return

        if len(q) < 2:
            suggestions_state.set(False)
            return

        suggestions_state.set(True)

        if lock():
            return

        if q == last_query():
            return

        lock.set(True)

        try:
            db = get_database()
            res = run_system_workflows(q, db) or {}

            workflow_state.set(res)
            last_query.set(q)

            status = res.get("status")

            # =========================
            # MODAL ROUTING FIX
            # =========================
            if status == "plan_2":
                modal_state.set("plan2")

            elif status == "plan_3":
                modal_state.set("plan3")

            else:
                modal_state.set(None)

            logger.info(f"STATUS: {status}")

        except Exception as e:
            logger.error(f"SEARCH ERROR: {e}")

        finally:
            lock.set(False)

    # =========================
    # SETTINGS BUTTON
    # =========================
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _():
        modal_state.set("settings")

    # =========================
    # CLOSE MODAL
    # =========================
    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _():
        modal_state.set(None)

    # =========================
    # UI PULSE (FORCE REACTIVE UPDATE)
    # =========================
    @reactive.effect
    def _pulse():
        _ = modal_state()
        _ = suggestions_state()
        _ = workflow_state()

    # =========================
    # MODAL RENDER
    # =========================
    @render.ui
    def dynamic_modal_container():

        m = modal_state()
        res = workflow_state() or {}

        if not m:
            return None

        phone = (res.get("input_data") or {}).get("phone", "")

        if m == "plan2":
            return draw_plan_2_modal(phone, panels_cache(), sensors_cache())

        if m == "plan3":
            return draw_plan_3_modal(phone, res)

        if m == "settings":
            return draw_settings_modal()

        return None

    # =========================
    # RESULTS VIEW (FIXED)
    # =========================
    @render.ui
    def results_workflow_view():

        res = workflow_state() or {}

        if not res:
            return ui.div("لا توجد نتائج", class_="empty-state")

        status = res.get("status", "UNKNOWN")
        phone = (res.get("input_data") or {}).get("phone", "")

        return ui.div(
            ui.div(f"📱 الهاتف: {phone}", class_="result-card"),
            ui.div(f"📌 الحالة: {status}", class_="result-card"),
            class_="results-container"
        )

    # =========================
    # AUTOCOMPLETE (FIXED)
    # =========================
    @render.ui
    def suggestions_curtain():

        if not suggestions_state():
            return None

        q = input.search_query()
        idx = autocomplete_index.get("index")

        if not q or not idx:
            return None

        try:
            results = idx.search_prefix(q, 5)
        except:
            results = []

        if not results:
            return None

        return ui.div(
            *[
                ui.div(
                    r,
                    class_="suggestion-row",
                    onclick=f"Shiny.setInputValue('search_query', {json.dumps(r)})"
                )
                for r in results
            ],
            class_="suggestions-curtain"
        )

    # =========================
    # SAFETY RESET (optional but important)
    # =========================
    @reactive.effect
    @reactive.event(input.search_query)
    def _():
        # reset modal if user clears search
        if not input.search_query():
            modal_state.set(None)
            suggestions_state.set(False)
