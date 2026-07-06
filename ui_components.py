from shiny import ui

# ==========================================================
# PWA + GLOBAL STYLES
# ==========================================================
def inject_pwa_and_styles():
    return ui.HTML("""
    <link rel="manifest" href="/manifest.json">
    <link rel="stylesheet" href="/style.css">
    """)


# ==========================================================
# WELCOME SECTION (صورة الهاتف فقط - بدون نصوص)
# ==========================================================
def draw_welcome_section(image_src: str = "/phone_image.webp"):
    """تظهر صورة الهاتف فقط عند عدم وجود نتائج بحث"""
    return ui.div(
        ui.tags.img(
            src=image_src,
            alt="Phone Interface",
            class_="welcome-phone-image"
        ),
        class_="glass-card welcome-image-card"
    )


# ==========================================================
# TECHNICAL CARD
# ==========================================================
def draw_technical_coords(size: str, panel: str, sensor: str, real_name: str):
    return ui.div(
        ui.h3(f"📱 {real_name}", class_="tech-title"),
        ui.div(f"📏 المقاس : {size if size else '-'}", class_="coord-line"),
        ui.div(f" الشاشة : {panel if panel else '-'}", class_="coord-line"),
        ui.div(f" المستشعر : {sensor if sensor else '-'}", class_="coord-line"),
        class_="glass-card tech-card"
    )


# ==========================================================
# COMPATIBLE SECTION
# ==========================================================
def draw_neon_section(title: str, models: list = None, color: str = "#3498db", icon: str = "", type_class: str = "default"):
    if not models:
        return None
    return ui.div(
        ui.h4(f"{icon} {title}", class_="neon-section-title", style=f"color:{color};"),
        *[ui.div(model, class_=f"ammar-flat-card flat-{type_class}") for model in models],
        class_="glass-card neon-section",
        style=f"border-right:4px solid {color};"
    )


# ==========================================================
# SETTINGS / PLAN MODALS
# ==========================================================
def draw_settings_modal():
    return ui.div(
        ui.h3("⚙️ إعدادات النظام"),
        ui.p("يمكن إدارة إعدادات التطبيق من هذه النافذة."),
        ui.input_action_button("btn_close_modal", "إغلاق", class_="btn-neon"),
        class_="glass-card modal-content"
    )


def draw_plan_2_modal(phone: str, panels: list = None, sensors: list = None):
    # ✅ تحويل إلى قائمة صريحة لضمان التوافق مع Shiny
    panels_list = sorted(list(panels)) if panels else []
    sensors_list = sorted(list(sensors)) if sensors else []
    
    return ui.div(
        ui.h3("📋 خطة 2"),
        ui.p(f"الموديل: {phone}", style="font-weight:bold;"),
        ui.input_text("p2_size", "المقاس"),
        ui.input_selectize("p2_panel", "نوع الشاشة", choices=panels_list),
        ui.input_selectize("p2_sensor", "المستشعر", choices=sensors_list),
        ui.input_action_button("exec_plan2", "🔍 بحث", class_="btn-neon"),
        class_="glass-card modal-content"
    )


def draw_plan_3_modal(phone: str):
    # ✅ حذف المعامل غير المستخدم result=None
    return ui.div(
        ui.h3("🚨 خطة 3"),
        ui.p(f"الموديل: {phone}"),
        ui.p("لم يتم العثور على مجموعة مطابقة."),
        ui.input_action_button("btn_close_modal", "إغلاق", class_="btn-neon"),
        class_="glass-card modal-content"
    )


# ==========================================================
# STATUS COMPONENTS
# ==========================================================
def draw_database_status(total: int):
    return ui.div(
        ui.div(" عدد الموديلات", class_="metric-title"),
        ui.div(str(total), class_="metric-value"),
        class_="metric-box"
    )


def draw_monitor_component(status):
    st = status.get("status", "OFFLINE") if isinstance(status, dict) else str(status)
    return ui.div(
        ui.div("🛰️ حالة المراقب", class_="metric-title"),
        ui.div(st, class_="metric-value"),
        class_="metric-box"
    )


def draw_notifications(status):
    src = status.get("source", "N/A") if isinstance(status, dict) else "N/A"
    return ui.div(
        ui.div("🔔 مصدر البيانات", class_="metric-title"),
        ui.div(src, class_="metric-value"),
        class_="metric-box"
    )


# ==========================================================
# MAIN APP UI
# ==========================================================
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    
    # 1. DRAWER
    ui.div(
        ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"),
        ui.h3("🛠 الإعدادات"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        ui.output_ui("notifications_area"),
        id="settings-drawer",
        class_="drawer"
    ),
    
    # 2. MAIN PAGE
    ui.div(
        # Header
        ui.div(
            ui.div(
                ui.tags.span("ZEGAAR", class_="brand-neon-main"),
                ui.tags.span("GLASS MANAGER", class_="brand-neon-sub"),
                class_="brand-neon-title"
            ),
            ui.tags.button("⋮", id="btn_settings", class_="btn-dots-menu"),
            class_="header-bar"
        ),
        
        # Search
        ui.div(
            ui.input_text("search_query", "", placeholder=" ابحث عن موديل الهاتف..."),
            ui.output_ui("suggestions_curtain"),
            class_="search-box"
        ),
        
        # Welcome Area
        ui.output_ui("welcome_area"),
        
        # Results
        ui.output_ui("results_workflow_view"),
        
        # Dynamic Modal
        ui.output_ui("dynamic_modal_container"),
        
        # ️ تم حذف ACTION BUTTONS نهائياً
        
        class_="container-fluid"
    ),
    
    # 3. Drawer JS Handler
    ui.output_ui("drawer_js_handler")
)
