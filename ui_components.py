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

.flat-exact {{
    background: linear-gradient(135deg, rgba(255,255,255,.30) 0%, rgba(76,187,85,.45) 50%, rgba(34,111,41,.60) 100%);
    border:1px solid rgba(255,255,255,.4);
    box-shadow: inset 0 0 15px rgba(255,255,255,.5), 0 8px 32px rgba(0,0,0,.1);
    backdrop-filter: blur(1px);
}}

.flat-plus {{
    background: linear-gradient(135deg, rgba(255,255,255,.30) 0%, rgba(41,98,255,.50) 50%, rgba(13,50,163,.60) 100%);
    border:1px solid rgba(255,255,255,.4);
    box-shadow: inset 0 0 15px rgba(255,255,255,.5), 0 8px 32px rgba(0,0,0,.1);
    backdrop-filter: blur(1px);
}}

.flat-minus {{
    background: linear-gradient(135deg, rgba(255,255,255,.30) 0%, rgba(255,82,82,.45) 50%, rgba(183,28,28,.60) 100%);
    border:1px solid rgba(255,255,255,.4);
    box-shadow: inset 0 0 15px rgba(255,255,255,.5), 0 8px 32px rgba(0,0,0,.1);
    backdrop-filter: blur(1px);
}}

.flat-warning {{
    background: linear-gradient(135deg, rgba(255,255,255,.30) 0%, rgba(255,165,0,.45) 50%, rgba(230,126,34,.60) 100%);
    border:1px solid rgba(255,255,255,.4);
    box-shadow: inset 0 0 15px rgba(255,255,255,.5), 0 8px 32px rgba(0,0,0,.1);
    backdrop-filter: blur(1px);
}}
</style>""")

def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f"""<div class="glass-card"><h3>📱 {escape(str(model_name))}</h3></div>""")

def draw_neon_section(title=None, models_list=None, color_hex="#00bfff", badge_icon="📱", plan_type="exact"):
    if not models_list:
        return ui.div()

    class_map = {
        "exact": "flat-exact",
        "plus": "flat-plus",
        "minus": "flat-minus",
        "warning": "flat-warning"
    }

    card_class = class_map.get(plan_type, "flat-exact")

    cards = [
        ui.h4(
            f"{badge_icon} {title}",
            style=f"color:{color_hex}; direction:rtl !important; text-align:right !important;"
        )
    ]

    for model in models_list:
        cards.append(
            ui.HTML(
                f'<div class="ammar-flat-card {card_class}"><div class="flat-phone-text">{escape(str(model))}</div></div>'
            )
        )

    return ui.div(*cards)

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    panel_options = {p: p for p in existing_panels if p}
    sensor_options = {s: s for s in existing_sensors if s}

    return ui.div(
        ui.div(
            ui.div(
                ui.h3(f"📋 المواصفات الفنية لـ {phone_name}")
            )
        ),
        id="plan_2_modal_container"
    )

def draw_plan_3_modal(phone_name, size, panel, sensor):
    info_str = f"📐 المقاس المقترح: {size} | 📺 الشاشة: {panel} | 👁️ المستشعر: {sensor}"

    return ui.div(
        ui.div(
            ui.h3("🚨 خطة الطوارئ 3: إنشاء مجموعة جديدة"),
            ui.p(info_str)
        ),
        class_="custom-modal-backdrop",
        id="plan_3_modal_container"
    )
