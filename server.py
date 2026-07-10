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

                    if not isinstance(model, str):
                        continue

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
    # DATABASE STATUS (يتحدث تلقائياً كل عدة ثوان)
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

        if query == "":

            workflow_state.set(None)
            show_curtain.set(False)
            show_not_found_modal.set(False)
            return

        show_curtain.set(True)

        database = get_database() or {}

        result = run_system_workflows(
            query=query,
            db_data=database,
        )

        workflow_state.set(result)

        if not result:
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

        if status == "plan_3":

            show_not_found_modal.set(True)

        else:

            show_not_found_modal.set(False)


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

        # إعادة تحميل قاعدة البيانات بعد الفحص
        get_database()


    # ======================================================
    # KEEP DATABASE CONNECTED
    # ======================================================

    @reactive.effect
    def _keep_database_alive():

        reactive.invalidate_later(REFRESH_INTERVAL_SEC)

        get_database()


    # ======================================================
    # KEEP MONITOR ALIVE
    # ======================================================

    @reactive.effect
    def _keep_monitor_alive():

        health_snapshot()
    # ======================================================
    # WELCOME AREA
    # ======================================================

    @render.ui
    def welcome_area():

        # تظهر الصورة فقط قبل البحث
        if workflow_state() is None:
            return draw_welcome_header()

        return None


    # ======================================================
    # RESULTS
    # ======================================================

    @render.ui
    def results_workflow_view():

        result = workflow_state()

        if result is None:
            return None

        if result.get("status") != "success":
            return None

        coords = result.get("coords", {})
        compatibles = result.get("compatibles", {})

        cards = []

        phone_card = draw_technical_coords(coords)

        if phone_card is not None:
            cards.append(phone_card)

        sections = [

            (
                "exact",
                "مطابقة تماماً",
                "#2ecc71",
                "🟢",
                "exact",
            ),

            (
                "plus",
                "أكبر بقليل",
                "#3498db",
                "🔵",
                "plus",
            ),

            (
                "minus",
                "أصغر بقليل",
                "#e67e22",
                "🟠",
                "minus",
            ),

            (
                "warn",
                "تحذير: مستشعر مختلف",
                "#ef4444",
                "⚠️",
                "warn",
            ),

        ]

        for key, title, color, icon, section_type in sections:

            models = compatibles.get(key, [])

            if not models:
                continue

            section = draw_neon_section(

                title=title,
                models=models,
                color=color,
                icon=icon,
                section_type=section_type,

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

        if query == "":
            return None

        database = get_database() or {}

        models = _extract_unique_models(database)

        matches = [
            model
            for model in models
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

        statistics = health.get("statistics", {})

        phones = statistics.get("phones", 0)

        return draw_database_status(phones)


    # ======================================================
    # MONITOR STATUS
    # ======================================================

    @render.ui
    def monitor_area():

        health = health_snapshot()

        status = "UNKNOWN"

        if isinstance(health, dict):

            status = health.get(
                "status",
                "UNKNOWN"
            )

        return draw_monitor_component(status)


    # ======================================================
    # NOTIFICATIONS
    # ======================================================

    @render.ui
    def notification_area():

        health = health_snapshot()

        notifications = 0

        if isinstance(health, dict):

            notifications = health.get(
                "notifications",
                0
            )

        return draw_notification_component(notifications)


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

        coords = result.get("coords", {})

        phone = coords.get(
            "real_name",
            str(input.search_query() or "").strip()
        )

        return draw_modal_overlay(

            draw_plan_3_modal(
                phone=phone,
                result=result,
            )

        )


    # ======================================================
    # CLEAN EMPTY QUERY
    # ======================================================

    @reactive.effect
    def _cleanup_state():

        query = str(
            input.search_query() or ""
        ).strip()

        if query:
            return

        workflow_state.set(None)

        show_curtain.set(False)

        show_not_found_modal.set(False)


    # ======================================================
    # REFRESH DATABASE
    # ======================================================

    @reactive.effect
    def _refresh_database():

        reactive.invalidate_later(REFRESH_INTERVAL_SEC)

        get_database()


    # ======================================================
    # REFRESH MONITOR
    # ======================================================

    @reactive.effect
    def _refresh_monitor():

        reactive.invalidate_later(REFRESH_INTERVAL_SEC)

        monitor()
    # ======================================================
    # KEEP DATABASE SYNCHRONIZED
    # ======================================================

    @reactive.effect
    def _sync_database():

        reactive.invalidate_later(REFRESH_INTERVAL_SEC)

        try:

            # يعيد تحميل قاعدة البيانات (ومنها Supabase إذا كان
            # get_database() يعتمد عليها)
            get_database()

        except Exception:

            pass


    # ======================================================
    # KEEP HEALTH SNAPSHOT UPDATED
    # ======================================================

    @reactive.effect
    def _update_health():

        reactive.invalidate_later(REFRESH_INTERVAL_SEC)

        health_snapshot()


    # ======================================================
    # KEEP SEARCH STATE CONSISTENT
    # ======================================================

    @reactive.effect
    def _hide_results_when_empty():

        if str(input.search_query() or "").strip():

            return

        workflow_state.set(None)

        show_curtain.set(False)

        show_not_found_modal.set(False)


    # ======================================================
    # END SERVER
    # ======================================================

    return     
