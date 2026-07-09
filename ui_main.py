from shiny import ui

from ui_header import draw_header
from ui_search import draw_search_box
from ui_settings import draw_settings_drawer


# ==========================================================
# HEAD
# ==========================================================

def inject_styles():

    return ui.tags.head(

        ui.tags.meta(
            charset="utf-8"
        ),

        ui.tags.meta(
            name="viewport",
            content="width=device-width, initial-scale=1"
        ),

        ui.tags.link(
            rel="stylesheet",
            href="style_v2.css"
        ),

        ui.tags.link(
            rel="manifest",
            href="manifest.json"
        ),

        ui.tags.script(
            src="https://code.jquery.com/jquery-3.7.1.min.js"
        ),

        ui.tags.script(
            src="service-worker.js"
        ),

        ui.HTML("""

<script>

if("serviceWorker" in navigator){

window.addEventListener("load",()=>{

navigator.serviceWorker.register("/service-worker.js")
.catch(console.error);

});

}

</script>

""")

    )


# ==========================================================
# EVENTS
# ==========================================================

def draw_ui_scripts():

    return ui.HTML("""

<script>

$(document).ready(function(){


$(document).on(
"click",
"#btn_settings",
function(){

$("#settings-drawer")
.addClass("drawer-open");

});


$(document).on(
"click",
"#btn_close_drawer_trigger",
function(){

$("#settings-drawer")
.removeClass("drawer-open");

});


$(document).on(
"click",
".suggestion-row",
function(){

let value=$(this).text();

Shiny.setInputValue(
"search_query",
value,
{priority:"event"}
);

});


});

</script>

""")


# ==========================================================
# MAIN UI
# ==========================================================

app_ui = ui.page_fluid(

    inject_styles(),

    draw_ui_scripts(),

    ui.div(
        class_="fixed-background"
    ),


    draw_settings_drawer(),


    ui.div(

        draw_header(),


        draw_search_box(),


        ui.output_ui(
            "welcome_area"
        ),


        ui.output_ui(
            "results_workflow_view"
        ),


        ui.output_ui(
            "dynamic_modal_container"
        ),


        class_="main-layout"

    )

)
