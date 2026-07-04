import json
from shiny import ui, render, reactive
import services as svs
# استيراد كافة الدوال المطلوبة من ui_components
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, 
    build_add_panel_modal, build_add_sensor_modal,
    draw_database_status, draw_monitor_component, draw_notifications
)
from silent_monitor import get_database, refresh, get_status
from logic_engine import run_system_workflows
from core.logger import get_logger

log = get_logger("server")

def server(input, output, session):
    # 1. الحالة (States)
    current_search_phone = reactive.Value("")
    active_modal = reactive.Value(None)
    db_trigger = reactive.Value(0)
    
    # تحميل الفهرس
    autocomplete_index = reactive.Value(svs.search_service.build_autocomplete_index(svs.search_service.load_models_index()))

    # 2. النوافذ المنبثقة (Modals)
    @render.ui
    def dynamic_modal_container():
        m = active_modal()
        if not m: return None
        db = get_database()
        panels, sensors = svs.index_service.extract_panels_sensors(db)
        
        if m == "plan_2": return draw_plan_2_modal(current_search_phone(), panels, sensors)
        if m == "plan_3": return draw_plan_3_modal(current_search_phone(), panels, sensors)
        if m == "add_panel": return build_add_panel_modal()
        if m == "add_sensor": return build_add_sensor_modal()
        return None

    # 3. معالجات الأحداث (Event Handlers)
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

    # 4. المكونات الديناميكية (UI Components)
    @render.ui
    def results_workflow_view():
        return ui.HTML(run_system_workflows(current_search_phone(), get_database()))

    @render.ui
    def database_status_area():
        db = get_database()
        # حساب إجمالي الهواتف
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

    # 5. التحكم بالدرج (Drawer)
    @reactive.effect
    @reactive.event(input.btn_settings)
    async def _(): await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def _(): await session.send_custom_message("toggle_drawer", "close")
