import asyncio

from shiny import render, reactive, ui

from core.logger import get_logger

from config import REFRESH_INTERVAL_SEC

log = get_logger("server")

from logic_engine import (
    run_system_workflows,
    run_intelligent_inspector,
    find_group_by_specs,
)

from database import add_model, delete_model

from silent_monitor import (
    get_database,
    monitor,
    get_database_async,
    monitor_async,
    run_ai_check,
    fix_ai_issue_index,
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
    draw_duplicate_issues,
    draw_ai_issues,
)

from ui_search import (
    draw_suggestions_curtain,
)

from ui_plans import (
    draw_modal_overlay,
    draw_wizard_size_modal,
    draw_wizard_panel_modal,
    draw_wizard_sensor_modal,
    draw_wizard_confirm_modal,
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


def _extract_unique_panels(db_data):

    panels = set()

    if not isinstance(db_data, dict):
        return []

    for size_group in db_data.values():

        if not isinstance(size_group, dict):
            continue

        for panel_name in size_group.keys():

            panel_name = str(panel_name or "").strip()

            if panel_name:
                panels.add(panel_name)

    return sorted(panels)


def _extract_unique_sensors(db_data):

    sensors = set()

    if not isinstance(db_data, dict):
        return []

    for size_group in db_data.values():

        if not isinstance(size_group, dict):
            continue

        for sensors_dict in size_group.values():

            if not isinstance(sensors_dict, dict):
                continue

            for sensor_name in sensors_dict.keys():

                sensor_name = str(sensor_name or "").strip()

                if sensor_name:
                    sensors.add(sensor_name)

    return sorted(sensors)


# ==========================================================
# SERVER
# ==========================================================

def server(input, output, session):

    workflow_state = reactive.value(None)

    show_curtain = reactive.value(False)

    show_not_found_modal = reactive.value(False)

    # ------ حالة الويزارد (البحث بالمواصفات عند فشل البحث بالاسم) ------
    wizard_step = reactive.value(None)          # None | "size" | "panel" | "sensor" | "confirm"
    wizard_phone = reactive.value("")
    wizard_size = reactive.value("")
    wizard_panel = reactive.value("")
    wizard_sensor = reactive.value("")
    wizard_panel_add_mode = reactive.value(False)
    wizard_sensor_add_mode = reactive.value(False)
    wizard_matched = reactive.value(None)

    # ------ حالة الإشعارات (مطوية + مقروء/غير مقروء) ------
    notif_expanded = reactive.value(None)   # موديل الإشعار المفتوح حالياً (أو None)
    notif_read = reactive.value(set())      # مجموعة أسماء الموديلات المقروءة

    def _reset_wizard():
        wizard_step.set(None)
        wizard_phone.set("")
        wizard_size.set("")
        wizard_panel.set("")
        wizard_sensor.set("")
        wizard_panel_add_mode.set(False)
        wizard_sensor_add_mode.set(False)
        wizard_matched.set(None)


    # ======================================================
    # HEALTH SNAPSHOT
    # ======================================================

    @reactive.calc
    async def health_snapshot():

        reactive.invalidate_later(REFRESH_INTERVAL_SEC)

        return await monitor_async() or {}

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

        database = await get_database_async() or {}

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

        if status == "success":

            _reset_wizard()

            show_not_found_modal.set(False)

        elif status == "plan_3":

            # فشل البحث بالاسم -> ابدأ الويزارد بالخطوة الأولى (المقاس)
            wizard_step.set("size")
            wizard_phone.set(query)
            wizard_size.set("")
            wizard_panel.set("")
            wizard_sensor.set("")
            wizard_panel_add_mode.set(False)
            wizard_sensor_add_mode.set(False)
            wizard_matched.set(None)

            show_not_found_modal.set(False)

        else:

            show_not_found_modal.set(False)


    # ======================================================
    # CLOSE PLAN 3 MODAL / WIZARD
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_close_modal, ignore_none=True)
    async def _close_modal():

        show_not_found_modal.set(False)

        _reset_wizard()


    # ======================================================
    # WIZARD STEP 1: SIZE -> NEXT
    # ======================================================

    @reactive.effect
    @reactive.event(input.wiz_size_next, ignore_none=True)
    def _wizard_size_next():

        size_val = str(input.wiz_size() or "").strip()

        if not size_val:
            return

        wizard_size.set(size_val)
        wizard_step.set("panel")


    # ======================================================
    # WIZARD STEP 2: PANEL -> TOGGLE ADD MODE
    # ======================================================

    @reactive.effect
    @reactive.event(input.wiz_show_add_panel, ignore_none=True)
    def _wizard_toggle_panel_add():

        wizard_panel_add_mode.set(
            not wizard_panel_add_mode()
        )


    # ======================================================
    # WIZARD STEP 2: PANEL -> NEXT
    # ======================================================

    @reactive.effect
    @reactive.event(input.wiz_panel_next, ignore_none=True)
    def _wizard_panel_next():

        if wizard_panel_add_mode():
            val = str(input.wiz_panel_new() or "").strip()
        else:
            val = str(input.wiz_panel() or "").strip()

        if not val or val == "-":
            return

        wizard_panel.set(val)
        wizard_step.set("sensor")


    # ======================================================
    # WIZARD STEP 3: SENSOR -> TOGGLE ADD MODE
    # ======================================================

    @reactive.effect
    @reactive.event(input.wiz_show_add_sensor, ignore_none=True)
    def _wizard_toggle_sensor_add():

        wizard_sensor_add_mode.set(
            not wizard_sensor_add_mode()
        )


    # ======================================================
    # WIZARD STEP 3: SENSOR -> SEARCH FOR MATCHING GROUP
    # ======================================================

    @reactive.effect
    @reactive.event(input.wiz_sensor_next, ignore_none=True)
    async def _wizard_sensor_next():

        if wizard_sensor_add_mode():
            val = str(input.wiz_sensor_new() or "").strip()
        else:
            val = str(input.wiz_sensor() or "").strip()

        if not val or val == "-":
            return

        wizard_sensor.set(val)

        database = await get_database_async() or {}

        specs = {
            "size": wizard_size(),
            "panel": wizard_panel(),
            "sensor": val,
        }

        matched = await asyncio.to_thread(
            find_group_by_specs,
            database,
            specs,
        )

        wizard_matched.set(matched)
        wizard_step.set("confirm")


    # ======================================================
    # WIZARD CONFIRM: SAVE (MERGE OR NEW GROUP)
    # ======================================================

    @reactive.effect
    @reactive.event(input.wiz_confirm_save, ignore_none=True)
    async def _wizard_confirm_save():

        phone = wizard_phone()
        size = wizard_size()
        panel = wizard_panel()
        sensor = wizard_sensor()

        try:

            ok = await asyncio.to_thread(
                add_model,
                size,
                panel,
                sensor,
                phone,
            )

        except Exception as e:

            log.error(f"Wizard save error: {e}")
            ok = False

        _reset_wizard()

        await get_database_async()

        if ok:

            ui.update_text(
                "search_query",
                value=phone,
            )


    # ======================================================
    # RUN INTELLIGENT INSPECTOR
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_run_inspector, ignore_none=True)
    async def _run_inspector():

        await asyncio.to_thread(run_intelligent_inspector)

        result = await asyncio.to_thread(run_ai_check)

        if result:
            log.info(
                f"AI check: فُحص {result['checked_now']}، "
                f"وُجد {result['found_now']} مشكلة، "
                f"متبقٍ {result['remaining']}"
            )

        await get_database_async()


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
    async def suggestions_curtain():

        if not show_curtain():

            return None

        query = str(
            input.search_query() or ""
        ).strip().lower()

        if not query:

            return None

        database = await get_database_async() or {}

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
    async def database_status_area():

        health = await health_snapshot()

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
    async def monitor_area():

        health = await health_snapshot()

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
    async def notification_area():

        health = await health_snapshot()

        issues = []

        if isinstance(health, dict):

            issues = health.get("duplicate_issues", [])

        read = notif_read()

        count = sum(
            1 for issue in issues
            if issue.get("model", "") not in read
        )

        return draw_notification_component(count)


    # ======================================================
    # DUPLICATE ISSUES (المراقب الصامت - عيني ويدي)
    # ======================================================

    @render.ui
    async def duplicate_issues_area():

        health = await health_snapshot()

        issues = []
        auto_log = []

        if isinstance(health, dict):

            issues = health.get("duplicate_issues", [])
            auto_log = health.get("auto_fix_log", [])

        return draw_duplicate_issues(
            issues,
            auto_log,
            notif_expanded(),
            notif_read(),
        )


    @reactive.effect
    @reactive.event(input.open_issue, ignore_none=True)
    def _toggle_issue():

        model = str(input.open_issue() or "")

        if not model:
            return

        # تعليمه كمقروء دائماً عند الضغط عليه
        current_read = set(notif_read())
        current_read.add(model)
        notif_read.set(current_read)

        # فتح/طي: لو كان مفتوحاً بالفعل، أغلقه؛ غير ذلك افتحه
        if notif_expanded() == model:
            notif_expanded.set(None)
        else:
            notif_expanded.set(model)


    @reactive.effect
    @reactive.event(input.fix_duplicate, ignore_none=True)
    async def _fix_duplicate():

        payload = str(input.fix_duplicate() or "")

        parts = payload.split("|")

        if len(parts) != 4:
            return

        model, size, panel, sensor = parts

        try:

            await asyncio.to_thread(
                delete_model,
                model,
                size,
                panel,
                sensor,
            )

        except Exception as e:

            log.error(f"Fix duplicate error: {e}")

        await get_database_async()


    # ======================================================
    # AI ISSUES (نتائج الفحص الذكي عبر Gemini)
    # ======================================================

    @render.ui
    async def ai_issues_area():

        health = await health_snapshot()

        ai_issues = []

        if isinstance(health, dict):

            ai_issues = health.get("ai_issues", [])

        return draw_ai_issues(ai_issues)


    @reactive.effect
    @reactive.event(input.fix_ai_issue, ignore_none=True)
    async def _fix_ai_issue():

        try:

            index = int(input.fix_ai_issue())

            await asyncio.to_thread(fix_ai_issue_index, index)

        except Exception as e:

            log.error(f"Fix AI issue error: {e}")

        await get_database_async()


    # ======================================================
    # SILENT INSPECTOR
    # ======================================================

    @render.ui
    def silent_inspector_area():

        return draw_silent_inspector()

    # ======================================================
    # WIZARD MODAL (الخطة 2/3)
    # ======================================================

    @render.ui
    async def dynamic_modal_container():

        step = wizard_step()

        if step is None:
            return None

        phone = wizard_phone()

        if step == "size":

            return draw_wizard_size_modal(phone)

        if step == "panel":

            database = await get_database_async() or {}

            panels = _extract_unique_panels(database)

            return draw_wizard_panel_modal(
                phone,
                panels,
                wizard_panel_add_mode(),
            )

        if step == "sensor":

            database = await get_database_async() or {}

            sensors = _extract_unique_sensors(database)

            return draw_wizard_sensor_modal(
                phone,
                sensors,
                wizard_sensor_add_mode(),
            )

        if step == "confirm":

            return draw_wizard_confirm_modal(
                phone,
                wizard_size(),
                wizard_panel(),
                wizard_sensor(),
                wizard_matched(),
            )

        return None


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
    async def _background_sync():

        reactive.invalidate_later(
            REFRESH_INTERVAL_SEC
        )

        try:

            await get_database_async()

            await health_snapshot()

        except Exception as e:

            log.error(f"Background sync error: {e}")


    # ======================================================
    # END SERVER
    # ======================================================

    return
