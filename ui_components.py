from shiny import ui
import datetime

def inject_pwa_and_styles():
    # نستخدم style_v2.css لتجنب الكاش
    return ui.HTML("""
    <link rel="manifest" href="/manifest.json">
    <link rel="stylesheet" href="/style_v2.css">
    """)

def draw_welcome_section(image_src: str = "phone_image.webp"):
    return ui.div(
        ui.tags.img(
            src=image_src,
            alt="Phone Interface",
            class_="welcome-phone-image"
        ),
        class_="glass-card welcome-image-card"
    )

def draw_technical_coords(size: str, panel: str, sensor: str, real_name: str):
    return ui.div(
        ui.h3(f"📱 {real_name}", class_="tech-title"),
        ui.div(f" المقاس : {size if size else '-'}", class_="coord-line"),
        ui.div(f"📺 الشاشة : {panel if panel else '-'}", class_="coord-line"),
        ui.div(f"🔧 المستشعر : {sensor if sensor else '-'}", class_="coord-line"),
        class_="glass-card tech-card"
    )

def draw_neon_section(title: str, models: list = None, color: str = "#3498db", icon: str = "", type_class: str = "default"):
    if not models: return None
    return ui.div(
        ui.h4(f"{icon} {title}", class_="neon-section-title", style=f"color:{color};"),
        *[ui.div(model, class_=f"ammar-flat-card flat-{type_class}") for model in models],
        class_="glass-card neon-section",
        style=f"border-right:4px solid {color};"
    )

def draw_plan_2_modal(phone: str, panels: list = None, sensors: list = None):
    return ui.div(
        ui.h3(" خطة 2"),
        ui.p(f"الموديل: {phone}", style="font-weight:bold;"),
        ui.input_text("p2_size", "المقاس"),
        ui.input_selectize("p2_panel", "نوع الشاشة", choices=panels or []),
        ui.input_selectize("p2_sensor", "المستشعر", choices=sensors or []),
        ui.input_action_button("exec_plan2", "🔍 بحث", class_="btn-neon"),
        class_="glass-card modal-content"
    )

def draw_plan_3_modal(phone: str):
    return ui.div(
        ui.h3("🚨 خطة 3"),
        ui.p(f"الموديل: {phone}"),
        ui.p("لم يتم العثور على مجموعة مطابقة."),
        ui.input_action_button("btn_close_modal", "إغلاق", class_="btn-neon"),
        class_="glass-card modal-content"
    )

# الدوال الأخرى (Status & Inspector) تبقى كما هي في ملفك الأصلي
def draw_database_status(total: int): return ui.div(ui.div(" إجمالي الهواتف", class_="metric-title"), ui.div(str(total), class_="metric-value"), class_="metric-box")
def draw_monitor_component(status): return ui.div(ui.div("🛰️ حالة المراقب", class_="metric-title"), ui.div(status, class_="metric-value"), class_="metric-box")
def draw_notifications(status): return ui.div(ui.div(" مصدر البيانات", class_="metric-title"), ui.div("Supabase", class_="metric-value"), class_="metric-box")
def draw_silent_inspector(): return ui.div(ui.h4("🧹 المراقب الصامت"), ui.input_action_button("btn_run_inspector", "🚀 تشغيل", class_="btn-neon"), class_="glass-card metric-box")
def draw_system_info(): return ui.div(ui.div(f"📅 اليوم: {datetime.date.today()}", class_="coord-line"), class_="glass-card metric-box")
def draw_drawer_js_handler(): return ui.HTML("<script>/* كود الـ JS الخاص بك */</script>")

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.div(ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"), id="settings-drawer", class_="drawer"),
    ui.div(
        ui.div(
            ui.div(
                ui.tags.span("ZEGAAR AMMAR", class_="brand-neon-main"),
                ui.tags.span("GLASS MANAGER", class_="brand-neon-sub"),
                class_="brand-neon-title"
            ),
            ui.tags.button("⋮", id="btn_settings", class_="btn-dots-menu"),
            class_="header-bar"
        ),
        ui.output_ui("welcome_area"),
        ui.output_ui("results_workflow_view"),
        ui.output_ui("dynamic_modal_container"),
        class_="container-fluid"
    )
)
