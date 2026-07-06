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
# WELCOME SECTION (صورة فقط بدون نصوص)
# ==========================================================
def draw_welcome_section():
    return ui.div(
        ui.tags.img(
            src="/phone_image.webp",
            alt="Phone Interface",
            style="width: 100%; max-width: 300px; height: auto; display: block; margin: 0 auto; border-radius: var(--radius-lg);"
        ),
        class_="glass-card welcome-image-card"
    )


# ==========================================================
# TECHNICAL CARD
# ==========================================================
def draw_technical_coords(size, panel, sensor, real_name):
    return ui.div(
        ui.h3(f"📱 {real_name}", style="margin-bottom:10px;"),
        ui.div(f"📏 المقاس : {size if size else '-'}", class_="coord-line"),
        ui.div(f"🖥 الشاشة : {panel if panel else '-'}", class_="coord-line"),
        ui.div(f"🔍 المستشعر : {sensor if sensor else '-'}", class_="coord-line"),
        class_="glass-card tech-card"
    )


# ==========================================================
# COMPATIBLE SECTION
# ==========================================================
def draw_neon_section(title, models, color, icon="", type_class="default"):
    if not models:
        return None
    return ui.div(
        ui.h4(f"{icon} {title}", style=f"color:{color}; margin-bottom:12px;"),
        *[ui.div(model, class_=f"ammar-flat-card flat-{type_class}") for model in models],
        class_="glass-card neon-section",
        style=f"border-right:4px solid {color}; margin-top:15px;"
    )


# ==========================================================
# STATUS COMPONENTS (للـ Drawer فقط)
# ==========================================================
def draw_database_status(total):
    return ui.div(
        ui.div("📊 عدد الموديلات", class_="metric-title"),
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
    
    # 1. DRAWER (يحتوي على البطاقات فقط)
    ui.div(
        ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"),
        ui.h3("⚙️ الإعدادات"),
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
            ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."),
            ui.output_ui("suggestions_curtain"),
            class_="search-box"
        ),
        
        # Welcome Area
        ui.output_ui("welcome_area"),
        
        # Results
        ui.output_ui("results_workflow_view"),
        
        # Dynamic Modal
        ui.output_ui("dynamic_modal_container"),
        
        # ⚠️ تم حذف Action Buttons بالكامل
        
        class_="main-container"
    ),
    
    # 3. Drawer JS
    ui.output_ui("drawer_js_handler")
)
