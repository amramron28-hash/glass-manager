import json
from shiny import ui, render, reactive
import services as svs
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, build_add_panel_modal,
    build_add_sensor_modal, draw_database_status, draw_monitor_component, draw_notifications
)
from silent_monitor import get_database, refresh, get_status, get_statistics, get_cached_status
from logic_engine import run_system_workflows
from database import add_model # الدالة الفعلية للإضافة
from core.logger import get_logger

log = get_logger("server")

def server(input, output, session):
    # 1. الحالة (States)
    current_search_phone = reactive.Value("")
    active_modal = reactive.Value(None)
    show_curtain = reactive.Value(False)
    suggestions_list = reactive.Value([])
    db_trigger = reactive.Value(0) # للتحكم في إعادة بناء الفهارس

    # 2. البحث (Search & Indexing)
    autocomplete_index = reactive.Value(svs.build_autocomplete_index(svs.load_models_index()))

    @reactive.effect
    def _():
        query = input.search_query()
        if query and autocomplete_index():
            results = autocomplete_index().search_prefix(query, 10)
            suggestions_list.set(results)
            show_curtain.set(len(results) > 0)
        else:
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

    # 3. النتائج والخطط (Workflow & Plans)
    @render.ui
    def results_workflow_view():
        phone = current_search_phone()
        if not phone: return None
        return ui.HTML(run_system_workflows(phone, get_database()))

    @render.ui
    def dynamic_modal_container():
        m = active_modal()
        db = get_database()
        # التواقيع الصحيحة كما طلبت:
        if m == "plan_2": return draw_plan_2_modal(current_search_phone(), svs.extract_panels_sensors(db)[0], svs.extract_panels_sensors(db)[1])
        if m == "plan_3": return draw_plan_3_modal(current_search_phone(), svs.extract_panels_sensors(db)[0], svs.extract_panels_sensors(db)[1])
        if m == "add_panel": return build_add_panel_modal()
        if m == "add_sensor": return build_add_sensor_modal()
        return None

    # 4. إدارة الأحداث والعمليات (Events & Logic)
    @reactive.effect
    @reactive.event(input.show_add_panel)
    def _(): active_modal.set("add_panel")

    @reactive.effect
    @reactive.event(input.show_add_sensor)
    def _(): active_modal.set("add_sensor")

    @reactive.effect
    @reactive.event(input.btn_cancel_add)
    def _(): active_modal.set(None)

    @reactive.effect
    @reactive.event(input.btn_confirm_add_panel)
    def _():
        # تنفيذ الإضافة الفعلية
        # add_model(input.panel_name(), ...)
        refresh()
        svs.workflow_cache.invalidate() # إعادة بناء الكاش
        autocomplete_index.set(svs.build_autocomplete_index(svs.load_models_index())) # إعادة بناء الفهارس
        active_modal.set(None)
        db_trigger.set(db_trigger() + 1)

    # 5. المراقبة والإعدادات
    @render.ui
    def monitor_area():
        db_trigger()
        s = get_cached_status()
        return draw_monitor_component(s)

    @render.ui
    def notifications_area():
        return draw_notifications(get_cached_status())

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def _(): await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def _(): await session.send_custom_message("toggle_drawer", "close")
