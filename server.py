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

from database import add_model, delete_model, update_model_specs

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

# قفل عالمي لمنع تشغيل فحصين ذكيين في نفس الوقت وتجنب استهلاك الحصة المجانية
is_inspector_running = False


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

    # ------ حالة التعديل اليدوي (القيم القديمة للصف المستهدف) ------
    edit_target = reactive.value(None)   # tuple: (model, old_size, old_panel, old_sensor)

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

            # تم الحذف: لا نفتح الويزارد تلقائياً لعدم مقاطعة كتابة المستخدم
            show_not_found_modal.set(False)

        else:

            show_not_found_modal.set(False)


    # ======================================================
    # TRIGGER WIZARD (التحكم التلقائي لبدء الويزارد بكامل الاسم)
    # ======================================================

    @reactive.effect
    @reactive.event(input.trigger_wizard, ignore_none=True)
    def _handle_trigger_wizard():
        phone = str(input.trigger_wizard() or "").strip()
        if phone:
            _reset_wizard()
            wizard_phone.set(phone)
            wizard_step.set("size")


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
            ui.notification_show("⚠️ يرجى إدخال مقاس الشاشة أولاً!", type="warning", duration=4)
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
            ui.notification_show("⚠️ يرجى اختيار أو كتابة نوع الشاشة!", type="warning", duration=4)
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
            ui.notification_show("⚠️ يرجى اختيار أو كتابة نوع المستشعر!", type="warning", duration=4)
            return

        wizard_sensor.set(val)

        try:
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
        except Exception as e:
            log.error(f"Error in wizard sensor step: {e}")
            ui.notification_show("❌ حدث خطأ غير متوقع أثناء معالجة البيانات.", type="error", duration=5)


    # ======================================================
    # WIZARD CONFIRM: SAVE (MERGE OR NEW GROUP)
    # ======================================================

    @reactive.effect
    @reactive.event(input.wiz_confirm_save, ignore_none=True)
    async def _wizard_confirm_save():

        phone = str(wizard_phone()).strip()
        size = str(wizard_size()).strip()
        panel = str(wizard_panel()).strip()
        sensor = str(wizard_sensor()).strip()

        if not all([phone, size, panel, sensor]):
            ui.notification_show("❌ مدخلات ناقصة، لا يمكن إتمام عملية التسجيل.", type="error", duration=5)
            return

        ui.notification_show("⏳ جاري إضافة الموديل الجديد وحفظه في السحابة...", type="message", duration=4)

        try:
            ok = await asyncio.to_thread(
                add_model,
                size,
                panel,
                sensor,
                phone,
            )
            if ok:
                ui.notification_show("✅ تم حفظ وإضافة الهاتف الجديد بنجاح!", type="message", duration=5)
                ui.update_text(
                    "search_query",
                    value=phone,
                )
            else:
                ui.notification_show("❌ فشل الاتصال بقاعدة البيانات، لم يتم الحفظ.", type="error", duration=5)
        except Exception as e:
            log.error(f"Wizard save error: {e}")
            ui.notification_show("❌ حدث خطأ داخلي أثناء الحفظ.", type="error", duration=5)
        finally:
            _reset_wizard()
            await get_database_async()


    # ======================================================
    # RUN INTELLIGENT INSPECTOR
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_run_inspector, ignore_none=True)
    async def _run_inspector():
        global is_inspector_running
        if is_inspector_running:
            ui.notification_show("⚠️ فحص ذكي جارٍ بالفعل، يرجى الانتظار لحين الانتهاء.", type="warning", duration=4)
            return

        is_inspector_running = True
        ui.notification_show("⏳ جاري تشغيل الفحص الذكي وتدقيق السجلات عبر السحابة...", type="message", duration=5)

        try:
            await asyncio.to_thread(run_intelligent_inspector)
            result = await asyncio.to_thread(run_ai_check)

            if result:
                log.info(
                    f"AI check: فُحص {result['checked_now']}، "
                    f"وُجد {result['found_now']} مشكلة، "
                    f"متبقٍ {result['remaining']}"
                )
            ui.notification_show("✅ اكتمل الفحص الذكي وتحديث البيانات الإحصائية!", type="message", duration=5)
        except Exception as e:
            log.error(f"Error in running inspector: {e}")
            ui.notification_show("❌ حدث خطأ أثناء تشغيل الفحص الذكي.", type="error", duration=5)
        finally:
            is_inspector_running = False
            await get_database_async()


    # ======================================================
    # DYNAMIC LOCAL SYNC (مزامنة الملف المحلي إلى Supabase)
    # ======================================================

    @reactive.effect
    @reactive.event(input.btn_sync_local_db, ignore_none=True)
    async def _sync_local_db():
        ui.notification_show("⏳ جاري بدء مزامنة ملف models_db.json المحمي إلى Supabase...", type="message", duration=5)
        
        try:
            import os
            import json
            from database import supabase
            from silent_monitor import refresh

            # تعديل المسار ليقرأ من الملف الخارجي الرئيسي المصحح مباشرة وتجنب المجلد الفرعي المكتوب فوقه
            JSON_FILE_PATH = "models_db.json"
            
            if not os.path.exists(JSON_FILE_PATH):
                ui.notification_show("❌ لم يتم العثور على ملف models_db.json الرئيسي!", type="error", duration=5)
                return

            with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            records = []
            for size, panels in data.items():
                if not isinstance(panels, dict):
                    continue
                for panel, sensors in panels.items():
                    if not isinstance(sensors, dict):
                        continue
                    for sensor, s_data in sensors.items():
                        models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                        if not isinstance(models_list, list):
                            continue
                        for model in models_list:
                            records.append({
                                "size": str(size).strip(),
                                "panel": str(panel).strip(),
                                "sensor": str(sensor).strip(),
                                "model_name": str(model).strip()
                            })

            total_records = len(records)
            
            # مسح الجدول القديم بالكامل لتفادي التكرار نهائياً
            supabase.table("phones").delete().neq("size", "none_existent_size").execute()
            
            # رفع البيانات الجديدة على دفعات (حجم الدفعة: 100)
            chunk_size = 100
            for i in range(0, total_records, chunk_size):
                chunk = records[i:i + chunk_size]
                supabase.table("phones").insert(chunk).execute()

            # تحديث الإحصائيات والكاش في التطبيق
            await asyncio.to_thread(refresh)
            await get_database_async()

            ui.notification_show(f"🎉 تم تحديث ومزامنة {total_records} هاتفاً بنجاح وتصفير الأخطاء!", type="message", duration=8)
        except Exception as e:
            log.error(f"Sync error: {e}")
            ui.notification_show(f"❌ حدث خطأ أثناء المزامنة: {str(e)}", type="error", duration=10)


    # ======================================================
    # WELCOME AREA
    # ======================================================

    @render.ui
    def welcome_area():

        if workflow_state() is None:

            return draw_welcome_header()

        return None


    # ======================================================
    # RESULTS (تنبيه ذكي غير مزعج بدلاً من المودال المفاجئ أثناء الكتابة)
    # ======================================================

    @render.ui
    def results_workflow_view():

        result = workflow_state()

        if not isinstance(result, dict):

            return None

        status = result.get("status", "")

        # إذا لم يكن الهاتف موجوداً، نعرض كارت أنيق يقترح عليه إضافة الهاتف بدلاً من فتح المودال قسراً أثناء الكتابة
        if status == "plan_3":
            query = str(input.search_query() or "").strip()
            return ui.div(
                ui.div(
                    f"⚠️ الهاتف '{query}' غير مسجل في قاعدة البيانات حالياً.",
                    class_="coord-line",
                    style="text-align:center; color: var(--text-muted); font-size:16px; border:none;"
                ),
                ui.tags.button(
                    f"➕ إضافة الموديل وتحديد مواصفاته الآن",
                    class_="btn-neon",
                    style="background: #3498db; color: white; margin-top:15px;",
                    onclick=f"Shiny.setInputValue('trigger_wizard', '{query}', {{priority:'event'}});"
                ),
                class_="glass-card neon-card"
            )

        if status != "success":

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
    # MANUAL EDIT (تعديل يدوي مباشر - بديل عند نفاد حصة AI)
    # ======================================================

    @reactive.effect
    @reactive.event(input.edit_target, ignore_none=True)
    def _set_edit_target():

        payload = str(input.edit_target() or "")

        parts = payload.split("|")

        if len(parts) != 4:
            return

        edit_target.set(tuple(parts))


    @reactive.effect
    @reactive.event(input.save_manual_edit, ignore_none=True)
    async def _save_manual_edit():

        target = edit_target()

        if not target:
            ui.notification_show("⚠️ يرجى اختيار هاتف للتعديل أولاً من الإشعارات.", type="warning", duration=4)
            return

        old_model, old_size, old_panel, old_sensor = target

        new_model = str(input.edit_model() or "").strip() or old_model
        new_size = str(input.edit_size() or "").strip()
        new_panel = str(input.edit_panel() or "").strip()
        new_sensor = str(input.edit_sensor() or "").strip()

        if not (new_size and new_panel and new_sensor):
            ui.notification_show("❌ جميع الحقول مطلوبة لإتمام عملية التعديل.", type="error", duration=4)
            return

        ui.notification_show("⏳ جاري تحديث بيانات الهاتف يدوياً في السحابة...", type="message", duration=4)

        try:
            if new_model != old_model:

                # تغيير الاسم أيضاً: نحذف القديم ونضيف الجديد بنفس المواصفات
                await asyncio.to_thread(
                    delete_model, old_model, old_size, old_panel, old_sensor
                )
                ok = await asyncio.to_thread(
                    add_model, new_size, new_panel, new_sensor, new_model
                )

            else:

                ok = await asyncio.to_thread(
                    update_model_specs,
                    old_model, old_size, old_panel, old_sensor,
                    new_size, new_panel, new_sensor,
                )

            if ok:
                edit_target.set(None)
                ui.update_text("edit_model", value="")
                ui.update_text("edit_size", value="")
                ui.update_text("edit_panel", value="")
                ui.update_text("edit_sensor", value="")
                ui.notification_show("✅ تم حفظ التعديل بنجاح وتحديث قاعدة البيانات!", type="message", duration=5)
            else:
                ui.notification_show("❌ لم نتمكن من حفظ التعديل، يرجى مراجعة اتصال السحابة.", type="error", duration=5)

        except Exception as e:
            log.error(f"Manual edit save error: {e}")
            ui.notification_show("❌ حدث خطأ داخلي أثناء حفظ التعديل اليدوي.", type="error", duration=5)
        finally:
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
--- START OF FILE glass-manager-main/ui_plans.py ---

from shiny import ui


# ==========================================================
# MODAL OVERLAY
# ==========================================================

def draw_modal_overlay(inner):

    if inner is None:
        return None

    return ui.div(

        inner,

        class_="modal-overlay"

    )


# ==========================================================
# WIZARD - STEP 1: SIZE
# ==========================================================

def draw_wizard_size_modal(phone):

    return draw_modal_overlay(

        ui.div(

            ui.h2("لم يتم العثور على الهاتف"),

            ui.p(f"الهاتف: {phone}"),

            ui.p("الخطوة 1 من 3 — أدخل مقاس الشاشة"),

            ui.input_text(
                "wiz_size",
                "المقاس (مثال: 6.5)"
            ),

            ui.div(

                ui.input_action_button(
                    "wiz_size_next",
                    "التالي ⟵",
                    class_="btn-neon"
                ),

                ui.input_action_button(
                    "btn_close_modal",
                    "إلغاء",
                    class_="btn-close"
                ),

                class_="modal-buttons"

            ),

            class_="glass-card modal-card"

        )

    )


# ==========================================================
# WIZARD - STEP 2: PANEL
# ==========================================================

def draw_wizard_panel_modal(phone, panels, add_mode=False):

    body = [

        ui.h2("لم يتم العثور على الهاتف"),

        ui.p(f"الهاتف: {phone}"),

        ui.p("الخطوة 2 من 3 — نوع الشاشة"),

    ]

    if add_mode:

        body.append(
            ui.input_text(
                "wiz_panel_new",
                "اكتب نوع الشاشة الجديد"
            )
        )

    else:

        body.append(
            ui.input_select(
                "wiz_panel",
                "اختر نوع الشاشة",
                choices=panels or ["-"]
            )
        )

    body.append(

        ui.input_action_button(
            "wiz_show_add_panel",
            "↩ اختيار من القائمة" if add_mode else "➕ نوع جديد غير موجود",
            class_="btn-close",
            style="background: #3498db !important; color: white !important; font-weight: 800; border-radius: 12px; margin-top: 10px; padding: 12px; border: none; cursor: pointer; pointer-events: auto !important;"
        )

    )

    body.append(

        ui.div(

            ui.input_action_button(
                "wiz_panel_next",
                "التالي ⟵",
                class_="btn-neon"
            ),

            ui.input_action_button(
                "btn_close_modal",
                "إلغاء",
                class_="btn-close"
            ),

            class_="modal-buttons"

        )

    )

    return draw_modal_overlay(
        ui.div(*body, class_="glass-card modal-card")
    )


# ==========================================================
# WIZARD - STEP 3: SENSOR
# ==========================================================

def draw_wizard_sensor_modal(phone, sensors, add_mode=False):

    body = [

        ui.h2("لم يتم العثور على الهاتف"),

        ui.p(f"الهاتف: {phone}"),

        ui.p("الخطوة 3 من 3 — مستشعر التقارب"),

    ]

    if add_mode:

        body.append(
            ui.input_text(
                "wiz_sensor_new",
                "اكتب اسم المستشعر الجديد"
            )
        )

    else:

        body.append(
            ui.input_select(
                "wiz_sensor",
                "اختر المستشعر",
                choices=sensors or ["-"]
            )
        )

    body.append(

        ui.input_action_button(
            "wiz_show_add_sensor",
            "↩ اختيار من القائمة" if add_mode else "➕ مستشعر جديد غير موجود",
            class_="btn-close",
            style="background: #3498db !important; color: white !important; font-weight: 800; border-radius: 12px; margin-top: 10px; padding: 12px; border: none; cursor: pointer; pointer-events: auto !important;"
        )

    )

    body.append(

        ui.div(

            ui.input_action_button(
                "wiz_sensor_next",
                "بحث عن مطابقة ⟵",
                class_="btn-neon"
            ),

            ui.input_action_button(
                "btn_close_modal",
                "إلغاء",
                class_="btn-close"
            ),

            class_="modal-buttons"

        )

    )

    return draw_modal_overlay(
        ui.div(*body, class_="glass-card modal-card")
    )


# ==========================================================
# WIZARD - CONFIRM (MERGE OR NEW GROUP)
# ==========================================================

def draw_wizard_confirm_modal(phone, size, panel, sensor, matched):

    if matched:

        title = "🟢 وُجدت مجموعة مطابقة"

        message = f'هل تريد إضافة "{phone}" إلى هذه المجموعة؟'

    else:

        title = "🆕 لا توجد مجموعة مطابقة"

        message = f'هل تريد تسجيل "{phone}" كمجموعة جديدة بهذه المواصفات؟'

    return draw_modal_overlay(

        ui.div(

            ui.h2(title),

            ui.p(message),

            ui.div(
                f"المقاس: {size}",
                class_="coord-line"
            ),

            ui.div(
                f"نوع الشاشة: {panel}",
                class_="coord-line"
            ),

            ui.div(
                f"المستشعر: {sensor}",
                class_="coord-line"
            ),

            ui.div(

                ui.input_action_button(
                    "wiz_confirm_save",
                    "✅ تأكيد الإضافة",
                    class_="btn-neon"
                ),

                ui.input_action_button(
                    "btn_close_modal",
                    "إلغاء",
                    class_="btn-close"
                ),

                class_="modal-buttons"

            ),

            class_="glass-card modal-card"

        )

    )


# ==========================================================
# PLAN 2 (قديم - غير مستخدم حالياً، أُبقي للتوافق)
# ==========================================================

def draw_plan_2_modal(
        phone="",
        panels=None,
        sensors=None
):

    panels = panels or []
    sensors = sensors or []


    return draw_modal_overlay(

        ui.div(

            ui.h2(
                "الخطة الثانية"
            ),


            ui.p(
                f"الهاتف: {phone}"
            ),


            ui.input_select(

                "p2_panel",

                "نوع الشاشة",

                choices=panels

            ),


            ui.input_select(

                "p2_sensor",

                "المستشعر",

                choices=sensors

            ),


            ui.div(

                ui.input_action_button(

                    "btn_plan2_save",

                    "💾 حفظ",

                    class_="btn-neon"

                ),


                ui.input_action_button(

                    "btn_close_modal",

                    "إغلاق",

                    class_="btn-close"

                ),


                class_="modal-buttons"

            ),


            class_="glass-card modal-card"

        )

    )



# ==========================================================
# PLAN 3 (قديم - غير مستخدم حالياً، أُبقي للتوافق)
# ==========================================================

def draw_plan_3_modal(
        phone="",
        result=None
):

    return draw_modal_overlay(

        ui.div(

            ui.h2(
                "الخطة الثالثة"
            ),


            ui.p(

                f"لم يتم العثور على نتائج للهاتف: {phone}"

            ),


            ui.input_text(

                "p3_size",

                "المقاس"

            ),


            ui.input_text(

                "p3_panel",

                "نوع الشاشة"

            ),


            ui.input_text(

                "p3_sensor",

                "المستشعر"

            ),


            # زر الإضافة المستقبلي +

            ui.input_action_button(

                "btn_plan3_save",

                "💾 إضافة",

                class_="btn-neon"

            ),


            ui.input_action_button(

                "btn_close_modal",

                "إغلاق",

                class_="btn-close"

            ),


            class_="glass-card modal-card"

        )

)
