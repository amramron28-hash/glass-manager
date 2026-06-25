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
html, body, .container-fluid {{ 
    background-color:#0a0e17 !important; 
    {bg_style} 
    background-size:92% auto !important; 
    background-position:center center !important; 
    background-repeat:no-repeat !important; 
    background-attachment:fixed !important; 
    color:white !important; 
    direction:rtl !important; 
}}
.header-bar {{ display:flex; justify-content:space-between; align-items:center; padding:10px 25px; background: rgba(13,17,23,.55); backdrop-filter:blur(12px); border-bottom: 1px solid rgba(0,191,255,.25); }}
.brand-neon-main {{ color: #00bfff; font-size: 26px; font-weight: 900; letter-spacing: 1px; text-shadow: 0 0 4px rgba(0,191,255,0.6); }}
.search-box {{ position:relative; width:90%; max-width:500px; margin:25px auto; }}
input[type="text"], input[type="number"], select {{ width:100% !important; background:#111827 !important; color:white !important; border:1px solid #00bfff !important; border-radius:12px !important; padding:12px !important; direction: ltr !important; text-align: left !important; }}

/* كلاسات البطاقات الزجاجية الملونة */
.glass-card-base {{ backdrop-filter:blur(15px); border: 1px solid rgba(255,255,255,0.2); border-radius:20px; padding:20px; margin:15px auto; max-width:500px; box-shadow: inset 0 0 15px rgba(255,255,255,0.1); }}
.card-green {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(76,175,80,0.4) 50%, rgba(46,125,50,0.6) 100%); }}
.card-blue  {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(33,150,243,0.4) 50%, rgba(21,101,192,0.6) 100%); }}
.card-red   {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(244,67,54,0.4) 50%, rgba(198,40,40,0.6) 100%); }}
.card-orange{{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,152,0,0.4) 50%, rgba(239,108,0,0.6) 100%); }}

.flat-phone-text {{ color:white; font-size:20px; font-weight:800; direction: ltr !important; text-align:left; }}
.custom-modal-backdrop {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.75); z-index: 999999; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(5px); }}
</style>""")

def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f"""<div class="glass-card-base card-blue" style="box-shadow: 0 0 15px rgba(0, 191, 255, 0.25);"><h3 style="color:#00bfff; text-align:center; margin-bottom:15px;">📱 {escape(str(model_name))}</h3><div style="font-size:16px; line-height:2; text-align:right; direction: rtl !important;">📏 <b>المقاس الفني:</b> <span style="color:#00bfff;">{escape(str(size_grp))}</span><br>📺 <b>نوع الشاشة:</b> <span style="color:#00bfff;">{escape(str(panel_grp))}</span><br>👁️ <b>المستشعر الحركي:</b> <span style="color:#00bfff;">{escape(str(sensor_grp))}</span></div></div>""")

def draw_neon_section(title=None, models_list=None, color_hex="#00bfff", badge_icon="📱", plan_type="exact"):
    if not models_list: return ui.div()
    class_map = {"exact": "card-green", "plus": "card-blue", "minus": "card-red"}
    card_class = class_map.get(plan_type, "card-blue")
    cards = [ui.h4(f"{badge_icon} {title}", style=f"color:{color_hex}; direction:rtl !important; text-align:right !important; margin:20px auto; max-width:500px;")]
    for model in models_list:
        cards.append(ui.HTML(f"""<div class="glass-card-base {card_class}" style="direction: ltr !important;"><div class="flat-phone-text">{escape(str(model))}</div></div>"""))
    return ui.div(*cards)

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    return ui.div(ui.div(ui.h3(f"📋 المواصفات لـ {phone_name}", style="color:#00bfff; text-align:center;"), ui.input_numeric("p2_size", "مقاس الشاشة:", value=6.5), ui.input_select("p2_panel", "نوع الشاشة:", choices={p:p for p in existing_panels if p}), ui.input_select("p2_sensor", "المستشعر:", choices={s:s for s in existing_sensors if s}), ui.input_action_button("p2_search", "فحص", class_="btn-success"), class_="glass-card-base card-blue", style="max-width:400px;"), class_="custom-modal-backdrop")
