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
