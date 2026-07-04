hereimport json
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
    STATUS_PLAN2_SUCCESS, STATUS_ERROR
)
from core.logger import get_logger

log = get_logger("server")
MAX_SUGGESTIONS = 5

def server(input, output, session):
    current_search_phone = reactive.Value("")
    last_phone = reactive.Value("")
    active_modal = reactive.Value(None)
    workflow_result = reactive.Value(None)
    autocomplete_index = reactive.Value(svs.build_autocomplete_index(svs.load_models_index()))
    # تخزين مؤقت للمواصفات
    panels_cache = reactive.Value({})
    sensors_cache = reactive.Value({})

    @reactive.effect
    def _(): current_search_phone.set(input.search_query())

    def reload_system():
        refresh()
        autocomplete_index.set(svs.build_autocomplete_index(svs.load_models_index()))
        p, s = svs.extract_panels_sensors(get_database())
        panels_cache.set(p)
        sensors_cache.set(s)

    def close_all():
        active_modal.set(None)
        workflow_result.set(None)
        last_phone.set("")

    # النقطة الوحيدة التي تستدعي logic_engine
    def trigger_workflow(phone, plan2_data=None):
        phone = phone.strip()
        if not phone or len(phone) < 3 or (not plan2_data and phone == last_phone()):
            return None
        
        last_phone.set(phone)
        log.info(f"Workflow triggered for: {phone}")
        try:
            res = run_system_workflows(phone, get_database(), plan2_input=plan2_data)
            workflow_result.set(res)
            
            status = res.get("status")
            if status in [STATUS_PLAN_2, STATUS_PLAN_3]:
                active_modal.set(status)
            else:
                active_modal.set(None)
            return res
        except Exception as e:
            log.exception(f"Workflow failed for {phone}")
            err = {"status": STATUS_ERROR, "message": "حدث خطأ غير متوقع"}
            workflow_result.set(err)
            return err

    # الأحداث
    @reactive.effect
    @reactive.event(input.search_query)
    def _(): trigger_workflow(current_search_phone())

    @reactive.effect
    @reactive.event(input.btn_confirm_plan2)
    def _():
        data = {"size": input.size(), "panel": input.panel(), "sensor": input.sensor()}
        trigger_workflow(current_search_phone(), plan2_data=data)

    @reactive.effect
    @reactive.event(input.btn_add_to_group)
    def _():
        res = workflow_result()
        if res and res.get("status") == STATUS_PLAN2_SUCCESS and all(k in res for k in ["size", "panel", "sensor"]):
            svs.add_phone_to_group(current_search_phone(), res["size"], res["panel"], res["sensor"])
            log.info(f"Added phone to group: {res['group_id']}")
            reload_system()
            current_search_phone.set("")
            close_all()

    @reactive.effect
    @reactive.event(input.btn_create_group)
    def _():
        res = workflow_result()
        if res and res.get("input_data"):
            svs.create_new_group(current_search_phone(), res["input_data"])
            log.info(f"Created new group: {res.get('group_name_suggestion')}")
            reload_system()
            current_search_phone.set("")
            close_all()

    @render.ui
    def results_workflow_view():
        res = workflow_result()
        if not res: return None
        s = res.get("status")
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
            return ui.div(ui.h4("المجموعة المقترحة للإنشاء:"),
                          ui.p(f"المقاس: {res.get('suggested_size')} | اللوحة: {res.get('suggested_panel')} | الحساس: {res.get('suggested_sensor')}"),
                          ui.input_action_button("btn_create_group", "🏗️ إنشاء مجموعة"))
        return None

    @render.ui
    def suggestions_curtain():
        query = current_search_phone()
        if not query or len(query) < 2: return None
        results = autocomplete_index().search_prefix(query, MAX_SUGGESTIONS)
        def make_onclick(val):
            return f"Shiny.setInputValue('search_query', {json.dumps(val)}, {{priority:'event'}});"
        return ui.div(*[ui.div(r, class_="suggestion-row", onclick=make_onclick(r)) for r in results], class_="suggestions-curtain")
