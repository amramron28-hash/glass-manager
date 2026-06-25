import os
import base64
from html import escape
from shiny import ui

def inject_pwa_and_styles():
    return ui.HTML("""
    <style>
        /* إجبار الخلفية وتنسيق شريط البحث */
        body { background-color: #0a0e17 !important; color: white !important; direction: rtl !important; }
        .search-box input { background: #161b22 !important; border: 1px solid #00bfff !important; color: white !important; }
        
        /* الشعار والنيون */
        .brand-neon { color: #00bfff; font-size: 26px; font-weight: 900; text-align: center; margin: 20px 0; text-shadow: 0 0 10px #00bfff; }
        .suggestions-curtain { background: #161b22; border: 1px solid #00bfff; border-radius: 0 0 15px 15px; z-index: 1000; }
        .glass-card { background: rgba(255,255,255,0.05); border: 1px solid #00bfff; border-radius: 15px; padding: 15px; margin: 10px; }
        
        /* الدرج */
        .drawer { position: fixed; top: 0; right: -300px; width: 280px; height: 100%; background: #0d1117; border-left: 2px solid #00bfff; transition: 0.3s; z-index: 2000; padding: 20px; }
        .drawer.open { right: 0; }
    </style>
    """)

def draw_header():
    return ui.div("ZEGAAR AMMAR GLASS MANAGER", class_="brand-neon")

# إصلاح الدالة لتستقبل 5 وسائط كما يحاول app.py تمريرها
def draw_neon_section(title=None, models_list=None, color_hex="#00bfff", badge_icon="📱", plan_type="exact"):
    if models_list is None: models_list = []
    class_map = {"exact": "card-green", "plus": "card-blue", "minus": "card-red"}
    card_class = class_map.get(plan_type, "card-blue")
    cards = [ui.h4(f"{badge_icon} {title}", style=f"color:{color_hex}; text-align:right;")]
    for model in models_list:
        cards.append(ui.div(model, class_=f"glass-card {card_class}"))
    return ui.div(*cards)

def draw_sidebar_drawer(notification_count, silent_mode, phone_count):
    return ui.div(
        ui.h3("إعدادات", style="color:#00bfff"),
        ui.div(f"🔔 الإشعارات: {notification_count}", class_="glass-card"),
        ui.div(f"🔇 صامت: {'مفعل' if silent_mode else 'معطل'}", class_="glass-card"),
        ui.div(f"📱 الهواتف: {phone_count}", class_="glass-card"),
        class_="drawer", id="settings_drawer"
    )

def draw_suggestions_curtain(items):
    return ui.div(*[ui.div(item, style="padding:10px; border-bottom:1px solid #333;") for item in items], class_="suggestions-curtain")

# بقية الدوال المساعدة (Technical_coords, Modal)
def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f'<div class="glass-card"><h3>📱 {escape(model_name)}</h3><div>📏 {size_grp}<br>📺 {panel_grp}<br>👁️ {sensor_grp}</div></div>')

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    return ui.div(ui.div(ui.h3(f"📋 {phone_name}"), ui.input_action_button("p2_search", "فحص"), class_="glass-card", style="background:#161b22;"), class_="custom-modal-backdrop")

def draw_plan_3_modal(phone_name, size, panel, sensor):
    return ui.div(ui.div(ui.h3("🚨 جديد"), ui.input_action_button("p3_submit", "حفظ"), class_="glass-card", style="background:#161b22;"), class_="custom-modal-backdrop")
