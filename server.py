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

def _extract_unique_models(db_data):
    models = set()
    for panels in (db_data or {}).values():
        if not isinstance(panels, dict): continue
        for sensors in panels.values():
            if not isinstance(sensors, dict): continue
            for data in sensors.values():
                model_list = data.get("models", []) if isinstance(data, dict) else data
                if not isinstance(model_list, list): continue
                for model in model_list:
                    if isinstance(model, str) and model.strip():
                        models.add(model.strip())
    return sorted(models)

# ======================================================
# SERVER LOGIC
# ======================================================

def server(input, output, session):
    workflow_state = reactive.value(None)
    show_curtain = reactive.value(False)
    show_not_found_modal = reactive.value(False)

    @reactive.calc
    def health_snapshot():
        reactive.invalidate_later(REFRESH_INTERVAL_SEC)
        return monitor() or {}

    @reactive.effect
    @reactive.event(input.search_query, ignore_none=False)
    async def _run_search():
        query = str(input.search_query() or "").strip()
        show_curtain.set(len(query) >= 1)
        
        if not query:
            workflow_state.set(None)
            show_not_found_modal.set(False)
            return

        db = get_database() or {}
        res = run_system_workflows(query, db_data=db)
        workflow_state.set(res)

        # المنطق الخاص بالمطابقة التامة
        matched_exact = (bool(res) and res.get("status") == "success" and 
                         res.get("coords", {}).get("real_name", "").strip().lower() == query.lower())
        
        if matched_exact:
            show_curtain.set(False)
        show_not_found_modal.set(bool(res) and res.get("status") == "plan_3")

    @reactive.effect
    @reactive.event(input.btn_close_modal, ignore_none=True)
    async def _close_modal():
        show_not_found_modal.set(False)

    @reactive.effect
    @reactive.event(input.btn_run_inspector, ignore_none=True)
    async def _run_inspector():
        run_intelligent_inspector()
        get_database() 

    # ======================================================
    # RENDER UI OUTPUTS
    # ======================================================

    @render.ui
    def welcome_area():
        # يعرض الترحيب فقط عند عدم وجود نتيجة
        return draw_welcome_header() if workflow_state() is None else None

    @render.ui
    def results_workflow_view():
        res = workflow_state()
        if not res or res.get("status") != "success": return None
        
        coords = res.get("coords", {})
        results = res.get("compatibles", {})
        output_cards = [draw_technical_coords(coords)]

        # إضافة النتائج مع تمرير section_type لضمان ألوان النيون
        if results.get("exact"): 
            output_cards.append(draw_neon_section("مطابقة تماماً", results["exact"], "#2ecc71", "🟢", section_type="exact"))
        if results.get("plus"): 
            output_cards.append(draw_neon_section("أكبر بقليل", results["plus"], "#3498db", "🔵", section_type="plus"))
        if results.get("minus"): 
            output_cards.append(draw_neon_section("أصغر بقليل", results["minus"], "#e67e22", "🟤", section_type="minus"))
        if results.get("warn"): 
            output_cards.append(draw_neon_section("تنبيه: مستشعر مختلف", results["warn"], "#ef4444", "⚠️", section_type="warn"))

        return ui.TagList(*output_cards)

    @render.ui
    def suggestions_curtain():
        if not show_curtain(): return None
        query = str(input.search_query() or "").strip().lower()
        if len(query) < 1: return None
        db = get_database() or {}
        matches = [m for m in _extract_unique_models(db) if query in m.lower()][:MAX_SUGGESTIONS]
        return draw_suggestions_curtain(list(dict.fromkeys(matches)))

    @render.ui
    def system_info_area(): return draw_system_info()

    @render.ui
    def database_status_area():
        health = health_snapshot()
        stats = health.get("statistics", {}) if isinstance(health, dict) else {}
        return draw_database_status(stats.get("phones", 0))

    @render.ui
    def monitor_area():
        health = health_snapshot()
        return draw_monitor_component(health.get("status", "UNKNOWN") if isinstance(health, dict) else "UNKNOWN")

    @render.ui
    def silent_inspector_area(): return draw_silent_inspector()

    @render.ui
    def dynamic_modal_container():
        return draw_modal_overlay(draw_plan_3_modal()) if show_not_found_modal() else None
