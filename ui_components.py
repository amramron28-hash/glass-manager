import os
import base64
from html import escape
from shiny import ui

def inject_pwa_and_styles():
    # ... (احتفظ بكود الستايل الخاص بك كما هو) ...
    return ui.HTML(f"""<style>
    /* ... [الستايلات السابقة] ... */
    .drawer { position:fixed; top:0; right:-310px; width:300px; height:100%; background:rgba(15,22,36,.98); backdrop-filter:blur(20px); border-left:1px solid rgba(0,191,255,.3); transition:.4s ease-in-out; z-index:200000; padding:30px; }
    .drawer.open { right:0 !important; }
    </style>""")

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.tags.head(
        ui.tags.script("""
        Shiny.addCustomMessageHandler('toggle_drawer', function(msg){
            let d = document.getElementById('settings_drawer');
            if(d) {
                if(msg === 'open') d.classList.add('open');
                else d.classList.remove('open');
            }
        });
        """)
    ),
    ui.div(
        ui.div(ui.div("ZEGAAR AMMAR", class_="brand-neon-main"), ui.div("GLASS MANAGER", class_="brand-neon-sub"), class_="brand-neon-title"),
        ui.input_action_button("btn_settings", "⋮", class_="btn-dots-menu"),
        class_="header-bar"
    ),
    ui.div(
        ui.input_action_button("btn_close_drawer_trigger", "×", class_="drawer-close-btn"),
        ui.h3("⚙️ الإعدادات العامة", style="color:#00bfff; text-align:center;"),
        ui.output_ui("database_status_area"),
        id="settings_drawer", class_="drawer"
    ),
    ui.div(ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."), ui.output_ui("suggestions_curtain"), class_="search-box"),
    ui.output_ui("results_workflow_view")
)
