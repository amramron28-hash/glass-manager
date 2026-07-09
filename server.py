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
    draw_welcome_header as draw_welcome_section,
)

from ui_settings import (
    draw_system_info,
    draw_database_status,
    draw_monitor_component,
    draw_silent_inspector,
    draw_notification_component,
)

from ui_search import (
    draw_suggestions_curtain,
)

from ui_plans import (
    draw_plan_3_modal,
    draw_modal_overlay,
)

MAX_SUGGESTIONS = 10
    # ======================================================
    # SEARCH ENGINE
    # ======================================================

    @reactive.effect
    @reactive.event(
        input.search_query,
        ignore_none=False,
    )
    async def _run_search():

        query = str(
            input.search_query() or ""
        ).strip()

        # إظهار الاقتراحات من أول حرف
        show_curtain.set(len(query) >= 1)

        if not query:

            workflow_state.set(None)

            show_not_found_modal.set(False)

            return

        db = get_database() or {}

        res = run_system_workflows(
            query,
            db_data=db
        )

        workflow_state.set(res)

        matched_exact = (

            bool(res)

            and res.get("status") == "success"

            and res.get("coords", {})
            .get("real_name", "")
            .strip()
            .lower()

            == query.lower()

        )

        # عند المطابقة التامة تختفي الستارة
        if matched_exact:
            show_curtain.set(False)

        show_not_found_modal.set(

            bool(res)

            and res.get("status") == "plan_3"

        )


    # ======================================================
    # CLOSE PLAN MODAL
    # ======================================================

    @reactive.effect
    @reactive.event(
        input.btn_close_modal,
        ignore_none=True,
    )
    async def _close_modal():

        show_not_found_modal.set(False)


    # ======================================================
    # RUN SILENT INSPECTOR
    # ======================================================

    @reactive.effect
    @reactive.event(
        input.btn_run_inspector,
        ignore_none=True,
    )
    async def _run_inspector():

        run_intelligent_inspector()

        # تحديث قاعدة البيانات بعد الفحص
        get_database()
    # ======================================================
    # WELCOME
    # ======================================================

    @render.ui
    def welcome_area():

        if workflow_state() is None:
            return draw_welcome_section()

        return None


    # ======================================================
    # RESULTS
    # ======================================================

    @render.ui
    def results_workflow_view():

        res = workflow_state()

        if not res:
            return None

        if res.get("status") != "success":
            return None

        coords = res.get("coords", {})
        results = res.get("compatibles", {})

        output_cards = []

        # البطاقة الرئيسية
        output_cards.append(
            draw_technical_coords(coords)
        )

        # مطابق تماماً
        if results.get("exact"):

            output_cards.append(

                draw_neon_section(

                    "هواتف مطابقة تماماً في الأبعاد والقص (Exact 0.00)",

                    results["exact"],

                    "#2ecc71",

                    "🟢"

                )

            )

        # أكبر قليلاً
        if results.get("plus"):

            output_cards.append(

                draw_neon_section(

                    "هواتف أكبر بقليل متوافقة (Plus +0.01 → +0.03)",

                    results["plus"],

                    "#3498db",

                    "🔵"

                )

            )

        # أصغر قليلاً
        if results.get("minus"):

            output_cards.append(

                draw_neon_section(

                    "هواتف أصغر بقليل متوافقة (Minus -0.01 → -0.03)",

                    results["minus"],

                    "#e67e22",

                    "🟤"

                )

            )

        # تحذير اختلاف المستشعر
        if results.get("warn"):

            output_cards.append(

                draw_neon_section(

                    "تنبيه: نفس المقاس لكن مستشعر مختلف",

                    results["warn"],

                    "#ef4444",

                    "⚠️"

                )

            )

        return ui.TagList(*output_cards)
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

        # يبدأ الاقتراح من أول حرف
        if len(query) < 1:
            return None

        db = get_database() or {}

        models = _extract_unique_models(db)

        matches = [
            model
            for model in models
            if query in model.lower()
        ]

        # إزالة التكرارات مع الحفاظ على الترتيب
        matches = list(dict.fromkeys(matches))

        # الحد الأقصى
        matches = matches[:MAX_SUGGESTIONS]

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

        stats = (
            health.get("statistics", {})
            if isinstance(health, dict)
            else {}
        )

        total = (
            stats.get("phones", 0)
            if isinstance(stats, dict)
            else 0
        )

        return draw_database_status(total)


    @render.ui
    def monitor_area():

        health = health_snapshot()

        status = (
            health.get("status", "UNKNOWN")
            if isinstance(health, dict)
            else "UNKNOWN"
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

        if show_not_found_modal():

            return draw_modal_overlay(
                draw_plan_3_modal()
            )

        return None
        
