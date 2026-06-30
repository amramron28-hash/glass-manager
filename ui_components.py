hereimport os
import base64
from html import escape
from shiny import ui

_bg_cache = None


def inject_pwa_and_styles():
    """حقن PWA والأنماط - يستخدم style.css الخارجي"""
    global _bg_cache
    if _bg_cache is None:
        for p in ["phone_image.webp", "./phone_image.webp", "/app/phone_image.webp"]:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    _bg_cache = base64.b64encode(f.read()).decode()
                break
    
    # خلفية ديناميكية فقط (إذا وُجدت الصورة)
    bg_style = f"background-image:linear-gradient(rgba(10,14,23,.20),rgba(10,14,23,.20)),url('data:image/webp;base64,{_bg_cache}');" if _bg_cache else ""
    
    return ui.tags.head(
        # ✅ ربط ملف CSS الخارجي
        ui.tags.link(rel="stylesheet", href="style.css"),
        
        # ✅ سطر واحد فقط للخلفية الديناميكية
        ui.tags.style(f"html, body {{ {bg_style} }}") if bg_style else None,
        
        # ✅ PWA Manifest
        ui.tags.link(rel="manifest", href="manifest.json"),
        
        # ✅ JavaScript للـ Drawer و Service Worker
        ui.tags.script("""
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function(){ 
                navigator.serviceWorker.register('/service-worker.js'); 
            });
        }
        Shiny.addCustomMessageHandler('toggle_drawer', function(msg){
            let d = document.getElementById('settings_drawer');
            if(d){ 
                if(msg === 'open') d.classList.add('open'); 
                else d.classList.remove('open'); 
            }
        });
        """)
    )


def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    """عرض الإحداثيات الفنية للموديل"""
    return ui.HTML(f"""<div class="glass-card">
        <h3 style="color:#00bfff; text-align:center;">📱 {escape(str(model_name))}</h3>
        <div style="font-size:16px; line-height:2; text-align:right; direction:rtl;">
            📏 <b>المقاس الفني:</b> <span style="color:#00bfff">{escape(str(size_grp))}</span><br>
            📺 <b>نوع الشاشة:</b> <span style="color:#00bfff">{escape(str(panel_grp))}</span><br>
            👁️ <b>المستشعر:</b> <span style="color:#00bfff">{escape(str(sensor_grp))}</span>
        </div>
    </div>""")


def draw_neon_section(title, models_list, color_hex="#00bfff", badge_icon="📱", plan_type="exact"):
    """عرض قسم من نتائج المطابقة"""
    if not models_list:
        return ui.div()
    class_map = {"exact": "flat-exact", "plus": "flat-plus", "minus": "flat-minus"}
    card_class = class_map.get(plan_type, "flat-exact")
    cards = [ui.h4(f"{badge_icon} {title}", style=f"color:{color_hex}; text-align:right; direction:rtl;")]
    for model in models_list:
        cards.append(ui.HTML(f'<div class="ammar-flat-card {card_class}"><div class="flat-phone-text">{escape(str(model))}</div></div>'))
    return ui.div(*cards)


def _draw_plan_modal(title, title_color, phone_name, size_label, size_id, panel_label, panel_id, sensor_label, sensor_id, btn_label, btn_id, btn_color, panels, sensors):
    """دالة مشتركة لبناء نوافذ Plan 2 و Plan 3"""
    panel_options = {p: p for p in panels if p}
    sensor_options = {s: s for s in sensors if s}
    return ui.div(ui.div(ui.div(
        ui.h3(title.format(phone_name=phone_name), style=f"color:{title_color}; text-align:center;"),
        ui.input_numeric(size_id, size_label, value=None, step=0.01),
        ui.input_select(panel_id, panel_label, choices=panel_options),
        ui.input_select(sensor_id, sensor_label, choices=sensor_options),
        ui.input_action_button(btn_id, btn_label, class_="btn-neon", style=f"width:100%; background:{btn_color}; color:white; padding:12px; border-radius:8px; border:none;"),
        class_="glass-card", style="width:90%; max-width:500px; background:rgba(22,27,34,.98);"
    ), class_="custom-modal-backdrop"))


def draw_plan_2_modal(phone_name, panels, sensors):
    """نافذة Plan 2 - المواصفات الفنية"""
    return _draw_plan_modal(
        "📋 المواصفات الفنية لـ {phone_name}", "#3498db", phone_name,
        "📏 مقاس الشاشة:", "p2_size",
        "📺 نوع الشاشة:", "p2_panel",
        "👁️ نوع المستشعر:", "p2_sensor",
        "🔍 فحص المطابقة", "p2_search", "#2ecc71",
        panels, sensors
    )


def draw_plan_3_modal(phone_name, panels, sensors):
    """نافذة Plan 3 - الخطة البديلة"""
    return _draw_plan_modal(
        "🔮 الخطة البديلة المتقدمة لـ {phone_name}", "#e67e22", phone_name,
        "📏 المقاس المقترح:", "p3_size",
        "📺 تخصيص نوع الشاشة:", "p3_panel",
        "👁️ تخصيص المستشعر:", "p3_sensor",
        "⚡ تشغيل البحث الذكي", "p3_search", "#e67e22",
        panels, sensors
    )


def draw_warning_card(message):
    """بطاقة تحذير"""
    return ui.HTML(f'<div class="flat-warning-card">⚠️ {escape(str(message))}</div>')


def draw_database_status(total):
    """عرض عداد قاعدة البيانات"""
    return ui.div(ui.div(f"📊 قاعدة البيانات: {total} هاتف", class_="metric-box"))


# ================================================================
# تعريف الواجهة الرئيسية (app_ui) - مصححة بالكامل
# ================================================================
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    
    # 🌟 الهيدر
    ui.div(
        ui.div(
            ui.div("ZEGAAR AMMAR", class_="brand-neon-main"),
            ui.div("GLASS MANAGER", class_="brand-neon-sub"),
            class_="brand-neon-title"
        ),
        ui.input_action_button("btn_settings", "⋮", class_="btn-dots-menu"),
        class_="header-bar"
    ),
    
    # 🌟 نافذة الإعدادات الجانبية (Drawer)
    ui.div(
        ui.tags.button(
            "×", 
            id="btn_close_drawer", 
            class_="drawer-close-btn", 
            onclick="Shiny.setInputValue('btn_close_drawer_trigger', Math.random(), {priority:'event'});"
        ),
        ui.h3("⚙️ الإعدادات العامة", style="color:#00bfff; text-align:center; margin-bottom:25px; font-weight:800;"),
        
        # ✅ عناصر ديناميكية مربوطة بـ server.py
        ui.output_ui("database_status_area"),
        ui.output_ui("notifications_area"),
        ui.output_ui("monitor_area"),
        
        id="settings_drawer",
        class_="drawer"
    ),
    
    # 🌟 مربع البحث
    ui.div(
        ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."),
        ui.output_ui("suggestions_curtain"),
        class_="search-box"
    ),
    
    # 🌟 مناطق العرض الرئيسية
    ui.output_ui("results_area"),
    ui.output_ui("modal_layer")
)
