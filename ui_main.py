from shiny import ui
from ui_header import draw_header
from ui_search import draw_search_box
from ui_settings import draw_settings_drawer

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.meta(charset="utf-8"),
        ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1"),
        ui.tags.link(rel="stylesheet", href="style_v2.css"),
        ui.tags.script(src="https://code.jquery.com/jquery-3.7.1.min.js"),
        ui.tags.script(src="service-worker.js")
    ),

    # سكربت التفاعل (الفتح والإغلاق)
    ui.tags.script("""
        $(document).ready(function(){
            $(document).on("click", "#btn_settings", function(){
                $("#settings-drawer").addClass("drawer-open");
            });
            $(document).on("click", "#btn_close_drawer_trigger", function(){
                $("#settings-drawer").removeClass("drawer-open");
            });
        });
    """),

    ui.div(class_="fixed-background"),
    
    # القائمة الجانبية (ثابتة)
    draw_settings_drawer(),

    ui.div(
        draw_header(),
        draw_search_box(),
        ui.output_ui("welcome_area"),
        ui.output_ui("results_workflow_view"),
        ui.output_ui("dynamic_modal_container"),
        class_="main-layout"
    )
)
