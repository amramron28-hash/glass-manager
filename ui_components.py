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

    bg_style = f"background-image: linear-gradient(rgba(10,14,23,.85), rgba(10,14,23,.85)), url('data:image/webp;base64,{_bg_cache}');" if _bg_cache else "background-color: #0a0e17;"

    return ui.HTML(f"""<style>
        body {{ {bg_style} background-size: cover; background-attachment: fixed; color: white; direction: rtl; }}
        
        /* التنسيق الزجاجي الموحد */
        .glass-card-base {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 20px;
            margin: 15px auto;
            box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.1);
        }}

        /* ألوان البطاقات المدمجة */
        .card-green  {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(76,175,80,0.4) 50%, rgba(46,125,50,0.6) 100%); }}
        .card-blue   {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(33,150,243,0.4) 50%, rgba(21,101,192,0.6) 100%); }}
        .card-red    {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(244,67,54,0.4) 50%, rgba(198,40,40,0.6) 100%); }}
        .card-orange {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,152,0,0.4) 50%, rgba(239,108,0,0.6) 100%); }}

        .custom-modal-backdrop {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 999999; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(5px); }}
        .flat-phone-text {{ color: white; font-size: 20px; font-weight: 800; direction: ltr !important; text-align: left; }}
    </style>""")

def draw_neon_section(title, models_list, plan_type="blue", badge_icon="📱"):
    class_map = {"exact": "card-green", "plus": "card-blue", "minus": "card-red", "warning": "card-orange"}
    card_color = class_map.get(plan_type, "card-blue")
    
    cards = [ui.h4(f"{badge_icon} {title}", style="text-align: right; color: #fff; margin-top:20px;")]
    for model in models_list:
        cards.append(ui.div(model, class_=f"glass-card-base {card_color} flat-phone-text"))
    return ui.div(*cards)

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    return ui.div(
        ui.div(
            ui.h3(f"📋 المواصفات الفنية لـ {phone_name}", style="color:white; text-align:center; margin-bottom:20px;"),
            ui.input_numeric("p2_size", "📏 مقاس الشاشة:", value=6.5, step=0.01),
            ui.input_select("p2_panel", "📺 نوع الشاشة:", choices={p: p for p in existing_panels if p}),
            ui.input_select("p2_sensor", "👁️ نوع المستشعر:", choices={s: s for s in existing_sensors if s}),
            ui.div(
                ui.input_action_button("p2_search", "🔍 بحث", style="background:#2ecc71; color:white; border:none; padding:10px; border-radius:8px; flex:2;"),
                ui.input_action_button("p2_cancel", "إلغاء", style="background:#e74c3c; color:white; border:none; padding:10px; border-radius:8px; flex:1;"),
                style="display:flex; gap:10px; margin-top:20px;"
            ),
            class_="glass-card-base card-blue", style="max-width:450px;"
        ),
        class_="custom-modal-backdrop"
    )

def draw_plan_3_modal(phone_name, size, panel, sensor):
    return ui.div(
        ui.div(
            ui.h3("🚨 إنشاء مجموعة جديدة", style="color:#e67e22; text-align:center;"),
            ui.p(f"للهاتف: {phone_name}", style="text-align:center; color:#ccc;"),
            ui.div(f"المقاس: {size} | الشاشة: {panel} | المستشعر: {sensor}", 
                   style="background:rgba(230,126,34,0.1); padding:10px; border-radius:8px; text-align:center; color:#e67e22; margin:15px 0;"),
            ui.input_action_button("p3_submit", "💾 حفظ المجموعة", style="width:100%; background:#e67e22; color:white; border:none; padding:10px; border-radius:8px;"),
            class_="glass-card-base card-orange", style="max-width:450px;"
        ),
        class_="custom-modal-backdrop"
    )
