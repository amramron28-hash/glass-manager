from shiny import render, reactive, ui
from logic_engine import run_system_workflows
from silent_monitor import get_database
from ui_components import draw_technical_coords, draw_neon_section, draw_welcome_section

def server(input, output, session):
    # حالة البحث
    workflow_state = reactive.value(None)

    # معالجة البحث عند الكتابة
    @reactive.effect
    @reactive.event(input.search_query, ignore_none=True)
    async def _run_search():
        query = str(input.search_query() or "").strip()
        if len(query) < 2:
            workflow_state.set(None)
            return
        
        # جلب البيانات وتشغيل المحرك
        db = get_database() or {}
        res = run_system_workflows(query, db)
        workflow_state.set(res)

    # عرض شاشة الترحيب فقط إذا لم تكن هناك نتائج
    @render.ui
    def welcome_area():
        if workflow_state() is None:
            return draw_welcome_section()
        return None

    # عرض النتائج
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
            draw_neon_section("أصغر", comp.get("minus", []), "minus")
        )
