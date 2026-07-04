hereimport json
import time
from shiny import render, reactive, ui
import services as svs
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, draw_database_status, 
    draw_monitor_component, draw_notifications, draw_technical_coords, 
    draw_neon_section, draw_warning_card
)
from silent_monitor import get_database, get_status, refresh
from logic_engine import (
    run_system_workflows, STATUS_SUCCESS, STATUS_PLAN_2, STATUS_PLAN_3, 
    STATUS_PLAN2_SUCCESS, STATUS_ERROR, STATUS_NOT_FOUND
)
from core.logger import get_logger

log = get_logger("server")
MAX_SUGGESTIONS = 5

def server(input, output, session):
    active_modal = reactive.Value(None)
    workflow_result = reactive.Value(None)
    autocomplete_index = reactive.Value(svs.build_autocomplete_index(svs.load_models_index()))
    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})

    # تحميل أولي عند بدء التطبيق
    @reactive.effect
    def _():
        reload_system()

    def reload_system():
        refresh()
        autocomplete_index.set(svs.build_autocomplete_index(svs.load_models_index()))
        db = get_database()
        if db:
            p, s = svs.extract_panels_sensors(db)
            panels_cache.set(p)
            sensors_cache.set(s)

    def close_all():
        active_modal.set(None)

    def trigger_workflow(phone, plan2_data=None):
        phone = (phone or "").strip()
        if not phone: return None
        if len(phone) < 3:
            workflow_result.set(None)
            active_modal.set(None)
            return None
        
        db = get_database()
        if not db:
            log.error("Database is empty or unavailable")
            return None

        log.info(f"Triggering workflow for: {phone}")
        start_time = time.time()
        try:
            res = run_system_workflows(phone, db, plan2_input=plan2_data)
            log.info(f"Workflow result: {res}")
            workflow_result.set(res)
            status = res.get("status")
            active_modal.set(status if status in [STATUS_PLAN_2, STATUS_PLAN_3] else None)
        except Exception as e:
            log.exception(f"Workflow execution failed: {e}")
            workflow_result.set({"status": STATUS_ERROR, "message": "حدث خطأ في النظام"})
        log.info(f"Execution time: {time.time() - start_time:.4f}s")

    # الأحداث
    @reactive.effect
    @reactive.event(input.search_query)
    def _(): trigger_workflow(input.search_query())

    @reactive.effect
    @reactive.event(input.btn_add_to_group)
    def _():
        res = workflow_result()
        if res and res.get("status") == STATUS_PLAN2_SUCCESS:
            svs.add_phone_to_group(input.search_query(), res.get("size"), res.get("panel"), res.get("sensor"))
            reload_system()
            close_all()
            trigger_workflow(input.search_query())

    @reactive.effect
    @reactive.event(input.btn_create_group)
    def _():
        res = workflow_result()
        if res and res.get("input_data"):
            svs.create_new_group(input.search_query(), res["input_data"])
            reload_system()
            close_all()
            trigger_workflow(input.search_query())

    # عرض الواجهة
    @render.ui
    def dynamic_modal_container():
        m = active_modal()
        if not m: return None
        return draw_plan_2_modal(input.search_query(), panels_cache(), sensors_cache()) if m == STATUS_PLAN_2 else \
               draw_plan_3_modal(input.search_query(), panels_cache(), sensors_cache()) if m == STATUS_PLAN_3 else None

    @render.ui
    def results_workflow_view():
        res = workflow_result()
        if not res: return None
        s = res.get("status")
        try:
            if s == STATUS_SUCCESS:
                c, comp = res.get("coords", {}), res.get("compatibles", {})
                return ui.div(draw_technical_coords(c.get("size"), c.get("panel"), c.get("sensor"), c.get("real_name")),
                              draw_neon_section("مطابقة", comp.get("exact", []), "#2ecc71", "🟢", "exact"),
                              draw_neon_section("أكبر", comp.get("plus", []), "#3498db", "🔵", "plus"),
                              draw_neon_section("أصغر", comp.get("minus", []), "#e67e22", "🟠", "minus"))
            elif s == STATUS_PLAN2_SUCCESS:
                return ui.div(draw_neon_section("المجموعة المقترحة", res.get("models", []), "#9b59b6", "📋", "group"),
                              ui.input_action_button("btn_add_to_group", "➕ إضافة للمجموعة"))
            elif s == STATUS_PLAN_3:
                return ui.div(ui.h4("المواصفات المقترحة:"),
                              ui.p(f"المقاس: {res.get('suggested_size')} | اللوحة: {res.get('suggested_panel')} | الحساس: {res.get('suggested_sensor')}"),
                              ui.input_action_button("btn_create_group", "🏗️ إنشاء مجموعة"))
            elif s == STATUS_ERROR: return draw_warning_card(res.get("message", "خطأ في البحث"))
            elif s == STATUS_NOT_FOUND: return draw_warning_card("الموديل غير موجود في قاعدة البيانات")
            return None
        except Exception as e:
            log.exception(f"Render Error: {e}")
            return draw_warning_card("خطأ في عرض النتائج")

    @render.ui
    def suggestions_curtain():
        query = input.search_query()
        if not query or len(query) < 2: return None
        results = autocomplete_index().search_prefix(query, MAX_SUGGESTIONS)
        if not results: return None
        # إخفاء الستارة برمجياً
        onclick = "Shiny.setInputValue('search_query', val, {priority:'event'}); this.parentElement.style.display='none';"
        return ui.div(*[ui.div(r, class_="suggestion-row", onclick=f"var val={json.dumps(r)}; {onclick}") for r in results], class_="suggestions-curtain")

    # المكونات الثابتة
    @render.ui
    def database_status_area(): return draw_database_status(svs.count_models(get_database()))
    @render.ui
    def monitor_area(): return draw_monitor_component(get_status())
    @render.ui
    def notifications_area(): return draw_notifications(get_status())
