from shiny import render, reactive, ui
import services as svs
from logic_engine import run_system_workflows, STATUS_PLAN_2, STATUS_PLAN_3
from silent_monitor import get_database, refresh
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_settings_modal
import json

AUTOCOMPLETE_INDEX = None

def server(input, output, session):

    ui_state = {
        "modal": reactive.Value(None),
        "suggestions": reactive.Value(False)
    }

    app_state = {
        "workflow": reactive.Value(None),
        "lock": reactive.Value(False)
    }

    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})
    initialized = reactive.Value(False)

    # 1. INIT
    @reactive.effect
    def _():
        if not initialized():
            global AUTOCOMPLETE_INDEX
            refresh()
            db = get_database()
            if isinstance(db, dict):
                p, s = svs.extract_panels_sensors(db)
                panels_cache.set(p)
                sensors_cache.set(s)
                AUTOCOMPLETE_INDEX = svs.build_autocomplete_index(
                    svs.load_models_index()
                )
            initialized.set(True)

    # 2. SEARCH ENGINE
    @reactive.effect
    def _():
        q = input.search_query()

        ui_state["suggestions"].set(bool(q and len(q) >= 2))

        if not q or len(q) < 2 or app_state["lock"]():
            return

        app_state["lock"].set(True)
        try:
            db = get_database()
            res = run_system_workflows(q, db)

            app_state["workflow"].set(res)

            status = res.get("status")
            if status in [STATUS_PLAN_2, STATUS_PLAN_3]:
                ui_state["modal"].set(status)
            else:
                ui_state["modal"].set(None)

        finally:
            app_state["lock"].set(False)

    # 3. SETTINGS
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _():
        ui_state["modal"].set("settings")

    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _():
        ui_state["modal"].set(None)

    # 4. MODAL RENDER
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
            return None

        if m == STATUS_PLAN_2:
            return draw_plan_2_modal(phone, panels_cache(), sensors_cache())

        if m == STATUS_PLAN_3:
            return draw_plan_3_modal(phone, res)

        return None

    # 5. AUTOCOMPLETE
    @render.ui
    def suggestions_curtain():
        if not ui_state["suggestions"]() or AUTOCOMPLETE_INDEX is None:
            return None

        q = input.search_query()
        if not q:
            return None

        results = AUTOCOMPLETE_INDEX.search_prefix(q, 5)
        if not results:
            return None

        onclick = """
        Shiny.setInputValue('search_query', val);
        Shiny.setInputValue('hide_suggestions', true);
        """

        return ui.div(
            *[
                ui.div(r, class_="suggestion-row",
                       onclick=f"var val={json.dumps(r)}; {onclick}")
                for r in results
            ],
            class_="suggestions-curtain"
        )

    # 6. CLOSE SUGGESTIONS
    @reactive.effect
    @reactive.event(input.hide_suggestions)
    def _():
        ui_state["suggestions"].set(False)
