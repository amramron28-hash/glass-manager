from shiny import ui

from ui_header import draw_header
from ui_search import draw_search_box
from ui_settings import draw_settings_drawer


app_ui = ui.page_fluid(

    ui.tags.head(
        ui.tags.meta(charset="utf-8"),
        ui.tags.meta(
            name="viewport",
            content="width=device-width, initial-scale=1",
        ),
        ui.tags.link(
            rel="stylesheet",
            href="style_v2.css?v=2",
        ),
    ),

    ui.tags.script("""
document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener("click", function(e){

        if(e.target.id==="btn_settings"){
            document.getElementById("settings-drawer")
                ?.classList.add("drawer-open");
        }

        if(e.target.id==="btn_close_drawer_trigger"){
            document.getElementById("settings-drawer")
                ?.classList.remove("drawer-open");
        }

    });

});
"""),

    ui.div(class_="fixed-background"),

    draw_settings_drawer(),

    ui.div(
        draw_header(),

        draw_search_box(),

        ui.output_ui("welcome_area"),

        ui.output_ui("suggestions_curtain"),

        ui.output_ui("results_workflow_view"),

        ui.output_ui("dynamic_modal_container"),

        class_="main-layout",
    ),
)
