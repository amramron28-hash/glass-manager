from shiny import ui
import datetime

# --- دوال الواجهة المساعدة ---
def inject_pwa_and_styles():
    return ui.HTML("""
    <link rel="stylesheet" href="style_v2.css">
    <script>
        document.addEventListener('click', function(e) {
            if (e.target.id === 'btn_settings') document.getElementById('settings-drawer').classList.add('open');
            if (e.target.id === 'btn_close_drawer_trigger') document.getElementById('settings-drawer').classList.remove('open');
        });
    </script>
    """)

def draw_welcome_section(image_src: str = "phone_image.webp"):
    return ui.div(ui.tags.img(src=image_src, class_="welcome-phone-image"), class_="glass-card")

def draw_technical_coords(size, panel, sensor, real_name):
    return ui.div(ui.h3(f"📱 {real_name}"), ui.div(f"المقاس: {size}"), ui.div(f"الشاشة: {panel}"), ui.div(f"المستشعر: {sensor}"), class_="glass-card")

def draw_neon_section(title, models, color, icon, type_class):
    if not models: return None
    return ui.div(ui.h4(f"{icon} {title}"), *[ui.div(m, class_=f"ammar-flat-card flat-{type_class}") for m in models], class_="glass-card")

# --- الدوال المطلوبة في server.py لحل مشكلة ImportError ---
def draw_plan_2_modal(phone, panels=None, sensors=None):
    return ui.div(ui.h3("خطة 2"), ui.p(f"الموديل: {phone}"), ui.input_text("p2_size", "المقاس"), 
                  ui.input_selectize("p2_panel", "نوع الشاشة", choices=panels or []), 
                  ui.input_selectize("p2_sensor", "المستشعر", choices=sensors or []), 
                  ui.input_action_button("exec_plan2", "بحث"), class_="glass-card")

def draw_plan_3_modal(phone):
    return ui.div(ui.h3("🚨 خطة 3"), ui.p(f"الموديل: {phone}"), ui.input_action_button("btn_close_modal", "إغلاق"), class_="glass-card")

def draw_database_status(total): return ui.div(f"إجمالي الهواتف: {total}", class_="metric-box")
def draw_monitor_component(status): return ui.div(f"حالة المراقب: {status}", class_="metric-box")
def draw_notifications(status): return ui.div(f"المصدر: {status}", class_="metric-box")
def draw_silent_inspector(): return ui.div(ui.input_action_button("btn_run_inspector", "🚀 تشغيل المراقب"), class_="glass-card")
def draw_system_info(): return ui.div(f"📅 {datetime.date.today()}", class_="coord-line")
def draw_drawer_js_handler(): return ui.HTML("")

# --- الواجهة الرئيسية ---
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.div(ui.tags.button("✕", id="btn_close_drawer_trigger"), ui.h3("⚙️ الإعدادات"), 
           ui.output_ui("system_info_area"), ui.output_ui("database_status_area"), 
           id="settings-drawer", class_="drawer"),
    ui.div(
        ui.div(ui.tags.span("ZEGAAR AMMAR", class_="brand-neon-main"), 
               ui.tags.span("GLASS MANAGER", class_="brand-neon-sub"), class_="brand-neon-title"),
        ui.tags.button("⚙️", id="btn_settings", class_="btn-dots-menu"),
        ui.input_text("search_query", "", placeholder=" ابحث عن موديل..."),
        ui.output_ui("welcome_area"), ui.output_ui("results_workflow_view"), ui.output_ui("dynamic_modal_container"),
        class_="container-fluid"
    )
)
