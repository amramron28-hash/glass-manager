import json
import time
from shiny import ui, render, reactive
import services as svs
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, 
    draw_database_status, draw_monitor_component, draw_notifications
)
from silent_monitor import get_database, refresh, get_status, get_statistics
from logic_engine import run_system_workflows
from database import add_model
from core.logger import get_logger

log = get_logger("server")

def server(input, output, session):
    # 1. الحالة (States)
    current_search_phone = reactive.Value("")
    active_modal = reactive.Value(None)
    show_curtain = reactive.Value(False)
    suggestions_list = reactive.Value([])
    db_trigger = reactive.Value(0)
    
    # تحميل الفهرس
    autocomplete_index = reactive.Value(svs.search_service.build_autocomplete_index(svs.search_service.load_models_index()))

    # 2. البحث (Search & AutoComplete)
    @reactive.effect
    def _():
        query = input.search_query()
        if query and autocomplete_index():
            results = autocomplete_index().search_prefix(query, 10)
            suggestions_list.set(results)
            show_curtain.set(len(results) > 0)
        else:
            current_search_phone.set("")
            suggestions_list.set([])
            show_curtain.set(False)

    @render.ui
    def suggestions_curtain():
        if not show_curtain(): return None
        return ui.div(*[ui.div(row, class_="suggestion-row", 
            onclick=f"Shiny.setInputValue('selected_model_trigger', '{row}', {{priority:'event'}});") 
            for row in suggestions_list()], class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def _():
        val = input.selected_model_trigger()
        ui.update_text(session, "search_query", value=val)
        current_search_phone.set(val)
        show_curtain.set(False)

    # 3. النوافذ المنبثقة (Modals)
    @render.ui
    def dynamic_modal_container():
        m = active_modal()
        if not m: return None
        db = get_database()
        panels, sensors = svs.index_service.extract_panels_sensors(db)
        
        if m == "plan_2": return draw_plan_2_modal(current_search_phone(), panels, sensors)
        if m == "plan_3": return draw_plan_3_modal(current_search_phone(), panels, sensors)
        return None

    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def _(): active_modal.set("plan_2")

    @reactive.effect
    @reactive.event(input.trigger_plan_3)
    def _(): active_modal.set("plan_3")

    # 4. عرض النتائج والمراقبة
    @render.ui
    def results_workflow_view():
        return ui.HTML(run_system_workflows(current_search_phone(), get_database()))

    @render.ui
    def database_status_area():
        db = get_database()
        total = sum(len(d.get("models", [])) for size in db.values() 
                    for p in size.values() if isinstance(p, dict) 
                    for d in p.values() if isinstance(d, dict))
        return draw_database_status(total)

    @render.ui
    def monitor_area():
        db_trigger()
        return draw_monitor_component(get_status())

    @render.ui
    def notifications_area():
        return draw_notifications(get_status())

    # 5. التحكم في الـ Drawer
    @reactive.effect
    @reactive.event(input.btn_settings)
    async def _(): await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def _(): await session.send_custom_message("toggle_drawer", "close")

