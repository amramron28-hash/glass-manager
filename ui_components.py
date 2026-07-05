from shiny import ui

# =========================
# PWA + STYLES
# =========================

def inject_pwa_and_styles():
    return ui.HTML("""
    <link rel="manifest" href="manifest.json">
    <link rel="stylesheet" href="style.css">
    """)

# =========================
# CORE UI COMPONENTS
# =========================

def draw_technical_coords(size, panel, sensor, real_name):
    return ui.div(
        ui.h4(f"📱 {real_name}", style="margin-bottom: 5px;"),
        ui.p(f"📏 {size or 'غير محدد'} | 🖥 {panel or 'غير محدد'} | 🔍 {sensor or 'غير محدد'}", style="opacity: 0.8;"),
        class_="tech-coords-card"
    )

def draw_neon_section(title, models, color, icon, type_class):
    if not models:
        return None
    return ui.div(
        ui.h4(f"{icon} {title}", style=f"color: {color}; margin-bottom: 10px; font-weight: bold;"),
        *[
            ui.div(m, class_=f"ammar-flat-card flat-{type_class}")
            for m in models
        ],
        class_="neon-section",
        style=f"border-right: 4px solid {color};"
    )

# =========================
# MODALS
# =========================

def draw_settings_modal():
    return ui.div(
        ui.h3("إعدادات النظام"),
        ui.input_action_button("btn_close_modal", "إغلاق"),
        class_="modal-content"
    )

def draw_plan_2_modal(phone, panels, sensors):
    return ui.div(
        ui.h3(f"خطة 2: {phone}"),
        ui.div(f"اللوحات: {len(panels) if panels else 0} | المستشعرات: {len(sensors) if sensors else 0}"),
        ui.input_action_button("btn_close_modal", "إغلاق"),
        class_="modal-content"
    )

def draw_plan_3_modal(phone, res):
    return ui.div(
        ui.h3(f"خطة 3: {phone}"),
        ui.div("تم تحميل بيانات الخطة 3"),
        ui.input_action_button("btn_close_modal", "إغلاق"),
        class_="modal-content"
    )

# =========================
# STATUS UI (Used inside Drawer now)
# =========================

def draw_database_status(total):
    return ui.div(f"📊 قاعدة البيانات: {total}", class_="status-card metric-box")

def draw_monitor_component(status):
    st = status.get('status', 'OFFLINE') if isinstance(status, dict) else status
    return ui.div(f"🛰️ المراقب: {st}", class_="monitor-card metric-box")

def draw_notifications(status):
    src = status.get('source', 'N/A') if isinstance(status, dict) else 'N/A'
    return ui.div(f"🔔 المصدر: {src}", class_="notify-card metric-box")

# =========================
# APP UI (THIS IS THE CRITICAL VARIABLE)
# =========================

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),

    # 1. Drawer (Settings) - Matched with CSS `.drawer` and `.drawer.open`
    ui.div(
        ui.tags.button("✕", class_="drawer-close-btn", id="btn_close_drawer_trigger"),
        ui.h3("🛠 الإعدادات ومراقبة النظام"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        ui.output_ui("notifications_area"),
        id="settings-drawer",
        class_="drawer"
    ),

    # 2. Header Bar
    ui.div(
        ui.div(
            ui.div(
                ui.tags.span("ZEGAAR", class_="brand-neon-main"),
                ui.tags.span("GLASS MANAGER", class_="brand-neon-sub"),
                class_="brand-neon-title"
            ),
            ui.tags.button("⋮", class_="btn-dots-menu", id="btn_settings"),
            class_="header-bar"
        ),

        # 3. Search Box
        ui.div(
            ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."),
            ui.output_ui("suggestions_curtain"),
            class_="search-box"
        ),

        # 4. Main Results Area
        ui.output_ui("results_workflow_view"),
        ui.output_ui("dynamic_modal_container"),

        # 5. Action Buttons
        ui.div(
            ui.input_action_button("show_add_panel", "➕ لوحة"),
            ui.input_action_button("show_add_sensor", "➕ مستشعر"),
            ui.input_action_button("trigger_plan_2", "📋 خ2"),
            ui.input_action_button("trigger_plan_3", "📋 خ3"),
            class_="action-buttons"
        ),
        
        # 6. JS Handler for Drawer toggle
        ui.output_ui("drawer_js_handler")
    )
)
