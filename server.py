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
    draw_notification_component,
    draw_silent_inspector,
)

from ui_search import (
    draw_suggestions_curtain,
)

from ui_plans import (
    draw_modal_overlay,
    draw_plan_3_modal,
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

        database = get_database() or {}

        show_curtain.set(True)

        # التصحيح: اسم الوسيط هو phone وليس query
        result = run_system_workflows(

            phone=query,

            db_data=database,

        )

        workflow_state.set(result)

        if not isinstance(result, dict):

            show_not_found_modal.set(False)

            return

        status = result.get("status", "")

        coords = result.get("coords", {})

        real_name = str(
            coords.get("real_name", "")
        ).strip().lower()

        if (
            status == "success"
            and
            real_name == query.lower()
        ):

            show_curtain.set(False)

        show_not_found_modal.set(
            status == "plan_3"
        )


    # ======================================================
    # CLOSE PLAN 3 MODAL
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_close_modal, ignore_none=True)
    async def _close_modal():

        show_not_found_modal.set(False)


    # ======================================================
    # RUN INTELLIGENT INSPECTOR
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_run_inspector, ignore_none=True)
    async def _run_inspector():

        run_intelligent_inspector()

        get_database()


    # ======================================================
    # KEEP DATABASE + MONITOR ALIVE
    # ======================================================

    @reactive.effect
    def _background_refresh():

        reactive.invalidate_later(
            REFRESH_INTERVAL_SEC
        )

        get_database()

        health_snapshot()

    # ======================================================
    # WELCOME AREA
    # ======================================================

    @render.ui
    def welcome_area():

        if workflow_state() is None:

            return draw_welcome_header()

        return None


    # ======================================================
    # RESULTS
    # ======================================================

    @render.ui
    def results_workflow_view():

        result = workflow_state()

        if not isinstance(result, dict):

            return None

        if result.get("status") != "success":

            return None

        coords = result.get("coords") or {}

        compatibles = result.get("compatibles") or {}

        cards = []

        technical = draw_technical_coords(coords)

        if technical is not None:

            cards.append(technical)

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
                "تحذير: مستشعر مختلف",
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

                phone=coords.get("real_name", ""),

                section_type=key,

            )

            if section is not None:

                cards.append(section)

        if not cards:

            return None

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

        if not query:

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
    # SYSTEM INFO
    # ======================================================

    @render.ui
    def system_info_area():

        return draw_system_info()


    # ======================================================
    # DATABASE STATUS
    # ======================================================

    @render.ui
    def database_status_area():

        health = health_snapshot()

        statistics = {}

        if isinstance(health, dict):

            statistics = health.get(
                "statistics",
                {}
            )

        total = statistics.get(
            "phones",
            0
        )

        return draw_database_status(total)


    # ======================================================
    # MONITOR
    # ======================================================

    @render.ui
    def monitor_area():

        health = health_snapshot()

        status = "OFFLINE"

        if isinstance(health, dict):

            status = health.get(
                "status",
                "OFFLINE"
            )

        return draw_monitor_component(status)


    # ======================================================
    # NOTIFICATIONS
    # ======================================================

    @render.ui
    def notification_area():

        health = health_snapshot()

        count = 0

        if isinstance(health, dict):

            count = health.get(
                "notifications",
                0
            )

        return draw_notification_component(count)


    # ======================================================
    # SILENT INSPECTOR
    # ======================================================

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

        result = workflow_state() or {}

        phone = str(
            input.search_query() or ""
        ).strip()

        return draw_modal_overlay(

            draw_plan_3_modal(

                phone=phone,

                result=result,

            )

        )


    # ======================================================
    # CLEANUP WHEN SEARCH IS EMPTY
    # ======================================================

    @reactive.effect
    def _cleanup_empty_query():

        query = str(
            input.search_query() or ""
        ).strip()

        if query:

            return

        workflow_state.set(None)

        show_curtain.set(False)

        show_not_found_modal.set(False)


    # ======================================================
    # KEEP DATABASE UPDATED
    # ======================================================

    @reactive.effect
    def _background_sync():

        reactive.invalidate_later(
            REFRESH_INTERVAL_SEC
        )

        try:

            get_database()

            health_snapshot()

        except Exception:

            pass


    # ======================================================
    # END SERVER
    # ======================================================

    return
