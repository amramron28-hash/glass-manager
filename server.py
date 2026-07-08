from __future__ import annotations
import asyncio
import logging
from shiny import render, reactive, ui, output
import services as svs
from logic_engine import run_system_workflows
from silent_monitor import get_database, get_db_hash
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, draw_technical_coords, 
    draw_neon_section, draw_welcome_section, draw_database_status,
    draw_monitor_component, draw_silent_inspector, draw_system_info
)

logger = logging.getLogger("glass_manager")

def server(input, output, session):
    # الحالات التفاعلية
    workflow_state = reactive.value(None)
    modal_state = reactive.value(None)
    suggestions_state = reactive.value(False)
    db_total_models = reactive.value(0)
    inspector_status = reactive.value("READY")
    
    # 1. تهيئة البيانات
    @reactive.effect
    def _init():
        try:
            db = get_database() or {}
            total = sum(len(p.get("models", [])) for p in db.values() if isinstance(p, dict))
            db_total_models.set(total)
        except Exception as e:
            logger.error(f"Init Error: {e}")

    # 2. البحث الذكي (مع تصفية القيم الفارغة)
    @reactive.effect
    @reactive.event(input.search_query, ignore_none=True)
    async def _run_search():
        query = str(input.search_query() or "").strip()
        if len(query) < 2:
            workflow_state.set(None)
            suggestions_state.set(False)
            return

        db = get_database() or {}
        res = run_system_workflows(query, db)
        workflow_state.set(res)
        
        # إدارة المودالات
        status = res.get("status")
        modal_state.set("plan2" if status == "plan_2" else "plan3" if status == "plan_3" else None)
        suggestions_state.set(True)

    # 3. المخرجات (ربط Outputs بالـ UI)
    @output
    @render.ui
    def system_info_area(): return draw_system_info()

    @output
    @render.ui
    def database_status_area(): return draw_database_status(db_total_models())

    @output
    @render.ui
    def monitor_area(): return draw_monitor_component(inspector_status())

    @output
    @render.ui
    def silent_inspector_area(): return draw_silent_inspector()

    @output
    @render.ui
    def welcome_area(): 
        return draw_welcome_section() if workflow_state() is None else None

    @output
    @render.ui
    def results_workflow_view():
        res = workflow_state()
        if not res or res.get("status") != "success": return None
        
        c = res.get("coords", {})
        comp = res.get("compatibles", {})
        
        return ui.TagList(
            draw_technical_coords(c),
            draw_neon_section("مطابقة تماماً", comp.get("exact", []), "exact"),
            draw_neon_section("أكبر بقليل", comp.get("plus", []), "plus"),
            draw_neon_section("أصغر بقليل", comp.get("minus", []), "minus")
        )

    @output
    @render.ui
    def dynamic_modal_container():
        m = modal_state()
        if m == "plan2": return draw_plan_2_modal()
        if m == "plan3": return draw_plan_3_modal()
        return None

    # 4. إغلاق المودال
    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _close_modal():
        modal_state.set(None)

    # 5. تنظيف الجلسة
    @session.on_ended
    def _cleanup():
        workflow_state.set(None)
        modal_state.set(None)
