from shiny import reactive, render, ui
from ui_components import (
    draw_welcome_section,
    draw_technical_coords,
    draw_neon_section,
    draw_system_info,
    draw_database_status,
    draw_monitor_component,
    draw_silent_inspector,
)

def server(input, output, session):

    workflow_state = reactive.value(None)

    # ==================================================
    # Settings Drawer
    # ==================================================

    @output
    @render.ui
    def system_info_area():
        return draw_system_info()

    @output
    @render.ui
    def database_status_area():
        return draw_database_status(0)

    @output
    @render.ui
    def monitor_area():
        return draw_monitor_component("ONLINE")

    @output
    @render.ui
    def silent_inspector_area():
        return draw_silent_inspector()

    # ==================================================
    # Welcome
    # ==================================================

    @output
    @render.ui
    def welcome_area():
        if workflow_state() is None:
            return draw_welcome_section()
        return None

    # ==================================================
    # Search Results
    # ==================================================

    @output
    @render.ui
    def results_workflow_view():

        res = workflow_state()

        if not res:
            return None

        coords = res.get("coords", {})
        compatibles = res.get("compatibles", {})

        return ui.TagList(

            draw_technical_coords(coords),

            draw_neon_section(
                "مطابقة تماماً",
                compatibles.get("exact", []),
                "exact"
            ),

            draw_neon_section(
                "إضافات",
                compatibles.get("plus", []),
                "plus"
            ),

            draw_neon_section(
                "نواقص",
                compatibles.get("minus", []),
                "minus"
            )

        )

    # ==================================================
    # Suggestions Curtain
    # ==================================================

    @output
    @render.ui
    def suggestions_curtain():
        return None

    # ==================================================
    # Modals
    # ==================================================

    @output
    @render.ui
    def dynamic_modal_container():
        return None
