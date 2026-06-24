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

.header-bar {{ 
    display:flex; 
    justify-content:space-between; 
    align-items:center; 
    padding:10px 25px; 
    background: rgba(13,17,23,.55); 
    backdrop-filter:blur(12px); 
    border-bottom: 1px solid rgba(0,191,255,.25); 
}}

.brand-neon-title {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    text-align: right;
    line-height: 1.1;
}}
.brand-neon-main {{
    color: #00bfff;
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 1px;
    text-shadow: 0 0 4px rgba(0,191,255,0.6), 0 0 12px rgba(0,191,255,0.4);
}}
.brand-neon-sub {{
    color: #87ceeb;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 3px;
    text-shadow: 0 0 3px rgba(135,206,235,0.5);
    opacity: 0.9;
}}

.search-box {{ position:relative; width:90%; max-width:500px; margin:25px auto; }}

/* إجبار حقل البحث وعناصر الاختيار على المحاذاة الصارمة لجهة اليمين دائماً */
input[type="text"], input[type="number"], select {{ 
    width:100%; 
    background:#111827 !important; 
    color:white !important; 
    border:1px solid #00bfff !important; 
    border-radius:12px !important; 
    padding:12px !important; 
    direction: rtl !important; 
    text-align: right !important;
}}

.suggestions-curtain {{ position:absolute; top:60px; right:0; left:0; background: rgba(22,27,34,.96); border: 1px solid #00bfff; border-radius:12px; max-height:240px; overflow-y:auto; z-index:99999; backdrop-filter:blur(15px); }}
.suggestion-row {{ padding:12px; color:white; cursor:pointer; border-bottom: 1px solid rgba(255,255,255,.08); text-align:right; }}
.suggestion-row:hover {{ background: rgba(0,191,255,.18); }}
.glass-card {{ background: rgba(255,255,255,.06); backdrop-filter:blur(15px); border: 1px solid rgba(0,191,255,.35); border-radius:20px; padding:20px; margin:15px auto; max-width:500px; }}

.ammar-flat-card {{ 
    display:flex; 
    justify-content: flex-end; 
    align-items:center; 
    padding:16px 24px; 
    margin-bottom:14px; 
    border-radius:24px; 
    width:100%; 
    box-sizing:border-box; 
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}}

.ammar-flat-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 50%;
    background: linear-gradient(rgba(255,255,255,0.25), rgba(255,255,255,0));
    border-radius: 24px 24px 0 0;
    pointer-events: none;
}}

.flat-exact {{ 
    background: radial-gradient(circle at center, #76d74b 0%, #3ca012 70%, #1e5a04 100%); 
    border: 1px solid #a3ff78; 
    box-shadow: inset 0 0 15px rgba(255,255,255,0.4), 0 0 15px rgba(60,160,18,0.4); 
}}

.flat-plus {{ 
    background: radial-gradient(circle at center, #00d2ff 0%, #007bb5 70%, #00466b 100%); 
    border: 1px solid #7be8ff; 
    box-shadow: inset 0 0 15px rgba(255,255,255,0.4), 0 0 15px rgba(0,123,181,0.4); 
}}

.flat-minus {{ 
    background: radial-gradient(circle at center, #ff5e3a 0%, #ff2a00 60%, #990000 100%); 
    border: 1px solid #ff9d85; 
    box-shadow: inset 0 0 15px rgba(255,255,255,0.4), 0 0 15px rgba(255,42,0,0.4); 
}}

.flat-warning-card {{ background: linear-gradient(135deg,#26090b,#120405); border: 2px solid #ff4500; border-radius:12px; padding:18px; color:#ffb3b9; font-weight:bold; text-align:center; max-width:500px; margin: 10px auto; }}
.flat-phone-text {{ color:white; font-size:20px; font-weight:800; text-align: right; text-shadow: 0 2px 4px rgba(0,0,0,0.6); z-index: 2; }}
.drawer {{ position:fixed; top:0; right:-320px; width:290px; height:100%; background: rgba(22,27,34,.95); backdrop-filter:blur(20px); border-left: 2px solid #00bfff; transition:.4s; z-index:200000; padding:30px; }}
.drawer.open {{ right:0; }}
.metric-box {{ background: rgba(255,255,255,.05); padding:10px; border-radius:8px; margin-bottom:10px; text-align:center; border: 1px solid rgba(0,191,255,.2); }}
.custom-modal-backdrop {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.75); z-index: 999999; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(5px); }}
</style>""")

def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f"""<div class="glass-card" style="box-shadow: 0 0 15px rgba(0, 191, 255, 0.25);"><h3 style="color:#00bfff; text-align:center; margin-bottom:15px;">📱 {escape(str(model_name))}</h3><div style="font-size:16px; line-height:2; text-align:right;">📏 <b>المقاس الفني:</b> <span style="color:#00bfff;">{escape(str(size_grp))}</span><br>📺 <b>نوع الشاشة:</b> <span style="color:#00bfff;">{escape(str(panel_grp))}</span><br>👁️ <b>المستشعر الحركي:</b> <span style="color:#00bfff;">{escape(str(sensor_grp))}</span></div></div>""")
def draw_neon_section(title=None, models_list=None, color_hex="#00bfff", badge_icon="📱", plan_type="exact"):
    if not models_list: return ui.div()
    class_map = {"exact": "flat-exact", "plus": "flat-plus", "minus": "flat-minus"}
    card_class = class_map.get(plan_type, "flat-exact")
    cards = [ui.h4(f"{badge_icon} {title}", style=f"color:{color_hex}; direction:rtl; text-align:right; margin-top:20px; margin-bottom:10px; max-width:500px; margin-left:auto; margin-right:auto;")]
    for model in models_list:
        # إجبار نصوص الهواتف بالكامل على البقاء في جهة اليمين بشكل مطلق وثابت ومتناسق
        cards.append(ui.HTML(f"""<div class="ammar-flat-card {card_class}" style="direction: rtl !important;"><div class="flat-phone-text" style="width:100%; text-align:right !important;">{escape(str(model))}</div></div>"""))
    return ui.div(*cards)

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    panel_options = {p: p for p in existing_panels if p}
    sensor_options = {s: s for s in existing_sensors if s}
    return ui.div(ui.div(ui.div(ui.h3(f"📋 المواصفات الفنية لـ {phone_name}", style="color:#3498db; text-align:center; margin-bottom:20px;"), ui.input_numeric("p2_size", "📏 أدخل مقاس الشاشة يدوياً (مثال: 6.53):", value=None, step=0.01), ui.p("", style="margin-bottom:15px;"), ui.div(ui.input_select("p2_panel", "📺 اختر شكل ونوع الشاشة:", choices=panel_options), ui.input_action_button("btn_add_panel", "➕", class_="btn-neon", style="padding:10px; margin-top:24px; background:#3498db; border:none; color:white; border-radius:8px;"), style="display:flex; gap:5px; width:100%; margin-bottom:15px; align-items: center;"), ui.div(ui.input_select("p2_sensor", "👁️ اختر نوع مستشعر التقارب الصارم:", choices=sensor_options), ui.input_action_button("btn_add_sensor", "➕", class_="btn-neon", style="padding:10px; margin-top:24px; background:#3498db; border:none; color:white; border-radius:8px;"), style="display:flex; gap:5px; width:100%; margin-bottom:20px; align-items: center;"), ui.div(ui.input_action_button("p2_search", "🔍 فحص وتطابق المجموعات", class_="btn-neon", style="background:#2ecc71; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold; flex:2;"), ui.input_action_button("p2_cancel", "إلغلاق", class_="btn-neon", style="background:#e74c3c; color:white; padding:12px; border:none; border-radius:8px; flex:1;"), style="display:flex; gap:10px; justify-content:space-between;"), class_="glass-card", style="width:90%; max-width:450px; background:#161b22; border-color:#3498db; border-width:2px; box-shadow: 0 0 25px rgba(52, 152, 219, 0.4);"), class_="custom-modal-backdrop"), id="plan_2_modal_container")

def draw_plan_3_modal(phone_name, size, panel, sensor):
    info_str = f"📐 المقاس المقترح: {size} | 📺 الشاشة: {panel} | 👁️ المستشعر: {sensor}"
    card_body = ui.div(
        ui.h3("🚨 خطة الطوارئ 3: إنشاء مجموعة جديدة", style="color:#e67e22; text-align:center; margin-bottom:15px;"),
        ui.p(f"النظام لم يعثر على أي مجموعة مطابقة للمواصفات المدخلة للهاتف ({phone_name}).", style="text-align:center; color:#bbb; font-size:14px;"),
        ui.div(info_str, style="background:rgba(230,126,34,0.1); border:1px solid #e67e22; padding:10px; border-radius:8px; font-size:13px; text-align:center; margin-bottom:20px; color:#e67e22;"),
        ui.p("هل تريد تسجيل هذا الهاتف وتأسيس مرجع فني ومجموعة جديدة له في السحاب?", style="text-align:right; font-size:14px; margin-bottom:20px;"),
        ui.div(
            ui.input_action_button("p3_submit", "💾 نعم، أنشئ المجموعة واحفظ", class_="btn-neon", style="background:#e67e22; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold; flex:2;"),
            ui.input_action_button("p3_cancel", "تراجع", class_="btn-neon", style="background:#7f8c8d; color:white; padding:12px; border:none; border-radius:8px; flex:1;"),
            style="display:flex; gap:10px;"
        ),
        class_="glass-card",
        style="""
            width:90%;
            max-width:500px;
            background:#161b22;
            border:2px solid #e67e22;
            box-shadow:0 0 25px rgba(230,126,34,.35);
        """
    )
    return ui.div(
        card_body,
        class_="custom-modal-backdrop",
        id="plan_3_modal_container"
    )
