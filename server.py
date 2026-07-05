from shiny import reactive, render, ui
import logging
import json

import services as svs
from logic_engine import run_system_workflows, STATUS_PLAN_2, STATUS_PLAN_3
from silent_monitor import get_database, refresh
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_settings_modal

logger = logging.getLogger("ui_debug")


def server(input, output, session):

    # ================= STATE MACHINE =================
    class UIStateMachine:
        IDLE = None
        SETTINGS = "settings"
        PLAN2 = "plan2"
        PLAN3 = "plan3"

    ui_state = {
        "modal": reactive.Value(UIStateMachine.IDLE),
        "suggestions": reactive.Value(False)
    }

    app_state = {
        "workflow": reactive.Value({}),
        "lock": reactive.Value(False),
        "last_q": reactive.Value("")
    }

    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})

    autocomplete_index = {"index": None}
    initialized = reactive.Value(False)

    # ================= INIT =================
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
            reactive.invalidate_later(5)

    # ================= SEARCH ENGINE =================
    @reactive.effect
    def _search():

        q = input.search_query()
        logger.info(f"SEARCH INPUT: {q}")

        if not q or len(q) < 2:
            ui_state["suggestions"].set(False)
            ui_state["modal"].set(UIStateMachine.IDLE)
            return

        ui_state["suggestions"].set(True)

        if app_state["lock"]():
            return

        if q == app_state["last_q"]():
            return

        app_state["lock"].set(True)

        try:
            db = get_database()
            res = run_system_workflows(q, db) or {}

            app_state["workflow"].set(res)
            app_state["last_q"].set(q)

            status = res.get("status")

            # ================= STATE MACHINE ROUTING =================
            if status == STATUS_PLAN_2:
                ui_state["modal"].set(UIStateMachine.PLAN2)

            elif status == STATUS_PLAN_3:
                ui_state["modal"].set(UIStateMachine.PLAN3)

            else:
                ui_state["modal"].set(UIStateMachine.IDLE)

            logger.info(f"STATUS: {status}")

        except Exception as e:
            logger.error(f"SEARCH ERROR: {e}")
            ui_state["modal"].set(UIStateMachine.IDLE)

        finally:
            app_state["lock"].set(False)

    # ================= SETTINGS =================
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _():
        ui_state["modal"].set(UIStateMachine.SETTINGS)

    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _():
        ui_state["modal"].set(UIStateMachine.IDLE)

    # ================= MODAL ENGINE =================
    @render.ui
    def dynamic_modal_container():

        state = ui_state["modal"]()
        res = app_state["workflow"]() or {}

        if state == UIStateMachine.IDLE:
            return None

        if state == UIStateMachine.SETTINGS:
            return draw_settings_modal()

        phone = (res.get("input_data") or {}).get("phone", "")

        if state == UIStateMachine.PLAN2:
            return draw_plan_2_modal(phone, panels_cache(), sensors_cache())

        if state == UIStateMachine.PLAN3:
            return draw_plan_3_modal(phone, res)

        return None

    # ================= RESULTS =================
    @render.ui
    def results_workflow_view():

        res = app_state["workflow"]() or {}

        if not res:
            return ui.div("لا توجد نتائج", class_="empty-state")

        phone = (res.get("input_data") or {}).get("phone", "")
        status = res.get("status", "UNKNOWN")

        return ui.div(
            ui.div(f"📱 الهاتف: {phone}", class_="result-card"),
            ui.div(f"📌 الحالة: {status}", class_="result-card"),
            class_="results-container"
        )

    # ================= AUTOCOMPLETE =================
    @render.ui
    def suggestions_curtain():

        if not ui_state["suggestions"]():
            return None

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

    # ================= CLOSE SUGGESTIONS =================
    @reactive.effect
    @reactive.event(input.hide_suggestions)
    def _():
        ui_state["suggestions"].set(False)
