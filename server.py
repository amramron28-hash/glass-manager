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

    @reactive.effect
    @reactive.event(input.btn_settings)
    def _(): session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    def _(): session.send_custom_message("toggle_drawer", "close")

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
        items = []
        for row in suggestions_list():
            items.append(ui.tags.div(row, class_="suggestion-row", 
                onclick=f"Shiny.setInputValue('selected_model_trigger', '{row}', {{priority:'event'}});"))
        return ui.div(*items, class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def _():
        current_phone.set(input.selected_model_trigger())
        show_curtain.set(False)

    @render.ui
    def results_workflow_view():
        phone = current_phone()
        if not phone or show_curtain(): return None
        return ui.HTML(run_system_workflows(phone, get_database()))
