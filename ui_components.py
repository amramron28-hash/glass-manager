import os
import base64
from html import escape
from shiny import ui

# --- إعداد الخلفية ---
_bg_cache = None

def inject_pwa_and_styles():
    global _bg_cache
    # تنسيقات CSS كاملة للواجهة (النيون، الستارة، الدرج)
    return ui.HTML("""
    <style>
        :root { --neon-color: #00bfff; }
        body { background-color: #0a0e17 !important; color: white !important; direction: rtl !important; font-family: sans-serif; margin: 0; padding: 0; }
        
        .header-container { display: flex; align-items: center; justify-content: center; padding: 20px; }
        .brand-neon { 
            text-align: center; font-size: 32px; font-weight: 900; 
            color: #fff; text-shadow: 0 0 10px var(--neon-color), 0 0 20px var(--neon-color);
            letter-spacing: 3px; margin-bottom: 20px;
        }
        
        .search-container { position: relative; width: 90%; max-width: 500px; margin: 20px auto; }
        .suggestions-curtain { 
            position: absolute; top: 100%; right: 0; left: 0;
            background: #161b22; border: 1px solid var(--neon-color);
            border-radius: 0 0 15px 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.5);
            z-index: 1000; padding: 15px;
        }
        
        .drawer { 
            position: fixed; top: 0; right: -320px; width: 300px; height: 100%; 
            background: #0d1117; border-left: 2px solid var(--neon-color);
            transition: 0.4s; z-index: 2000; padding: 30px; box-shadow: -5px 0 15px rgba(0,0,0,0.5);
        }
        .drawer.open { right: 0; }
        
        .glass-card { 
            background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px; padding: 20px; margin: 15px 0; backdrop-filter: blur(10px);
        }
        .custom-modal-backdrop { 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.9); z-index: 9999; display: flex; justify-content: center; align-items: center; 
        }
    </style>
    """)

# --- الدوال الخاصة بالواجهة ---

def draw_header():
    return ui.div("ZEGAAR AMMAR GLASS MANAGER", class_="brand-neon")

def draw_sidebar_drawer(notification_count, silent_mode, phone_count):
    return ui.div(
        ui.h3("لوحة تحكم النظام", style="color:var(--neon-color); text-align:center;"),
        ui.div(f"🔔 الإشعارات: {notification_count}", class_="glass-card"),
        ui.div(f"🔇 المراقب الصامت: {'مفعل' if silent_mode else 'معطل'}", class_="glass-card"),
        ui.div(f"📱 إجمالي الهواتف: {phone_count}", class_="glass-card"),
        ui.input_action_button("close_drawer", "إغلاق الدرج", style="width:100%; background:var(--neon-color); border:none; padding:10px; border-radius:10px;"),
        class_="drawer", id="settings_drawer"
    )

def draw_suggestions_curtain(items):
    return ui.div(*[ui.div(item, style="padding:12px; border-bottom:1px solid #333; color:white;") for item in items], class_="suggestions-curtain")

def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f"""<div class="glass-card">
        <h3 style="color:var(--neon-color); text-align:center;">📱 {escape(str(model_name))}</h3>
        <div style="text-align:right; font-size:18px;">
            📏 المقاس: {escape(str(size_grp))}<br>
            📺 الشاشة: {escape(str(panel_grp))}<br>
            👁️ المستشعر: {escape(str(sensor_grp))}
        </div>
    </div>""")

def draw_neon_section(title, models_list, plan_type="exact"):
    class_map = {"exact": "card-green", "plus": "card-blue", "minus": "card-red"}
    card_class = class_map.get(plan_type, "card-blue")
    cards = [ui.h4(f"✨ {title}", style="color:var(--neon-color); text-align:right; margin-top:30px;")]
    for model in models_list:
        cards.append(ui.div(model, class_=f"glass-card {card_class}"))
    return ui.div(*cards)

def draw_plan_2_modal(phone_name, existing_panels, existing_sensors):
    return ui.div(ui.div(
        ui.h3(f"📋 المواصفات لـ {phone_name}", style="color:var(--neon-color);"),
        ui.input_numeric("p2_size", "مقاس الشاشة:", value=6.5),
        ui.input_select("p2_panel", "نوع الشاشة:", choices={p:p for p in existing_panels}),
        ui.input_select("p2_sensor", "نوع المستشعر:", choices={s:s for s in existing_sensors}),
        ui.input_action_button("p2_search", "فحص المطابقة", style="width:100%; margin-top:10px;"),
        class_="glass-card", style="background:#161b22; width:350px;"), 
        class_="custom-modal-backdrop"
    )

def draw_plan_3_modal(phone_name, size, panel, sensor):
    return ui.div(ui.div(
        ui.h3("🚨 إضافة مجموعة جديدة", style="color:#e67e22;"),
        ui.p(f"للهاتف: {phone_name}"),
        ui.input_action_button("p3_submit", "💾 حفظ المجموعة", style="width:100%; background:#e67e22;"),
        class_="glass-card", style="background:#161b22; width:350px;"), 
        class_="custom-modal-backdrop"
    )
