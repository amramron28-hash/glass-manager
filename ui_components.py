import os
import base64
from html import escape
from shiny import ui

# ... (دالة inject_pwa_and_styles تبقى كما هي دون تغيير) ...

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.tags.head(
        ui.tags.script("""
        Shiny.addCustomMessageHandler('toggle_drawer', function(msg){
            let d = document.getElementById('settings_drawer');
            if(d){ 
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
    # النافذة الجانبية (Drawer)
    ui.div(
        ui.input_action_button("btn_close_drawer_trigger", "×", class_="drawer-close-btn"),
        ui.h3("⚙️ الإعدادات العامة", style="color:#00bfff; text-align:center;"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        id="settings_drawer", class_="drawer"
    ),
    ui.div(ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."), ui.output_ui("suggestions_curtain"), class_="search-box"),
    ui.output_ui("results_workflow_view"),
    ui.output_ui("dynamic_modal_container")
)
