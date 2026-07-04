from shiny import render, reactive, ui
import json
import time
import logging

import services as svs
from logic_engine import run_system_workflows, STATUS_PLAN_2, STATUS_PLAN_3
from silent_monitor import get_database, refresh
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_settings_modal

# -----------------------
# LOGGER
# -----------------------
logger = logging.getLogger("ui_debug")
workflow_logger = logging.getLogger("WorkflowEngine")


def server(input, output, session):

    ui_state = {
        "modal": reactive.Value(None),
        "suggestions": reactive.Value(False),
    }

    workflow_state = reactive.Value(None)
    last_query = reactive.Value("")
    last_run_time = reactive.Value(0.0)

    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})
    initialized = reactive.Value(False)

    autocomplete_index = {"index": None}

    # -----------------------
    # INIT
    # -----------------------
    @reactive.effect
    def _():
        if initialized():
            return

        try:
            refresh()
            db = get_database()

            if isinstance(db, dict):
                panels, sensors = svs.extract_panels_sensors(db)

                panels_cache.set(panels)
                sensors_cache.set(sensors)

                autocomplete_index["index"] = svs.build_autocomplete_index(
                    svs.load_models_index()
                )

            initialized.set(True)
            workflow_logger.info("System READY")

        except Exception as e:
            workflow_logger.error(f"INIT ERROR: {e}")
            reactive.invalidate_later(5)

    # -----------------------
    # SEARCH ENGINE + LOGGER ADDED
    # -----------------------
    @reactive.effect
    def _():

        q = input.search_query()

        # ✅ DEBUG LOG (مضاف كما طلبت)
        if q != last_query():
            logger.info(f"SEARCH INPUT: {q}")

        ui_state["suggestions"].set(bool(q and len(q) >= 2))

        if not q or len(q) < 2:
            return

        if q == last_query():
            return

        now = time.time()
        if now - last_run_time() < 0.35:
            return

        last_run_time.set(now)
        last_query.set(q)

        try:
            db = get_database()
            res = run_system_workflows(q, db)

            workflow_state.set(res)

            status = res.get("status") if isinstance(res, dict) else None

            if status in [STATUS_PLAN_2, STATUS_PLAN_3]:
                ui_state["modal"].set(status)
            else:
                ui_state["modal"].set(None)

        except Exception as e:
            workflow_logger.error(f"SEARCH ERROR: {e}")

    # -----------------------
    # SETTINGS
    # -----------------------
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _():
        ui_state["modal"].set("settings")

    # -----------------------
    # CLOSE MODAL
    # -----------------------
    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _():
        ui_state["modal"].set(None)

    # -----------------------
    # AUTOCOMPLETE
    # -----------------------
    @render.ui
    def suggestions_curtain():
        if not ui_state["suggestions"]():
            return None

        q = input.search_query()
        idx = autocomplete_index["index"]

        if not q or not idx:
            return None

        results = idx.search_prefix(q, 5)

        if not results:
            return None

        return ui.div(
            *[
                ui.div(
                    r,
                    class_="suggestion-row",
                    onclick=f"""
                        Shiny.setInputValue('search_query', {json.dumps(r)});
                        Shiny.setInputValue('hide_suggestions', true);
                    """
                )
                for r in results
            ],
            class_="suggestions-curtain",
        )

    # -----------------------
    # MODAL
    # -----------------------
    @render.ui
    def dynamic_modal_container():

        m = ui_state["modal"]()
        res = workflow_state()

        if not m:
            return None

        if m == "settings":
            return draw_settings_modal()

        if not isinstance(res, dict):
            return None

        phone = res.get("input_data", {}).get("phone")
        if not phone:
            return None

        if m == STATUS_PLAN_2:
            return draw_plan_2_modal(phone, panels_cache(), sensors_cache())

        if m == STATUS_PLAN_3:
            return draw_plan_3_modal(phone, res)

        return None

    # -----------------------
    # CLOSE SUGGESTIONS
    # -----------------------
    @reactive.effect
    @reactive.event(input.hide_suggestions)
    def _():
        ui_state["suggestions"].set(False)
