import os
import base64
from html import escape
from shiny import ui

# --- 1. دالة معالجة الصورة الخلفية ---
_bg_cache = None

def get_bg_style():
    global _bg_cache
    if _bg_cache is None:
        for p in ["phone_image.webp", "./phone_image.webp", "/app/phone_image.webp"]:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    _bg_cache = base64.b64encode(f.read()).decode()
                break
    
    if _bg_cache:
        return f"background-image: linear-gradient(rgba(10,14,23,.85), rgba(10,14,23,.85)), url('data:image/webp;base64,{_bg_cache}');"
    return "background-color: #0a0e17;"

# --- 2. تعريف الستايل الموحد (CSS) ---
def inject_styles():
    return ui.HTML(f"""
    <style>
        body {{ {get_bg_style()} background-size: cover; background-attachment: fixed; color: white; direction: rtl; font-family: sans-serif; }}
        
        /* البطاقة الزجاجية الأساسية */
        .glass-card-base {{
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(10px);
            box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.4), 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            margin: 15px auto;
            max-width: 500px;
        }}

        /* ألوان البطاقات المدمجة */
        .card-green  {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(76,175,80,0.4) 50%, rgba(46,125,50,0.6) 100%); }}
        .card-blue   {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(33,150,243,0.4) 50%, rgba(21,101,192,0.6) 100%); }}
        .card-red    {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(244,67,54,0.4) 50%, rgba(198,40,40,0.6) 100%); }}
        .card-orange {{ background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,152,0,0.4) 50%, rgba(239,108,0,0.6) 100%); }}
        
        .phone-text {{ color: white; font-size: 18px; font-weight: bold; text-align: left; direction: ltr; }}
    </style>
    """)

# --- 3. دوال بناء الواجهة ---
def draw_neon_section(title, models_list, card_type="blue"):
    card_class = f"glass-card-base card-{card_type}"
    cards = [ui.h4(title, style="text-align: right; color: #fff; margin-top:20px;")]
    for model in models_list:
        cards.append(ui.div(model, class_=f"{card_class} phone-text"))
    return ui.div(*cards)

def draw_plan_2_modal(phone_name, panel_options, sensor_options):
    return ui.div(
        ui.div(
            ui.h3(f"📋 المواصفات لـ {phone_name}", style="text-align:center;"),
            ui.input_numeric("p2_size", "📏 مقاس الشاشة:", value=6.5),
            ui.input_select("p2_panel", "📺 نوع الشاشة:", choices=panel_options),
            ui.input_select("p2_sensor", "👁️ نوع المستشعر:", choices=sensor_options),
            ui.input_action_button("p2_search", "🔍 بحث", class_="btn-success", style="width:100%; margin-top:15px;"),
            class_="glass-card-base card-blue"
        ),
        class_="custom-modal-backdrop"
    )

# --- 4. مثال على التطبيق الرئيسي ---
app_ui = ui.page_fluid(
    inject_styles(),
    ui.h2("نظام فحص الهواتف", style="text-align:center;"),
    draw_neon_section("هواتف مدعومة", ["iPhone 15 Pro", "Samsung S24"], "green"),
    draw_neon_section("هواتف تحت الفحص", ["Pixel 8"], "red")
)
