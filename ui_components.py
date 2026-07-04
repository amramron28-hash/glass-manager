import os
import base64
from html import escape
from shiny import ui

def inject_pwa_and_styles():
    return ui.HTML("""<style>
    html, body, .container-fluid { background-color:#0a0e17 !important; color:white !important; direction:rtl !important; font-family:"Segoe UI",sans-serif !important; }
    .header-bar { display:flex; justify-content:space-between; align-items:center; padding:15px 25px; background:rgba(13,17,23,.55); border-bottom:1px solid rgba(0,191,255,.25); }
    .brand-neon-main { color:#00bfff; font-size:28px; font-weight:900; }
    .brand-neon-sub { color:#87ceeb; font-size:16px; font-weight:700; }
    .search-box { position:relative; width:90%; max-width:500px; margin:30px auto; }
    input[type="text"] { width:100%; background:rgba(17,24,39,.90); color:white; border:1px solid #00bfff; border-radius:14px; padding:14px; }
    .suggestions-curtain { position:absolute; top:60px; right:0; left:0; background:rgba(22,27,34,.96); border:1px solid #00bfff; border-radius:12px; z-index:9999; }
    .suggestion-row { padding:12px; cursor:pointer; border-bottom:1px solid rgba(255,255,255,.08); }
    .drawer { position:fixed; top:0; right:-310px; width:300px; height:100%; background:rgba(15,22,36,.98); z-index:200000; transition:.4s; padding:30px; }
    .drawer.open { right:0 !important; }
    .btn-dots-menu { background:transparent; border:none; color:#00bfff; font-size:28px; cursor:pointer; }
    .drawer-close-btn { background:transparent; border:none; color:#ff5252; font-size:24px; cursor:pointer; }
    </style>""")

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.tags.head(ui.tags.script("""
        Shiny.addCustomMessageHandler('toggle_drawer', function(msg){
            let d = document.getElementById('settings_drawer');
            if(d) { if(msg === 'open') d.classList.add('open'); else d.classList.remove('open'); }
        });
    """)),
    ui.div(
        ui.div(ui.div("ZEGAAR AMMAR", class_="brand-neon-main"), ui.div("GLASS MANAGER", class_="brand-neon-sub")),
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
