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
    bg_style = f"background-image: linear-gradient(rgba(10,14,23,.20), rgba(10,14,23,.20)), url('data:image/webp;base64,{_bg_cache}');" if _bg_cache else "background-image: none;"
    return ui.HTML(f"""<style>
        html, body {{ background-color:#0a0e17 !important; {bg_style} color:white !important; direction:rtl !important; font-family: sans-serif; }}
        /* الهيدر والشعار */
        .header-bar {{ display:flex; justify-content:space-between; align-items:center; padding:15px; background:rgba(13,17,23,.8); backdrop-filter:blur(10px); border-bottom:1px solid #00bfff; }}
        .brand-neon-main {{ color: #00bfff; font-size: 22px; font-weight: 900; text-shadow: 0 0 10px #00bfff; }}
        /* البحث والستارة */
        .search-box {{ position:relative; width:90%; max-width:500px; margin:20px auto; }}
        .suggestions-curtain {{ position:absolute; top:60px; right:0; left:0; background:rgba(22,27,34,.95); border:1px solid #00bfff; border-radius:15px; max-height:300px; overflow-y:auto; z-index:999; backdrop-filter:blur(10px); }}
        /* البطاقات */
        .glass-card-base {{ backdrop-filter:blur(15px); border:1px solid rgba(255,255,255,.2); border-radius:20px; padding:20px; margin:15px auto; box-shadow:0 4px 15px rgba(0,0,0,.3); }}
        .metric-box {{ background:rgba(255,255,255,.05); padding:10px; border-radius:10px; text-align:center; border:1px solid #00bfff; margin:5px; }}
        .custom-modal-backdrop {{ position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,.85); z-index:999999; display:flex; justify-content:center; align-items:center; }}
    </style>""")

def draw_header(title="ZEGAAR AMMAR GLASS MANAGER"):
    return ui.div(ui.input_action_button("btn_settings", "⚙️", style="background:transparent; border:none; color:white; font-size:20px;"), 
                  ui.span(title, class_="brand-neon-main"), class_="header-bar")

def draw_suggestions_curtain(items):
    return ui.div(*[ui.div(item, style="padding:10px; border-bottom:1px solid #333;") for item in items], class_="suggestions-curtain")

def draw_dashboard_modal(notification_count, silent_mode, phone_count):
    return ui.div(ui.div(
        ui.h4("⚙️ لوحة التحكم", style="text-align:center; color:#00bfff;"),
        ui.div(ui.p(f"🔔 الإشعارات: {notification_count}", class_="metric-box"),
               ui.p(f"🔇 مراقب صامت: {'مفعل' if silent_mode else 'معطل'}", class_="metric-box"),
               ui.p(f"📱 إجمالي الهواتف: {phone_count}", class_="metric-box")),
        ui.input_action_button("close_modal", "إغلاق", style="width:100%; margin-top:10px;"),
        class_="glass-card-base", style="background:#161b22; width:300px;"), class_="custom-modal-backdrop")

def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f"""<div class="glass-card-base"><h3 style="color:#00bfff; text-align:center;">📱 {escape(str(model_name))}</h3><div style="text-align:right;">📏 المقاس: {escape(str(size_grp))}<br>📺 الشاشة: {escape(str(panel_grp))}<br>👁️ المستشعر: {escape(str(sensor_grp))}</div></div>""")

def draw_neon_section(title, models_list, plan_type="exact"):
    class_map = {"exact": "card-green", "plus": "card-blue", "minus": "card-red"}
    card_class = class_map.get(plan_type, "card-blue")
    cards = [ui.h4(f"📱 {title}", style="text-align:right; margin-top:20px;")]
    for model in models_list:
        cards.append(ui.div(model, class_=f"glass-card-base {card_class}"))
    return ui.div(*cards)

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    return ui.div(ui.div(ui.h3(f"📋 لـ {phone_name}"), ui.input_numeric("p2_size", "مقاس:", 6.5), ui.input_select("p2_panel", "شاشة:", choices={p:p for p in existing_panels}), ui.input_select("p2_sensor", "مستشعر:", choices={s:s for s in existing_sensors}), ui.input_action_button("p2_search", "فحص"), class_="glass-card-base", style="background:#161b22; width:300px;"), class_="custom-modal-backdrop")

def draw_plan_3_modal(phone_name, size, panel, sensor):
    return ui.div(ui.div(ui.h3("🚨 مجموعة جديدة"), ui.p(f"الهاتف: {phone_name}"), ui.input_action_button("p3_submit", "حفظ"), class_="glass-card-base", style="background:#161b22; width:300px;"), class_="custom-modal-backdrop")
