import json
import time
from shiny import ui, render, reactive
import services as svs
# استيراد الدوال من ملفك الفعلي
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, 
    draw_database_status, draw_monitor_component, draw_notifications
)
from silent_monitor import get_database, refresh, get_status, get_statistics, get_cached_status
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
    
    # تحميل الفهرس (نستخدم الدالة الموثوقة من services)
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
        # استخراج البيانات مرة واحدة لتفادي الأخطاء
        panels, sensors = svs.index_service.extract_panels_sensors(db)
        
        if m == "plan_2": return draw_plan_2_modal(current_search_phone(), panels, sensors)
        if m == "plan_3": return draw_plan_3_modal(current_search_phone(), panels, sensors)
        return None

    # 4. الأحداث (Events)
    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def _(): active_modal.set("plan_2")

    @reactive.effect
    @reactive.event(input.trigger_plan_3)
    def _(): active_modal.set("plan_3")

    @reactive.effect
    @reactive.event(input.btn_cancel_add)
    def _(): active_modal.set(None)

    # 5. عرض البيانات (Renderers)
    @render.ui
    def results_workflow_view():
        return ui.HTML(run_system_workflows(current_search_phone(), get_database()))

    @render.ui
    def database_status_area():
        db = get_database()
        # الحساب الصحيح للمستويات الثلاثة: Size -> Panel -> Sensor
        total = sum(len(d.get("models", [])) for size in db.values() 
                    for p in size.values() if isinstance(p, dict) 
                    for d in p.values() if isinstance(d, dict))
        return draw_database_status(total)

    @render.ui
    def monitor_area():
        db_trigger() # للربط التفاعلي
        return draw_monitor_component(get_cached_status())

    @render.ui
    def notifications_area():
        return draw_notifications(get_cached_status())

    # 6. تحديث النظام بعد الإضافة
    def refresh_system_state():
        refresh()
        svs.cache_service.workflow_cache.invalidate()
        autocomplete_index.set(svs.search_service.build_autocomplete_index(svs.search_service.load_models_index()))
        db_trigger.set(db_trigger() + 1)
