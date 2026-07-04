import json
from shiny import render, reactive, ui
import services as svs
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, 
    build_add_panel_modal, build_add_sensor_modal,
    draw_database_status, draw_monitor_component, draw_notifications
)
from silent_monitor import get_database, get_status
from logic_engine import run_system_workflows
from core.logger import get_logger

log = get_logger("server")
MAX_SUGGESTIONS = 5

# تحميل الفهرس مرة واحدة (Shared Index)
_shared_autocomplete_index = svs.build_autocomplete_index(svs.load_models_index())

def server(input, output, session):
    current_search_phone = reactive.Value("")
    active_modal = reactive.Value(None)
    db_trigger = reactive.Value(0)

    @reactive.effect
    def _():
        current_search_phone.set(input.search_query())

    @render.ui
    def suggestions_curtain():
        query = input.search_query()
        if not query: return None
        
        results = _shared_autocomplete_index.search_prefix(query, MAX_SUGGESTIONS)
        if not results: return None
        
        # استخدام JSON dumps لتفادي مشاكل الاقتباس
        def make_onclick(val):
            val_json = json.dumps(val)
            return f"document.getElementById('search_query').value={val_json}; Shiny.setInputValue('search_query', {val_json}, {{priority:'event'}});"
        
        return ui.div(*[ui.div(r, class_="suggestion-row", onclick=make_onclick(r)) 
                       for r in results], class_="suggestions-curtain")

    @render.ui
    def dynamic_modal_container():
        m = active_modal()
        if not m: return None
        try:
            db = get_database()
            panels, sensors = svs.extract_panels_sensors(db)
            if m == "plan_2": return draw_plan_2_modal(current_search_phone(), panels, sensors)
            if m == "plan_3": return draw_plan_3_modal(current_search_phone(), panels, sensors)
            if m == "add_panel": return build_add_panel_modal()
            if m == "add_sensor": return build_add_sensor_modal()
        except Exception as e:
            log.error(f"Error loading modal: {e}")
            return None
        return None

    # إدارة الأحداث
    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def _(): active_modal.set("plan_2")

    @reactive.effect
    @reactive.event(input.trigger_plan_3)
    def _(): active_modal.set("plan_3")

    @reactive.effect
    @reactive.event(input.show_add_panel)
    def _(): active_modal.set("add_panel")

    @reactive.effect
    @reactive.event(input.show_add_sensor)
    def _(): active_modal.set("add_sensor")

    @reactive.effect
    @reactive.event(input.btn_cancel_add)
    def _(): active_modal.set(None)

    @render.ui
    def results_workflow_view():
        try:
            return ui.HTML(run_system_workflows(current_search_phone(), get_database()))
        except Exception as e:
            log.error(f"Workflow error: {e}")
            return ui.p("حدث خطأ في عرض النتائج.")

    @render.ui
    def database_status_area():
        db = get_database()
        total = sum(len(d.get("models", [])) for size in db.values() 
                    if isinstance(size, dict) for p in size.values() 
                    if isinstance(p, dict) for d in p.values() if isinstance(d, dict))
        return draw_database_status(total)

    @render.ui
    def monitor_area():
        db_trigger()
        return draw_monitor_component(get_status())

    @render.ui
    def notifications_area():
        return draw_notifications(get_status())

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def _(): await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def _(): await session.send_custom_message("toggle_drawer", "close")
