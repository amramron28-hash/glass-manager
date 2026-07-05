from shiny import reactive, render, ui
import logging
import time
import json

import services as svs
from logic_engine import run_system_workflows, STATUS_PLAN_2, STATUS_PLAN_3
from silent_monitor import get_database, refresh
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_settings_modal

logger = logging.getLogger("ui_debug")


def server(input, output, session):

    # ---------------- STATE ----------------
    ui_state = {
        "modal": reactive.Value(None),
        "suggestions": reactive.Value(False)
    }

    app_state = {
        "workflow": reactive.Value(None),
        "lock": reactive.Value(False),
        "last_query": reactive.Value("")
    }

    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})
    initialized = reactive.Value(False)

    autocomplete_index = {"index": None}

    # ---------------- INIT ----------------
    @reactive.effect
    def _init():
        if initialized():
            return

        try:
            refresh()
            db = get_database()

            if isinstance(db, dict):
                p, s = svs.extract_panels_sensors(db)
                panels_cache.set(p)
                sensors_cache.set(s)

                autocomplete_index["index"] = svs.build_autocomplete_index(
                    svs.load_models_index()
                )

            initialized.set(True)
            logger.info("SYSTEM INITIALIZED")

        except Exception as e:
            logger.error(f"INIT ERROR: {e}")
            reactive.invalidate_later(5)

    # ---------------- SEARCH ENGINE ----------------
    @reactive.effect
    def _search():
        q = input.search_query()

        # 🔥 LOGGING الذي طلبته
        logger.info(f"SEARCH INPUT: {q}")

        if not q or len(q) < 2:
            ui_state["suggestions"].set(False)
            return

        ui_state["suggestions"].set(True)

        if app_state["lock"]():
            return

        app_state["lock"].set(True)

        try:
            db = get_database()
            res = run_system_workflows(q, db)

            app_state["workflow"].set(res)
            app_state["last_query"].set(q)

            status = res.get("status")

            if status in [STATUS_PLAN_2, STATUS_PLAN_3]:
                ui_state["modal"].set(status)
            else:
                ui_state["modal"].set(None)

            logger.info(f"SEARCH RESULT STATUS: {status}")

        except Exception as e:
            logger.error(f"SEARCH ERROR: {e}")

        finally:
            app_state["lock"].set(False)

    # ---------------- MODAL CONTROL ----------------
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _():
        ui_state["modal"].set("settings")

    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _():
        ui_state["modal"].set(None)

    # ---------------- MODAL RENDER ----------------
    @render.ui
    def dynamic_modal_container():

        m = ui_state["modal"]()
        res = app_state["workflow"]()

        if not m:
            return None

        if m == "settings":
            return draw_settings_modal()

        if not res:
            return None

        phone = (res or {}).get("input_data", {}).get("phone", "غير محدد")

        if m == STATUS_PLAN_2:
            return draw_plan_2_modal(phone, panels_cache(), sensors_cache())

        if m == STATUS_PLAN_3:
            return draw_plan_3_modal(phone, res)

        return None

    # ---------------- RESULTS CARDS (FIX IMPORTANT) ----------------
    @render.ui
    def results_workflow_view():

        res = app_state["workflow"]()
        if not res:
            return ui.div("لا توجد نتائج بعد", class_="empty-state")

        status = res.get("status", "")
        phone = (res.get("input_data", {}) or {}).get("phone", "غير محدد")

        cards = [
            ui.div(
                ui.h4(f"📱 الهاتف: {phone}"),
                ui.p(f"📌 الحالة: {status}"),
                class_="result-card"
            )
        ]

        return ui.div(*cards, class_="results-container")

    # ---------------- AUTOCOMPLETE ----------------
    @render.ui
    def suggestions_curtain():

        if not ui_state["suggestions"]():
            return None

        q = input.search_query()
        idx = autocomplete_index["index"]

        if not q or not idx:
            return None

        results = idx.search_prefix(q, 5)

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

    # ---------------- CLOSE SUGGESTIONS ----------------
    @reactive.effect
    @reactive.event(input.hide_suggestions)
    def _():
        ui_state["suggestions"].set(False)
