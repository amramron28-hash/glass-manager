from shiny import ui

from ui_header import draw_header
from ui_search import draw_search_box
from ui_settings import draw_settings_drawer


app_ui = ui.page_fluid(

    # ==========================================================
    # HEAD
    # ==========================================================

    ui.tags.head(

        ui.tags.meta(charset="utf-8"),

        ui.tags.meta(
            name="viewport",
            content="width=device-width, initial-scale=1"
        ),

        ui.tags.meta(
            name="theme-color",
            content="#00bfff"
        ),

        ui.tags.meta(
            name="mobile-web-app-capable",
            content="yes"
        ),

        ui.tags.meta(
            name="apple-mobile-web-app-capable",
            content="yes"
        ),

        ui.tags.meta(
            name="apple-mobile-web-app-status-bar-style",
            content="black-translucent"
        ),

        ui.tags.meta(
            name="apple-mobile-web-app-title",
            content="ZEGAAR AMMAR"
        ),

        ui.tags.link(
            rel="manifest",
            href="/manifest.json"
        ),

        ui.tags.link(
            rel="icon",
            type="image/jpeg",
            href="/AMMAR.jpg"
        ),

        ui.tags.link(
            rel="shortcut icon",
            href="/AMMAR.jpg"
        ),

        ui.tags.link(
            rel="apple-touch-icon",
            href="/AMMAR.jpg"
        ),

        ui.tags.link(
            rel="stylesheet",
            href="/style_v2.css?v=7"
        ),

        ui.tags.script("""
if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker
            .register("/service-worker.js")
            .then(function(reg){
                console.log("Service Worker Registered", reg);
            })
            .catch(function(err){
                console.error("Service Worker Error:", err);
            });
    });
}
""")

    ),

    # ==========================================================
    # DRAWER EVENTS
    # ==========================================================

    ui.tags.script("""

document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener("click", function(e){

        if(e.target.id==="btn_settings"){

            document
                .getElementById("settings-drawer")
                ?.classList.add("drawer-open");

        }

        if(e.target.id==="btn_close_drawer_trigger"){

            document
                .getElementById("settings-drawer")
                ?.classList.remove("drawer-open");

        }

        const row = e.target.closest(".suggestion-row");

        if(row){

            const value = row.dataset.value;

            const input = document.getElementById("search_query");

            if(input && value){

                input.value = value;

                input.dispatchEvent(
                    new Event("input",{bubbles:true})
                );

            }

        }

    });

});

"""),

    # ==========================================================
    # BACKGROUND
    # ==========================================================

    ui.div(
        class_="fixed-background"
    ),

    # ==========================================================
    # SETTINGS
    # ==========================================================

    draw_settings_drawer(),

    # ==========================================================
    # MAIN
    # ==========================================================

    ui.div(

        draw_header(),

        draw_search_box(),

        ui.output_ui(
            "welcome_area"
        ),

        ui.div(

            ui.output_ui(
                "results_workflow_view"
            ),

            class_="results-workflow-view"

        ),

        ui.output_ui(
            "dynamic_modal_container"
        ),

        class_="main-layout"

    )

)
