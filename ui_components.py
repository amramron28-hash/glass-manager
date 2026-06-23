import os
import base64
from html import escape
from shiny import ui

_bg_cache = None

def inject_pwa_and_styles():
    global _bg_cache
    if _bg_cache is None:
        img = ""
        for p in ["phone_image.webp", "./phone_image.webp", "/app/phone_image.webp"]:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    img = base64.b64encode(f.read()).decode()
                break
        _bg_cache = img

    return ui.HTML(f"""
<style>
html, body, .container-fluid {{
    background-color:#0a0e17 !important;
    background-image: linear-gradient(rgba(10,14,23,.20), rgba(10,14,23,.20)), url('data:image/webp;base64,{_bg_cache}');
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
    padding:15px 25px;
    background: rgba(13,17,23,.55);
    backdrop-filter:blur(12px);
    border-bottom: 1px solid rgba(0,191,255,.25);
}}

.search-box {{
    position:relative;
    width:90%;
    max-width:500px;
    margin:35px auto;
}}

input[type="text"], input[type="number"], select {{
    width:100%;
    background:#111827 !important;
    color:white !important;
    border:1px solid #00bfff !important;
    border-radius:12px !important;
    padding:12px !important;
    direction:rtl;
}}

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
}}

.suggestion-row {{
    padding:12px;
    color:white;
    cursor:pointer;
    border-bottom: 1px solid rgba(255,255,255,.08);
    text-align:right;
}}

.suggestion-row:hover {{
    background: rgba(0,191,255,.18);
}}

.glass-card {{
    background: rgba(255,255,255,.06);
    backdrop-filter:blur(15px);
    border: 1px solid rgba(0,191,255,.35);
    border-radius:20px;
    padding:20px;
    margin:15px auto;
    max-width:500px;
}}

.ammar-flat-card {{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:14px;
    margin-bottom:12px;
    border-radius:12px;
    width:100%;
    box-sizing:border-box;
}}

.flat-exact {{
    background: linear-gradient(135deg,#0d1f13,#07120b);
    border: 2px solid #2ecc71;
    box-shadow: 0 0 10px rgba(46,204,113,0.2);
}}

.flat-plus {{
    background: linear-gradient(135deg,#0b1a33,#060e1c);
    border: 2px solid #3498db;
    box-shadow: 0 0 10px rgba(52,152,219,0.2);
}}

.flat-minus {{
    background: linear-gradient(135deg,#2b1807,#140b03);
    border: 2px solid #e67e22;
    box-shadow: 0 0 10px rgba(230,126,34,0.2);
}}

.flat-warning-card {{
    background: linear-gradient(135deg,#26090b,#120405);
    border: 2px solid #ff4500;
    border-radius:12px;
    padding:18px;
    color:#ffb3b9;
    font-weight:bold;
    text-align:center;
    max-width:500px;
    margin: 10px auto;
}}

.flat-phone-text {{
    color:white;
    font-size:20px;
    font-weight:800;
    text-align: right;
}}

.image-placeholder-box {{
    width:50px;
    height:50px;
    border-radius:8px;
    border: 1px dashed #00bfff;
    display:flex;
    align-items:center;
    justify-content:center;
}}

.drawer {{
    position:fixed;
    top:0;
    right:-320px;
    width:290px;
    height:100%;
    background: rgba(22,27,34,.95);
    backdrop-filter:blur(20px);
    border-left: 2px solid #00bfff;
    transition:.4s;
    z-index:200000;
    padding:30px;
}}

.drawer.open {{
    right:0;
}}

.metric-box {{
    background: rgba(255,255,255,.05);
    padding:10px;
    border-radius:8px;
    margin-bottom:10px;
    text-align:center;
    border: 1px solid rgba(0,191,255,.2);
}}

.custom-modal-backdrop {{
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.75); z-index: 999999; display: flex;
    justify-content: center; align-items: center; backdrop-filter: blur(5px);
}}
</style>
""")

def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f"""
<div class="glass-card" style="box-shadow: 0 0 15px rgba(0, 191, 255, 0.25);">
<h3 style="color:#00bfff; text-align:center; margin-bottom:15px;">
📱 {escape(str(model_name))}
</h3>
<div style="font-size:16px; line-height:2; text-align:right;">
📏 <b>المقاس الفني:</b> <span style="color:#00bfff;">{escape(str(size_grp))}</span><br>
📺 <b>نوع الشاشة:</b> <span style="color:#00bfff;">{escape(str(panel_grp))}</span><br>
👁️ <b>المستشعر الحركي:</b> <span style="color:#00bfff;">{escape(str(sensor_grp))}</span>
</div>
</div>
""")

def draw_neon_section(title=None, models_list=None, color_hex="#00bfff", badge_icon="📱", plan_type="exact"):
    if models_list is None and isinstance(title, list):
        models_list = title
        title = "الهواتف المتوافقة"

    if not models_list:
        return ui.div()

    class_map = {
        "exact": "flat-exact",
        "plus": "flat-plus",
        "minus": "flat-minus"
    }
    card_class = class_map.get(plan_type, "flat-exact")

    cards = [
        ui.h4(f"{badge_icon} {title}", style=f"color:{color_hex}; direction:rtl; text-align:right; margin-top:20px; margin-bottom:10px; max-width:500px; margin-left:auto; margin-right:auto;")
    ]

    for model in models_list:
        cards.append(
            ui.HTML(f"""
<div class="ammar-flat-card {card_class}" style="max-width:500px; margin-left:auto; margin-right:auto;">
    <div class="image-placeholder-box" style="border-color:{color_hex};">
        📱
    </div>
    <div class="flat-phone-text">
        {escape(str(model))}
    </div>
</div>
""")
        )

    return ui.div(*cards)
def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    panel_options = {p: p for p in existing_panels if p}
    sensor_options = {s: s for s in existing_sensors if s}
    
    return ui.div(
        ui.div(
            ui.div(
                ui.h3(f"📋 المواصفات الفنية لـ {phone_name}", style="color:#3498db; text-align:center; margin-bottom:20px;"),
                ui.label("📏 أدخل مقاس الشاشة يدوياً (مثال: 6.53):", style="display:block; margin-bottom:5px; text-align:right;"),
                ui.input_numeric("p2_size", "", value=None, step=0.01),
                ui.p("", style="margin-bottom:15px;"),
                ui.div(
                    ui.label("📺 اختر شكل ونوع الشاشة:", style="text-align:right;"),
                    style="display:flex; justify-content:space-between; align-items:center;"
                ),
                ui.div(
                    ui.input_select("p2_panel", "", choices=panel_options),
                    ui.input_action_button("btn_add_panel", "➕", class_="btn-neon", style="padding:10px; margin-right:5px; background:#3498db; border:none; color:white; border-radius:8px;"),
                    style="display:flex; gap:5px; width:100%; margin-bottom:15px;"
                ),
                ui.div(
                    ui.label("👁️ اختر نوع مستشعر التقارب الصارم:", style="text-align:right;"),
                ),
                ui.div(
                    ui.input_select("p2_sensor", "", choices=sensor_options),
                    ui.input_action_button("btn_add_sensor", "➕", class_="btn-neon", style="padding:10px; margin-right:5px; background:#3498db; border:none; color:white; border-radius:8px;"),
                    style="display:flex; gap:5px; width:100%; margin-bottom:20px;"
                ),
                ui.div(
                    ui.input_action_button("p2_search", "🔍 فحص وتطابق المجموعات", class_="btn-neon", style="background:#2ecc71; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold; flex:2;"),
                    ui.input_action_button("p2_cancel", "إلغلاق", class_="btn-neon", style="background:#e74c3c; color:white; padding:12px; border:none; border-radius:8px; flex:1;"),
                    style="display:flex; gap:10px; justify-content:space-between;"
                ),
                class_="glass-card", style="width:90%; max-width:450px; background:#161b22; border-color:#3498db; border-width:2px; box-shadow: 0 0 25px rgba(52, 152, 219, 0.4);"
            ),
            class_="custom-modal-backdrop"
        ),
        id="plan_2_modal_container"
    )

def draw_plan_3_modal(phone_name, size, panel, sensor):
    return ui.div(
        ui.div(
            ui.div(
                ui.h3("🚨 خطة الطوارئ 3: إنشاء مجموعة جديدة", style="color:#e67e22; text-align:center; margin-bottom:15px;"),
                ui.p(f"النظام لم يعثر على أي مجموعة مطابقة للمواصفات المدخلة للهاتف ({phone_name}).", style="text-align:center; color:#bbb; font-size:14px;"),
                ui.div(
                    f"📐 المقاس المقترح: {size} | 📺 الشاشة: {panel} | 👁️ المستشعر: {sensor}",
                    style="background:rgba(230,126,34,0.1); border:1px solid #e67e22; padding:10px; border-radius:8px; font-size:13px; text-align:center; margin-bottom:20px; color:#e67e22;"
                ),
                ui.p("هل تريد تسجيل هذا الهاتف وتأسيس مرجع فني ومجموعة جديدة له في السحاب؟", style="text-align:right; font-size:14px; margin-bottom:20px;"),
                ui.div(
                    ui.input_action_button("p3_submit", "💾 نعم، أنشئ المجموعة واحفظ", class_="btn-neon", style="background:#e67e22; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold; flex:2;"),
                    ui.input_action_button("p3_cancel", "تراجع", class_="btn-neon", style="background:#7f8c8d; color:white; padding:12px; border:none; border-radius:8px; flex:1;"),
                    style="display:flex; gap:10px;"
                ),
                class_="glass-card", style="width:90%; max-width:450px; background:#161b22; border-color:#e67e22; border-width:2px; box-shadow: 0 0 25px rgba(230, 126, 34, 0.4);"
            ),
            class_="custom-modal-backdrop"
        ),
        id="plan_3_modal_container"
    )

def draw_control_panel(total_models=0, empty_groups_count=0):
    return ui.div(
        ui.h3("🛠️ لوحة التحكم", style="color:#00bfff;text-align:center;"),
        ui.div(f"📱 الهواتف المسجلة: {total_models}", class_="glass-card"),
        ui.div(f"🧹 مجموعات للمراجعة: {empty_groups_count}", class_="glass-card")
    )
