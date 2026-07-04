from shiny import render, reactive, ui
import services as svs
from logic_engine import run_system_workflows, STATUS_PLAN_2, STATUS_PLAN_3
from silent_monitor import get_database, refresh
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_settings_modal
import json
import time


def server(input, output, session):

    # =========================
    # STATE LAYER (Clean Design)
    # =========================

    ui_state = {
        "modal": reactive.Value(None),
        "suggestions": reactive.Value(False)
    }

    app_state = {
        "workflow": reactive.Value(None),
        "lock": reactive.Value(False),
        "index": reactive.Value(None),
        "last_query": reactive.Value(""),
        "cache": reactive.Value({})  # query -> result cache
    }

    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})
    initialized = reactive.Value(False)

    last_time = reactive.Value(0.0)

    # =========================
    # INIT (SAFE + RETRY)
    # =========================

    @reactive.effect
    def _():
        if initialized():
            return

        try:
            refresh()
            db = get_database()

            if not isinstance(db, dict):
                reactive.invalidate_later(3)
                return

            p, s = svs.extract_panels_sensors(db)

            panels_cache.set(p or {})
            sensors_cache.set(s or {})

            app_state["index"].set(
                svs.build_autocomplete_index(svs.load_models_index())
            )

            initialized.set(True)

        except Exception:
            reactive.invalidate_later(3)

    # =========================
    # SEARCH ENGINE (ULTRA OPTIMIZED)
    # =========================

    @reactive.effect
    def _():
        q = input.search_query()

        if not q:
            ui_state["suggestions"].set(False)
            return

        # suggestions logic
        ui_state["suggestions"].set(len(q) >= 2)

        if len(q) < 2:
            return

        if app_state["lock"]():
            return

        # debounce (real-time guard)
        now = time.time()
        if now - last_time() < 0.25:
            return
        last_time.set(now)

        # avoid duplicate computation
        if q == app_state["last_query"]():
            return

        # CACHE HIT (big optimization)
        cache = app_state["cache"]()
        if q in cache:
            res = cache[q]
            app_state["workflow"].set(res)
            _handle_status(res)
            return

        app_state["lock"].set(True)

        try:
            db = get_database()
            if not isinstance(db, dict):
                return

            res = run_system_workflows(q, db)

            # save cache
            cache[q] = res
            app_state["cache"].set(cache)

            app_state["workflow"].set(res)
            app_state["last_query"].set(q)

            _handle_status(res)

        finally:
            app_state["lock"].set(False)

    # =========================
    # STATUS HANDLER (CLEAN)
    # =========================

    def _handle_status(res):
        status = (res or {}).get("status")

        if status in [STATUS_PLAN_2, STATUS_PLAN_3]:
            ui_state["modal"].set(status)
        else:
            ui_state["modal"].set(None)

    # =========================
    # UI EVENTS
    # =========================

    @reactive.effect
    @reactive.event(input.btn_settings)
    def _():
        ui_state["modal"].set("settings")

    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _():
        ui_state["modal"].set(None)

    @reactive.effect
    @reactive.event(input.hide_suggestions)
    def _():
        ui_state["suggestions"].set(False)

    # =========================
    # MODAL RENDER
    # =========================

    @render.ui
    def dynamic_modal_container():
        m = ui_state["modal"]()
        res = app_state["workflow"]()

        if not m:
            return None

        if m == "settings":
            return draw_settings_modal()

        phone = (res or {}).get("input_data", {}).get("phone")

        if not phone:
            return ui.div("جاري تحميل البيانات...")

        if m == STATUS_PLAN_2:
            return draw_plan_2_modal(phone, panels_cache(), sensors_cache())

        if m == STATUS_PLAN_3:
            return draw_plan_3_modal(phone, res)

        return None

    # =========================
    # AUTOCOMPLETE (SAFE + FAST)
    # =========================

    @render.ui
    def suggestions_curtain():
        if not ui_state["suggestions"]():
            return None

        idx = app_state["index"]()
        if not idx:
            return None

        q = input.search_query()
        if not q or len(q) < 2:
            return None

        results = idx.search_prefix(q, 5)
        if not results:
            return None

        return ui.div(
            *[
                ui.div(
                    r,
                    class_="suggestion-row",
                    onclick=f"Shiny.setInputValue('search_query', {json.dumps(r)}); Shiny.setInputValue('hide_suggestions', true);"
                )
                for r in results
            ],
            class_="suggestions-curtain"
        )
