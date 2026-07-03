import json
from shiny import ui, render, reactive
import services as svs
from silent_monitor import get_database
from logic_engine import run_system_workflows

def server(input, output, session):
    current_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    suggestions_list = reactive.Value([])
    autocomplete_index = reactive.Value(svs.build_autocomplete_index(svs.load_models_index()))

    # --- Drawer Events ---
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _(): session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    def _(): session.send_custom_message("toggle_drawer", "close")

    # --- Search Logic ---
    @reactive.effect
    def _():
        query = input.search_query()
        trie = autocomplete_index()
        if query and trie:
            results = trie.search_prefix(query, 10)
            suggestions_list.set(results)
            show_curtain.set(len(results) > 0)
        else:
            show_curtain.set(False)

    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list(): return None
        items = []
        for row in suggestions_list():
            # استخدام JS للضغط لضمان إرسال القيمة للسيرفر مباشرة
            items.append(ui.tags.div(row, class_="suggestion-row", 
                onclick=f"Shiny.setInputValue('search_query', '{row}'); Shiny.setInputValue('selected_model_trigger', '{row}', {{priority:'event'}});"))
        return ui.div(*items, class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def _():
        current_phone.set(input.selected_model_trigger())
        show_curtain.set(False) # إخفاء الستارة عند الاختيار

    # --- Output Logic ---
    @render.ui
    def results_workflow_view():
        phone = current_phone()
        if not phone or show_curtain(): return None
        # جلب البيانات مباشرة من السيرفس لضمان التحديث
        return ui.HTML(run_system_workflows(phone, get_database()))
