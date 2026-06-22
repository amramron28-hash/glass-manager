import os
import base64
from shiny import ui

_bg_cache = None

def inject_pwa_and_styles():
    global _bg_cache
    if _bg_cache is None:
        paths = ["phone_image.webp", "./phone_image.webp", "/app/phone_image.webp"]
        img = ""
        for p in paths:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    img = base64.b64encode(f.read()).decode()
                break
        _bg_cache = img

    # حقن التنسيق لـ Shiny
    style_content = f"""
    <style>
    html, body, .container-fluid {{
        background-color: #0a0e17 !important;
        background-image: linear-gradient(rgba(10,14,23,.20), rgba(10,14,23,.20)), url('data:image/webp;base64,{_bg_cache}');
        background-size: 92% auto !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    .search-box {{ width: 90%; max-width: 500px; margin: 20px auto; }}
    </style>
    """
    return ui.HTML(style_content)

def draw_technical_coords(size_grp, panel_grp, sensor_grp):
    return ui.HTML(f"""
    <div style="background:rgba(15,23,42,.85); padding:8px 15px; border-radius:10px; border:1px solid #00bfff; margin-bottom:10px; direction:rtl; text-align:right;">
        <div style="font-size:16px; line-height:1.7; color:white;">
            📏 <b>المقاس:</b> {size_grp} <br>
            📺 <b>نوع الشاشة:</b> {panel_grp} <br>
            👁️ <b>المستشعر:</b> {sensor_grp}
        </div>
    </div>
    """)

def draw_neon_section(title, models_list, color_hex, badge_icon):
    if not models_list: return ui.div()
    
    cards = [ui.h4(f"{badge_icon} {title}", style=f"color:{color_hex}; direction:rtl; text-align:right; margin:8px 0;")]
    
    for model in models_list:
        cards.append(ui.HTML(f"""
        <div style="background:rgba(10,14,23,.90); border:1px solid {color_hex}; border-radius:10px; padding:10px; margin-bottom:8px; display:flex; direction:ltr; justify-content:space-between; align-items:center;">
            <div style="font-size:18px; font-weight:800; color:white; text-align:left;">{model}</div>
            <div style="width:45px; height:45px; border-radius:8px; border:1px dashed #00bfff;"></div>
        </div>
        """))
    return ui.div(*cards)

def draw_control_panel(total_models, empty_groups_count):
    return ui.sidebar(
        ui.h3("🛠️ لوحة التحكم", style="text-align:center; color:#00bfff;"),
        ui.accordion(
            ui.accordion_panel("⚙️ الإعدادات", ui.input_checkbox("monitor", "تفعيل المراقب", True)),
            ui.accordion_panel("🛡️ المراقب الصامت", 
                ui.div(f"📱 الهواتف: {total_models}"),
                ui.div(f"🧹 مراجعة: {empty_groups_count}")
            )
        )
    )
