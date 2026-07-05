from shiny import reactive, render, ui
import logging
import json

import services as svs
from logic_engine import run_system_workflows, STATUS_PLAN_2, STATUS_PLAN_3
from silent_monitor import get_database, refresh
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_settings_modal

logger = logging.getLogger("ui_debug")

# =========================
# STATE MACHINE CORE
# =========================

STATE_IDLE = "idle"
STATE_SEARCHING = "searching"
STATE_RESULT = "result"
STATE_SETTINGS = "settings"
STATE_PLAN2 = "plan2"
STATE_PLAN3 = "plan3"


def server(input, output, session):

    # =========================
    # GLOBAL STATE
    # =========================
    state = reactive.Value(STATE_IDLE)
    workflow = reactive.Value({})
    last_query = reactive.Value("")
    initialized = reactive.Value(False)

    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})
    autocomplete_index = {"index": None}

    # =========================
    # INIT
    # =========================
    @reactive.effect
    def init():
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
    # SEARCH STATE MACHINE
    # =========================
    @reactive.effect
    def search_engine():

        q = input.search_query()

        if not q or len(q) < 2:
            return

        if q == last_query():
            return

        state.set(STATE_SEARCHING)

        try:
            db = get_database()
            res = run_system_workflows(q, db) or {}

            workflow.set(res)
            last_query.set(q)

            status = res.get("status")

            # STATE ROUTING
            if status == STATUS_PLAN_2:
                state.set(STATE_PLAN2)

            elif status == STATUS_PLAN_3:
                state.set(STATE_PLAN3)

            else:
                state.set(STATE_RESULT)

            logger.info(f"STATUS => {status}")

        except Exception as e:
            logger.error(f"SEARCH ERROR: {e}")
            state.set(STATE_IDLE)

    # =========================
    # SETTINGS BUTTON
    # =========================
    @reactive.effect
    @reactive.event(input.btn_settings)
    def open_settings():
        state.set(STATE_SETTINGS)

    # =========================
    # CLOSE MODAL (GLOBAL)
    # =========================
    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def close_modal():
        state.set(STATE_IDLE)

    # =========================
    # MODAL ENGINE (PURE STATE ROUTER)
    # =========================
    @render.ui
    def dynamic_modal_container():

        s = state()
        res = workflow() or {}

        if s == STATE_SETTINGS:
            return draw_settings_modal()

        phone = (res.get("input_data") or {}).get("phone", "غير محدد")

        if s == STATE_PLAN2:
            return draw_plan_2_modal(phone, panels_cache(), sensors_cache())

        if s == STATE_PLAN3:
            return draw_plan_3_modal(phone, res)

        return None

    # =========================
    # SEARCH RESULTS UI
    # =========================
    @render.ui
    def results_workflow_view():

        res = workflow() or {}

        if not res:
            return ui.div("لا توجد نتائج", class_="empty-state")

        status = res.get("status", "UNKNOWN")

        return ui.div(
            ui.div(f"📌 الحالة: {status}", class_="result-card"),
            class_="results-container"
        )

    # =========================
    # AUTOCOMPLETE (OPTIONAL SAFE)
    # =========================
    @render.ui
    def suggestions_curtain():

        q = input.search_query()
        idx = autocomplete_index["index"]

        if not q or not idx:
            return None

        results = idx.search_prefix(q, 5) or []

        return ui.div(
            *[
                ui.div(
                    r,
                    class_="suggestion-row",
                    onclick=f"Shiny.setInputValue('search_query', {json.dumps(r)});"
                )
                for r in results
            ],
            class_="suggestions-curtain"
        )
