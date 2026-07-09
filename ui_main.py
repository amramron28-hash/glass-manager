from shiny import ui
from ui_header import draw_header, draw_welcome_header
from ui_search import draw_search_box
from ui_settings import draw_settings_drawer

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.meta(charset="utf-8"),
        ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1"),
        # تم إضافة ?v=2 لإجبار المتصفح على تحميل النسخة الجديدة
        ui.tags.link(rel="stylesheet", href="style_v2.css?v=2"),
        ui.tags.script(src="https://code.jquery.com/jquery-3.7.1.min.js")
    ),

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
    draw_settings_drawer(),

    ui.div(
        draw_header(),          # الترس والشعار
        draw_search_box(),      # مربع البحث
        draw_welcome_header(),  # الصورة الثابتة فقط
        ui.output_ui("results_workflow_view"),
        ui.output_ui("dynamic_modal_container"),
        class_="main-layout"
    )
)
