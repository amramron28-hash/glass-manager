import os, base64
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

    if _bg_cache:
        bg_style = f"background-image: linear-gradient(rgba(10,14,23,.20), rgba(10,14,23,.20)), url('data:image/webp;base64,{_bg_cache}');"
    else:
        bg_style = "background-image: none;"

    return ui.HTML(f"""<style>
/* =========================================
   ZEGAAR AMMAR GLASS MANAGER UI
========================================= */
html, body, .container-fluid {{ 
    background-color:#0a0e17 !important; 
    {bg_style} 
    background-size:92% auto !important; 
    background-position:center center !important; 
    background-repeat:no-repeat !important; 
    background-attachment:fixed !important; 
    color:white !important; 
    direction:rtl !important; 
    font-family:"Segoe UI", sans-serif !important;
}}

/* =========================================
   HEADER & BRAND LOGO ONE LINE
========================================= */
.header-bar {{ 
    display:flex; 
    justify-content:space-between; 
    align-items:center; 
    padding:12px 25px; 
    background: rgba(13,17,23,.55); 
    backdrop-filter:blur(12px); 
    -webkit-backdrop-filter:blur(12px);
    border-bottom: 1px solid rgba(0,191,255,.25); 
}}

.brand-neon-title {{
    text-align: right;
    white-space: nowrap;
}}
.brand-neon-main {{
    color: #00bfff;
    font-size: 28px;
    font-weight: 900;
    text-shadow: 0 0 5px rgba(0,191,255,.7), 0 0 15px rgba(0,191,255,.5);
    display: inline-block;
}}
.brand-neon-sub {{
    color: #87ceeb;
    font-size: 24px;
    font-weight: 700;
    margin-right: 8px;
    text-shadow: 0 0 5px rgba(135,206,235,.6);
    display: inline-block;
}}

/* =========================================
   SEARCH & INPUTS
========================================= */
.search-box {{ 
    position:relative; 
    width:90%; 
    max-width:500px; 
    margin:30px auto; 
}}

input[type="text"], input[type="number"], select {{ 
    width:100% !important; 
    background: rgba(17,24,39,.90) !important; 
    color:white !important; 
    border:1px solid #00bfff !important; 
    border-radius:14px !important; 
    padding:14px !important; 
    box-shadow: 0 0 15px rgba(0,191,255,.15) !important;
    direction: ltr !important; 
    text-align: left !important;
    outline: none;
}}

/* =========================================
   AUTOCOMPLETE
========================================= */
.suggestions-curtain {{ 
    position:absolute; 
    top:60px; 
    right:0; 
    left:0; 
    background: rgba(22,27,34,.96); 
    border: 1px solid #00bfff; 
    border-radius:12px; 
    max-height:240px; 
    overflow-y:auto; 
    z-index:99999; 
    backdrop-filter:blur(15px); 
    -webkit-backdrop-filter:blur(15px);
    box-shadow: 0 8px 30px rgba(0,0,0,.6);
}}

.suggestions-curtain::-webkit-scrollbar {{
    width: 6px;
}}
.suggestions-curtain::-webkit-scrollbar-track {{
    background: rgba(22,27,34,.96);
}}
.suggestions-curtain::-webkit-scrollbar-thumb {{
    background: #00bfff;
    border-radius: 10px;
}}

.suggestion-row {{ 
    padding:12px; 
    color:white; 
    cursor:pointer; 
    border-bottom: 1px solid rgba(255,255,255,.08); 
    text-align:left; 
    direction: ltr !important; 
    transition: background 0.2s ease-in-out;
}}
.suggestion-row:hover {{ background: rgba(0,191,255,.18); }}

/* =========================================
   GLASS CARD
========================================= */
.glass-card {{ 
    background: rgba(255,255,255,.06); 
    backdrop-filter:blur(15px); 
    -webkit-backdrop-filter:blur(15px);
    border: 1px solid rgba(0,191,255,.35); 
    border-radius:20px; 
    padding:20px; 
    margin:20px auto; 
    max-width:500px; 
}}
/* =========================================
   RESULT CARDS (AMMAR FLAT CARDS)
========================================= */
.ammar-flat-card {{ 
    display:flex !important; 
    justify-content: flex-end !important; 
    align-items:center !important; 
    padding:16px 24px; 
    margin-bottom:14px; 
    border-radius:24px; 
    width:100%; 
    box-sizing:border-box; 
    position: relative;
    overflow: hidden;
}}

.flat-exact {{ 
    background: linear-gradient(135deg, rgba(255,255,255,.30) 0%, rgba(76,187,85,.45) 50%, rgba(34,111,41,.60) 100%); 
    border: 1px solid rgba(255,255,255,.4); 
    box-shadow: inset 0 0 15px rgba(255,255,255,.5), 0 8px 32px rgba(0,0,0,.1); 
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}}

.flat-plus {{ 
    background: linear-gradient(135deg, rgba(255,255,255,.30) 0%, rgba(41,98,255,.50) 50%, rgba(13,50,163,.60) 100%); 
    border: 1px solid rgba(255,255,255,.4); 
    box-shadow: inset 0 0 15px rgba(255,255,255,.5), 0 8px 32px rgba(0,0,0,.1); 
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}}

.flat-minus {{ 
    background: linear-gradient(135deg, rgba(255,255,255,.30) 0%, rgba(255,165,0,.45) 50%, rgba(230,126,34,.60) 100%); 
    border: 1px solid rgba(255,255,255,.4); 
    box-shadow: inset 0 0 15px rgba(255,255,255,.5), 0 8px 32px rgba(0,0,0,.1); 
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}}

.flat-warning-card {{ 
    background: linear-gradient(135deg, rgba(255,255,255,.30) 0%, rgba(255,82,82,.45) 50%, rgba(183,28,28,.60) 100%); 
    border: 1px solid rgba(255,255,255,.4); 
    box-shadow: inset 0 0 15px rgba(255,255,255,.5), 0 8px 32px rgba(0,0,0,.1); 
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius:12px; 
    padding:18px; 
    color:white; 
    font-weight:bold; 
    text-align:center; 
    max-width:500px; 
    margin: 10px auto; 
}}

.flat-phone-text {{ 
    color:white; 
    font-size:20px; 
    font-weight:800; 
    text-align: left !important; 
    z-index: 2; 
    width: 100% !important; 
    direction: ltr !important; 
}}

/* =========================================
   DRAWER
========================================= */
.drawer {{ 
    position:fixed; 
    top:0; 
    right:-290px; 
    width:290px; 
    height:100%; 
    background: rgba(22,27,34,.95); 
    backdrop-filter:blur(20px); 
    -webkit-backdrop-filter:blur(20px);
    border-left: 2px solid #00bfff; 
    transition: right 0.4s ease-in-out; 
    z-index:200000; 
    padding:30px; 
    box-sizing: border-box;
}}

.drawer.open {{ right:0; }}

.metric-box {{ 
    background: rgba(255,255,255,.05); 
    padding:10px; 
    border-radius:8px; 
    margin-bottom:10px; 
    text-align:center; 
    border: 1px solid rgba(0,191,255,.2); 
}}

.custom-modal-backdrop {{ 
    position: fixed; 
    top: 0; 
    left: 0; 
    width: 100%; 
    height: 100%; 
    background: rgba(0,0,0,0.75); 
    z-index: 999999; 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    backdrop-filter: blur(5px); 
}}
</style>""")

def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f"""<div class="glass-card" style="box-shadow: 0 0 15px rgba(0, 191, 255, 0.25);"><h3 style="color:#00bfff; text-align:center; margin-bottom:15px;">📱 {escape(str(model_name))}</h3><div style="font-size:16px; line-height:2; text-align:right; direction: rtl !important;">📏 <b>المقاس الفني:</b> <span style="color:#00bfff;">{escape(str(size_grp))}</span><br>📺 <b>نوع الشاشة:</b> <span style="color:#00bfff;">{escape(str(panel_grp))}</span><br>👁️ <b>المستشعر الحركي:</b> <span style="color:#00bfff;">{escape(str(sensor_grp))}</span></div></div>""")

def draw_neon_section(title=None, models_list=None, color_hex="#00bfff", badge_icon="📱", plan_type="exact"):
    if not models_list: return ui.div()
    class_map = {"exact": "flat-exact", "plus": "flat-plus", "minus": "flat-minus"}
    card_class = class_map.get(plan_type, "flat-exact")
    cards = [ui.h4(f"{badge_icon} {title}", style=f"color:{color_hex}; direction:rtl !important; text-align:right !important; margin-top:20px; margin-bottom:10px; max-width:500px; margin-left:auto; margin-right:auto;")]
    for model in models_list:
        cards.append(ui.HTML(f"""<div class="ammar-flat-card {card_class}" style="direction: ltr !important; text-align: left !important;"><div class="flat-phone-text" style="width:100% !important; text-align:left !important; direction: ltr !important;">{escape(str(model))}</div></div>"""))
    return ui.div(*cards)

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    panel_options = {p: p for p in existing_panels if p}
    sensor_options = {s: s for s in existing_sensors if s}
    return ui.div(
        ui.div(
            ui.div(
                ui.h3(f"📋 المواصفات الفنية لـ {phone_name}", style="color:#3498db; text-align:center; margin-bottom:20px;"), 
                ui.input_numeric("p2_size", "📏 أدخل مقاس الشاشة يدوياً (مثال: 6.53):", value=None, step=0.01), 
                ui.p("", style="margin-bottom:15px;"), 
                ui.div(
                    ui.input_select("p2_panel", "📺 اختر شكل ونوع الشاشة:", choices=panel_options), 
                    ui.input_action_button("btn_add_panel", "➕", class_="btn-neon", style="padding:10px; margin-top:24px; background:#3498db; border:none; color:white; border-radius:8px;"), 
                    style="display:flex; gap:5px; width:100%; margin-bottom:15px; align-items: center;"
                ), 
                ui.div(
                    ui.input_select("p2_sensor", "👁️ اختر نوع مستشعر التقارب الصارم:", choices=sensor_options), 
                    ui.input_action_button("btn_add_sensor", "➕", class_="btn-neon", style="padding:10px; margin-top:24px; background:#3498db; border:none; color:white; border-radius:8px;"), 
                    style="display:flex; gap:5px; width:100%; margin-bottom:20px; align-items: center;"
                ), 
                ui.div(
                    ui.input_action_button("p2_search", "🔍 فحص وتطابق المجموعات", class_="btn-neon", style="background:#2ecc71; color:white; padding:12px; border:none; border-radius:8px; width:100%; font-weight:bold;"),
                    style="width:100%;"
                ),
                class_="glass-card",
                style="width:90%; max-width:500px; background:rgba(22,27,34,.98); border:1px solid #00bfff;"
            ),
            class_="custom-modal-backdrop"
        )
    )

def draw_plan_3_modal(phone_name, existing_panels, existing_sensors):
    panel_options = {p: p for p in existing_panels if p}
    sensor_options = {s: s for s in existing_sensors if s}
    return ui.div(
        ui.div(
            ui.div(
                ui.h3(f"🔮 الخطة البديلة المتقدمة لـ {phone_name}", style="color:#e67e22; text-align:center; margin-bottom:20px;"), 
                ui.input_numeric("p3_size", "📏 مقاس الشاشة المقترح:", value=None, step=0.01), 
                ui.p("", style="margin-bottom:15px;"), 
                ui.div(
                    ui.input_select("p3_panel", "📺 تخصيص شكل الشاشة:", choices=panel_options), 
                    style="width:100%; margin-bottom:15px;"
                ), 
                ui.div(
                    ui.input_select("p3_sensor", "👁️ تخصيص مستشعر التقارب المتقدم:", choices=sensor_options), 
                    style="width:100%; margin-bottom:20px;"
                ), 
                ui.div(
                    ui.input_action_button("p3_search", "⚡ تشغيل فحص المطابقة الذكي", class_="btn-neon", style="background:#e67e22; color:white; padding:12px; border:none; border-radius:8px; width:100%; font-weight:bold;"),
                    style="width:100%;"
                ),
                class_="glass-card",
                style="width:90%; max-width:500px; background:rgba(22,27,34,.98); border:1px solid #e67e22;"
            ),
            class_="custom-modal-backdrop"
        )
    )
