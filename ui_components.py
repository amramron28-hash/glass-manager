# ui_components.py - تم تنظيف الاستيرادات الدائرية

import os
import base64
from html import escape
from shiny import ui

_bg_cache = None

def inject_pwa_and_styles():
    global _bg_cache
    if _bg_cache is None:
        for p in ["phone_image.webp", "./phone_image.webp", "/app/phone_image.webp"]:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    _bg_cache = base64.b64encode(f.read()).decode()
                break
    
    bg_style = f"background-image:linear-gradient(rgba(10,14,23,.20),rgba(10,14,23,.20)),url('data:image/webp;base64,{_bg_cache}');" if _bg_cache else "background-image:none;"
    
    return ui.HTML(f"""<style>
    html, body, .container-fluid {{ background-color:#0a0e17 !important; {bg_style} background-size:92% auto !important; background-position:center center !important; background-repeat:no-repeat !important; background-attachment:fixed !important; color:white !important; direction:rtl !important; font-family:"Segoe UI",sans-serif !important; }}
    .header-bar {{ display:flex; justify-content:space-between; align-items:center; padding:15px 25px; background:rgba(13,17,23,.55); backdrop-filter:blur(12px); border-bottom:1px solid rgba(0,191,255,.25); width:100%; }}
    .brand-neon-title {{ display:flex; flex-direction:column; gap:4px; text-align:right; flex-grow:1; }}
    .brand-neon-main {{ color:#00bfff; font-size:28px; font-weight:900; letter-spacing:0.5px; }}
    .brand-neon-sub {{ color:#87ceeb; font-size:16px; font-weight:700; opacity:0.9; }}
    .search-box {{ position:relative; width:90%; max-width:500px; margin:30px auto; }}
    input[type="text"], input[type="number"], select {{ width:100% !important; background:rgba(17,24,39,.90) !important; color:white !important; border:1px solid #00bfff !important; border-radius:14px !important; padding:14px !important; direction:ltr !important; text-align:left !important; }}
    .suggestions-curtain {{ position:absolute; top:60px; right:0; left:0; background:rgba(22,27,34,.96); border:1px solid #00bfff; border-radius:12px; max-height:240px; overflow-y:auto; z-index:99999; }}
    .suggestion-row {{ padding:12px; color:white; cursor:pointer; border-bottom:1px solid rgba(255,255,255,.08); direction:ltr; text-align:left; }}
    .suggestion-row:hover {{ background:rgba(0,191,255,.18); }}
    .glass-card {{ background:rgba(255,255,255,.06); backdrop-filter:blur(15px); border:1px solid rgba(0,191,255,.35); border-radius:20px; padding:20px; margin:20px auto; max-width:500px; }}
    .ammar-flat-card {{ padding:16px 24px; margin-bottom:14px; border-radius:24px; width:100%; }}
    .flat-exact {{ background:linear-gradient(135deg, rgba(76,187,85,.45), rgba(34,111,41,.60)); }}
    .flat-plus {{ background:linear-gradient(135deg, rgba(41,98,255,.50), rgba(13,50,163,.60)); }}
    .flat-minus {{ background:linear-gradient(135deg, rgba(255,165,0,.45), rgba(230,126,34,.60)); }}
    .flat-warning-card {{ background:rgba(255,82,82,.45); border-radius:12px; padding:18px; color:white; font-weight:bold; text-align:center; }}
    .flat-phone-text {{ color:white; font-size:20px; font-weight:800; direction:ltr; text-align:left; }}
    .drawer {{ position:fixed; top:0; right:-310px; width:300px; height:100%; background:rgba(15,22,36,.98); backdrop-filter:blur(20px); border-left:1px solid rgba(0,191,255,.3); transition:.4s ease-in-out; z-index:200000; padding:30px; box-shadow:-5px 0 25px rgba(0,0,0,0.5); }}
    .drawer.open {{ right:0 !important; }}
    .drawer-close-btn {{ background:transparent; border:none; color:#ff5252; font-size:24px; cursor:pointer; float:left; font-weight:bold; }}
    .metric-box {{ background:rgba(255,255,255,.05); padding:14px; border-radius:12px; margin-bottom:15px; text-align:center; border:1px solid rgba(0,191,255,0.15); font-weight:bold; }}
    .custom-modal-backdrop {{ position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,.75); z-index:999999; display:flex; justify-content:center; align-items:center; }}
    .btn-dots-menu {{ background:transparent !important; border:none !important; color:#00bfff !important; font-size:28px !important; font-weight:bold !important; cursor:pointer; padding:0 10px !important; line-height:1 !important; transition:color 0.3s ease; }}
    .btn-dots-menu:hover {{ color:#87ceeb !important; }}
    .input-with-add {{ display:flex; gap:8px; align-items:center; margin-bottom:14px; }}
    .input-with-add select, .input-with-add input {{ flex:1; margin-bottom:0 !important; }}
    .btn-add-option {{ background:#00bfff; color:white; border:none; border-radius:14px; width:48px; height:48px; font-size:24px; cursor:pointer; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
    </style>""")

def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f"""<div class="glass-card">
        <h3 style="color:#00bfff; text-align:center;">📱 {escape(str(model_name))}</h3>
        <div style="font-size:16px; line-height:2; text-align:right; direction:rtl;">
            📏 <b>المقاس الفني:</b> <span style="color:#00bfff">{escape(str(size_grp))}</span><br>
            📺 <b>نوع الشاشة:</b> <span style="color:#00bfff">{escape(str(panel_grp))}</span><br>
            👁️ <b>المستشعر:</b> <span style="color:#00bfff">{escape(str(sensor_grp))}</span>
        </div>
    </div>""")

def draw_neon_section(title, models_list, color_hex="#00bfff", badge_icon="📱", plan_type="exact"):
    if not models_list: return ui.div()
    class_map = {"exact": "flat-exact", "plus": "flat-plus", "minus": "flat-minus"}
    card_class = class_map.get(plan_type, "flat-exact")
    cards = [ui.h4(f"{badge_icon} {title}", style=f"color:{color_hex}; text-align:right; direction:rtl;")]
    for model in models_list:
        cards.append(ui.HTML(f'<div class="ammar-flat-card {card_class}"><div class="flat-phone-text">{escape(str(model))}</div></div>'))
    return ui.div(*cards)

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    panel_options = {p: p for p in existing_panels if p} or {"__empty__": "لا توجد خيارات"}
    sensor_options = {s: s for s in existing_sensors if s} or {"__empty__": "لا توجد خيارات"}

    return ui.div(ui.div(ui.div(
        ui.h3(f"📋 المواصفات الفنية لـ {str(phone_name)}", style="color:#3498db; text-align:center;"),
        ui.input_numeric("p2_size", "📏 مقاس الشاشة:", value=None, step=0.01),
        ui.div(
            ui.input_select("p2_panel", "📺 نوع الشاشة:", choices=panel_options),
            ui.tags.button("+", id="btn_add_panel_p2", class_="btn-add-option", onclick="Shiny.setInputValue('show_add_panel', true, {priority:'event'});"),
            class_="input-with-add"
        ),
        ui.div(
            ui.input_select("p2_sensor", "👁️ نوع المستشعر:", choices=sensor_options),
            ui.tags.button("+", id="btn_add_sensor_p2", class_="btn-add-option", onclick="Shiny.setInputValue('show_add_sensor', true, {priority:'event'});"),
            class_="input-with-add"
        ),
        ui.input_action_button("p2_search", "🔍 فحص المطابقة", style="width:100%; background:#2ecc71; color:white; padding:12px; border-radius:8px; border:none;"),
        class_="glass-card", style="width:90%; max-width:500px; background:rgba(22,27,34,.98);"
    ), class_="custom-modal-backdrop"))

def draw_plan_3_modal(phone_name, existing_panels, existing_sensors):
    panel_options = {p: p for p in existing_panels if p} or {"__empty__": "لا توجد خيارات"}
    sensor_options = {s: s for s in existing_sensors if s} or {"__empty__": "لا توجد خيارات"}

    return ui.div(ui.div(ui.div(
        ui.h3(f"🔮 خطة الطوارئ لـ {str(phone_name)}", style="color:#e67e22; text-align:center;"),
        ui.input_numeric("p3_size", "📏 المقاس المقترح:", value=None, step=0.01),
        ui.div(
            ui.input_select("p3_panel", "📺 تخصيص نوع الشاشة:", choices=panel_options),
            ui.tags.button("+", id="btn_add_panel_p3", class_="btn-add-option", onclick="Shiny.setInputValue('show_add_panel', true, {priority:'event'});"),
            class_="input-with-add"
        ),
        ui.div(
            ui.input_select("p3_sensor", "👁️ تخصيص المستشعر:", choices=sensor_options),
            ui.tags.button("+", id="btn_add_sensor_p3", class_="btn-add-option", onclick="Shiny.setInputValue('show_add_sensor', true, {priority:'event'});"),
            class_="input-with-add"
        ),
        ui.input_action_button("p3_search", "⚡ تشغيل البحث الذكي", style="width:100%; background:#e67e22; color:white; padding:12px; border-radius:8px; border:none;"),
        class_="glass-card", style="width:90%; max-width:500px; background:rgba(22,27,34,.98);"
    ), class_="custom-modal-backdrop"))

def draw_warning_card(message):
    return ui.HTML(f'<div class="flat-warning-card">⚠️ {escape(str(message))}</div>')

def draw_database_status(total):
    return ui.div(ui.div(f"📊 قاعدة البيانات: {total} هاتف", class_="metric-box"))

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.tags.head(
        ui.tags.link(rel="manifest", href="manifest.json"),
        ui.tags.script("""
        if ('serviceWorker' in navigator) { window.addEventListener('load', function(){ navigator.serviceWorker.register('/service-worker.js'); }); }
        Shiny.addCustomMessageHandler('toggle_drawer', function(msg){
            let d = document.getElementById('settings_drawer');
            if(d){ if(msg === 'open') d.classList.add('open'); else d.classList.remove('open'); }
        });
        """)
    ),
    ui.div(
        ui.div(ui.div("ZEGAAR AMMAR", class_="brand-neon-main"), ui.div("GLASS MANAGER", class_="brand-neon-sub"), class_="brand-neon-title"),
        ui.input_action_button("btn_settings", "⋮", class_="btn-dots-menu"),
        class_="header-bar"
    ),
    ui.div(
        ui.tags.button("×", id="btn_close_drawer", class_="drawer-close-btn", onclick="Shiny.setInputValue('btn_close_drawer_trigger', Math.random(), {priority:'event'});"),
        ui.h3("⚙️ الإعدادات العامة", style="color:#00bfff; text-align:center; margin-bottom:25px; font-weight:800;"),
        ui.output_ui("database_status_area"),
        ui.output_ui("notifications_area"),
        ui.output_ui("monitor_area"),
        id="settings_drawer", class_="drawer"
    ),
    ui.div(ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."), ui.output_ui("suggestions_curtain"), class_="search-box"),
    ui.output_ui("results_workflow_view"),
    ui.output_ui("dynamic_modal_container")
)
