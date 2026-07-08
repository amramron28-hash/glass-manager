from shiny import render, reactive, ui

from config import REFRESH_INTERVAL_SEC
from logic_engine import run_system_workflows, run_intelligent_inspector
from silent_monitor import get_database, monitor
from ui_components import (
    draw_technical_coords,
    draw_neon_section,
    draw_welcome_section,
    draw_system_info,
    draw_database_status,
    draw_monitor_component,
    draw_silent_inspector,
    draw_suggestions_curtain,
    draw_plan_3_modal,
    draw_modal_overlay,
)

MAX_SUGGESTIONS = 10


def _extract_unique_models(db_data: dict) -> list:
    """استخراج قائمة مسطحة وفريدة بكل أسماء الموديلات من قاعدة البيانات المتداخلة"""
    models = set()
    for panels in (db_data or {}).values():
        if not isinstance(panels, dict):
            continue
        for sensors in panels.values():
            if not isinstance(sensors, dict):
                continue
            for data in sensors.values():
                model_list = data.get("models", []) if isinstance(data, dict) else data
                if not isinstance(model_list, list):
                    continue
                for m in model_list:
                    if isinstance(m, str) and m.strip():
                        models.add(m.strip())
    return sorted(models)


def server(input, output, session):
    # حالة نتيجة البحث الحالية
    workflow_state = reactive.value(None)

    # هل صندوق اقتراحات البحث ظاهر أثناء الكتابة؟
    show_curtain = reactive.value(False)

    # هل مودال "غير موجود / الخطة الثالثة" ظاهر؟
    show_not_found_modal = reactive.value(False)

    # ============================================================
    # لقطة حالة موحّدة (قاعدة البيانات + المراقب الصامت) مع تحديث دوري
    # ============================================================
    @reactive.calc
    def health_snapshot():
        reactive.invalidate_later(REFRESH_INTERVAL_SEC)
        return monitor() or {}

    # ============================================================
    # البحث عند الكتابة
    # ============================================================
    @reactive.effect
    @reactive.event(input.search_query, ignore_none=True)
    async def _run_search():
        query = str(input.search_query() or "").strip()

        if len(query) < 2:
            workflow_state.set(None)
            show_curtain.set(False)
            show_not_found_modal.set(False)
            return

        # جلب البيانات (يدعم النسخة الاحتياطية المحلية تلقائياً عند تعطل Supabase)
        db = get_database() or {}
        res = run_system_workflows(query, db_data=db)
        workflow_state.set(res)

        # إخفاء قائمة الاقتراحات تلقائياً عند إيجاد مطابقة تامة للنص المكتوب،
        # وإبقاؤها ظاهرة أثناء الكتابة الجزئية
        matched_exactly = (
            bool(res)
            and res.get("status") == "success"
            and res.get("coords", {}).get("real_name", "").strip().lower() == query.lower()
        )
        show_curtain.set(not matched_exactly)

        show_not_found_modal.set(bool(res) and res.get("status") == "plan_3")

    # إغلاق أي مودال ديناميكي مفتوح
    @reactive.effect
    @reactive.event(input.btn_close_modal, ignore_none=True)
    async def _close_modal():
        show_not_found_modal.set(False)

    # ============================================================
    # تشغيل فحص/تنظيف قاعدة البيانات يدوياً من لوحة الإعدادات
    # ============================================================
    @reactive.effect
    @reactive.event(input.btn_run_inspector, ignore_none=True)
    async def _run_inspector():
        run_intelligent_inspector()
        # إجبار جلب بيانات جديدة عند البحث التالي
        get_database()

    # ============================================================
    # شاشة الترحيب (تظهر فقط قبل أي بحث)
    # ============================================================
    @render.ui
    def welcome_area():
        if workflow_state() is None:
            return draw_welcome_section()
        return None

    # ============================================================
    # نتائج البحث (تنسيقات المطابقة)
    # ============================================================
    @render.ui
    def results_workflow_view():
        res = workflow_state()
        if not res or res.get("status") != "success":
            return None

        c = res.get("coords", {})
        comp = res.get("compatibles", {})

        return ui.TagList(
            draw_technical_coords(c),
            draw_neon_section("مطابقة تماماً", comp.get("exact", []), "exact"),
            draw_neon_section("إضافات", comp.get("plus", []), "plus"),
            draw_neon_section("أصغر", comp.get("minus", []), "minus"),
        )

    # ============================================================
    # قائمة الاقتراحات المنسدلة أثناء الكتابة
    # ============================================================
    @render.ui
    def suggestions_curtain():
        if not show_curtain():
            return None

        query = str(input.search_query() or "").strip().lower()
        if len(query) < 2:
            return None

        db = get_database() or {}
        all_models = _extract_unique_models(db)
        matches = [m for m in all_models if query in m.lower()][:MAX_SUGGESTIONS]

        return draw_suggestions_curtain(matches)

    # ============================================================
    # لوحة الإعدادات (المتصلة بالمراقب الصامت silent_monitor)
    # ============================================================
    @render.ui
    def system_info_area():
        return draw_system_info()

    @render.ui
    def database_status_area():
        health = health_snapshot()
        stats = health.get("statistics", {}) if isinstance(health, dict) else {}
        total = stats.get("phones", 0) if isinstance(stats, dict) else 0
        return draw_database_status(total)

    @render.ui
    def monitor_area():
        health = health_snapshot()
        label = health.get("status", "UNKNOWN") if isinstance(health, dict) else "UNKNOWN"
        return draw_monitor_component(label)

    @render.ui
    def silent_inspector_area():
        return draw_silent_inspector()

    # ============================================================
    # المودال الديناميكي (يظهر عند عدم إيجاد الموديل - الخطة الثالثة)
    # ============================================================
    @render.ui
    def dynamic_modal_container():
        if show_not_found_modal():
            return draw_modal_overlay(draw_plan_3_modal())
        return None
