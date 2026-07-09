from shiny import render, reactive, ui

from config import REFRESH_INTERVAL_SEC

from logic_engine import (
    run_system_workflows,
    run_intelligent_inspector,
)

from silent_monitor import (
    get_database,
    monitor,
)

from ui_cards import (
    draw_technical_coords,
    draw_neon_section,
)

from ui_header import (
    draw_welcome_header,
)

from ui_settings import (
    draw_system_info,
    draw_database_status,
    draw_monitor_component,
    draw_silent_inspector,
)

from ui_search import (
    draw_suggestions_curtain,
)

from ui_plans import (
    draw_plan_3_modal,
    draw_modal_overlay,
)

MAX_SUGGESTIONS = 10


# ==========================================================
# DATABASE HELPERS
# ==========================================================

def _extract_unique_models(db_data):

    models = set()

    if not isinstance(db_data, dict):
        return []

    for panels in db_data.values():

        if not isinstance(panels, dict):
            continue

        for sensors in panels.values():

            if not isinstance(sensors, dict):
                continue

            for value in sensors.values():

                if isinstance(value, dict):
                    items = value.get("models", [])
                else:
                    items = value

                if not isinstance(items, list):
                    continue

                for model in items:

                    if isinstance(model, str):

                        model = model.strip()

                        if model:
                            models.add(model)

    return sorted(models)


# ==========================================================
# SERVER
# ==========================================================

def server(input, output, session):

    workflow_state = reactive.value(None)

    show_curtain = reactive.value(False)

    show_not_found_modal = reactive.value(False)

    show_settings_drawer = reactive.value(False)
    # ======================================================
    # HEALTH SNAPSHOT
    # ======================================================

    @reactive.calc
    def health_snapshot():

        reactive.invalidate_later(REFRESH_INTERVAL_SEC)

        return monitor() or {}


    # ======================================================
    # SEARCH WORKFLOW
    # ======================================================

    @reactive.effect
    @reactive.event(input.search_query, ignore_none=False)
    async def _run_search():

        query = str(input.search_query() or "").strip()

        if not query:

            workflow_state.set(None)

            show_curtain.set(False)

            show_not_found_modal.set(False)

            return

        show_curtain.set(True)

        db = get_database() or {}

        result = run_system_workflows(

            query,

            db_data=db,

        )

        workflow_state.set(result)

        if not result:

            return

        coords = result.get("coords", {})

        real_name = str(

            coords.get("real_name", "")

        ).strip().lower()

        if (

            result.get("status") == "success"

            and

            real_name == query.lower()

        ):

            show_curtain.set(False)

        show_not_found_modal.set(

            result.get("status") == "plan_3"

        )


    # ======================================================
    # CLOSE MODAL
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_close_modal, ignore_none=True)
    async def _close_modal():

        show_not_found_modal.set(False)


    # ======================================================
    # RUN INSPECTOR
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_run_inspector, ignore_none=True)
    async def _run_inspector():

        run_intelligent_inspector()

        get_database()


    # ======================================================
    # SETTINGS DRAWER
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_open_drawer, ignore_none=True)
    async def _open_drawer():

        show_settings_drawer.set(True)


    @reactive.effect
    @reactive.event(
        input.btn_close_drawer_trigger,
        ignore_none=True,
    )
    async def _close_drawer():

        show_settings_drawer.set(False)
    # ======================================================
    # WELCOME AREA
    # ======================================================

    @render.ui
    def welcome_area():

        if workflow_state() is None:

            return draw_welcome_header()

        return None


    # ======================================================
    # RESULTS AREA
    # ======================================================

    @render.ui
    def results_workflow_view():

        result = workflow_state()

        if result is None:

            return None

        if result.get("status") != "success":

            return None

        coords = result.get("coords") or {}

        compatibles = result.get("compatibles") or {}

        cards = []

        technical_card = draw_technical_coords(coords)

        if technical_card is not None:

            cards.append(technical_card)

        sections = [

            (
                "exact",
                "مطابقة تماماً",
                "#2ecc71",
                "🟢",
            ),

            (
                "plus",
                "أكبر بقليل",
                "#3498db",
                "🔵",
            ),

            (
                "minus",
                "أصغر بقليل",
                "#e67e22",
                "🟠",
            ),

            (
                "warn",
                "تنبيه: مستشعر مختلف",
                "#ef4444",
                "⚠️",
            ),

        ]

        for key, title, color, icon in sections:

            models = compatibles.get(key, [])

            if not models:

                continue

            section = draw_neon_section(

                title=title,

                models=models,

                color=color,

                icon=icon,

                section_type=key,

            )

            if section is not None:

                cards.append(section)

        return ui.TagList(*cards)


    # ======================================================
    # AUTOCOMPLETE
    # ======================================================

    @render.ui
    def suggestions_curtain():

        if not show_curtain():

            return None

        query = str(

            input.search_query() or ""

        ).strip().lower()

        if len(query) < 1:

            return None

        database = get_database() or {}

        all_models = _extract_unique_models(database)

        matches = [

            model

            for model in all_models

            if query in model.lower()

        ][:MAX_SUGGESTIONS]

        if not matches:

            return None

        return draw_suggestions_curtain(matches)


    # ======================================================
    # SETTINGS
    # ======================================================

    @render.ui
    def system_info_area():

        return draw_system_info()


    @render.ui
    def database_status_area():

        health = health_snapshot()

        statistics = health.get(

            "statistics",

            {},

        )

        return draw_database_status(

            statistics.get(

                "phones",

                0,

            )

        )


    @render.ui
    def monitor_area():

        health = health_snapshot()

        status = "UNKNOWN"

        if isinstance(health, dict):

            status = health.get(

                "status",

                "UNKNOWN",

            )

        return draw_monitor_component(status)


    @render.ui
    def silent_inspector_area():

        return draw_silent_inspector()


    # ======================================================
    # PLAN 3 MODAL
    # ======================================================

    @render.ui
    def dynamic_modal_container():

        if not show_not_found_modal():

            return None

        return draw_modal_overlay(

            draw_plan_3_modal()

        )
    # ======================================================
    # SETTINGS DRAWER SCRIPT
    # ======================================================

    @render.ui
    def settings_drawer_script():

        if show_settings_drawer():

            return ui.tags.script("""
(function(){

const drawer=document.getElementById("settings-drawer");

if(drawer){

drawer.classList.add("drawer-open");

}

})();
""")

        return ui.tags.script("""
(function(){

const drawer=document.getElementById("settings-drawer");

if(drawer){

drawer.classList.remove("drawer-open");

}

})();
""")


    # ======================================================
    # KEEP HEALTH MONITOR ALIVE
    # ======================================================

    @reactive.effect
    def _keep_monitor_alive():

        health_snapshot()


    # ======================================================
    # KEEP DATABASE LOADED
    # ======================================================

    @reactive.effect
    def _keep_database_alive():

        get_database()


    # ======================================================
    # KEEP WORKFLOW STATE SAFE
    # ======================================================

    @reactive.effect
    def _cleanup_empty_query():

        query = str(input.search_query() or "").strip()

        if query:

            return

        workflow_state.set(None)

        show_curtain.set(False)

        show_not_found_modal.set(False)


    # ======================================================
    # END SERVER
    # ======================================================
