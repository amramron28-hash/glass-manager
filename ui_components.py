from shiny import ui

# =========================
# PWA + STYLES
# =========================

def inject_pwa_and_styles():
    return ui.HTML("""
    <link rel="manifest" href="manifest.json">
    <link rel="stylesheet" href="style.css">

    <style>
        body {
            background-color: #0a0e17;
            color: white;
            direction: rtl;
            font-family: sans-serif;
        }

        #settings-drawer {
            display:none;
            position:fixed;
            right:0;
            top:0;
            width:300px;
            height:100%;
            background:#161b22;
            z-index:9999;
            padding:20px;
            box-shadow: -2px 0 10px #000;
        }

        .modal-content {
            background: #1a1f2e;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #333;
            margin: 20px auto;
            max-width: 500px;
        }

        .tech-coords-card {
            background: #1a1f2e;
            padding: 15px;
            border-radius: 8px;
            border-right: 4px solid #3498db;
            margin-bottom: 15px;
        }

        .neon-section {
            background: #111;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-right: 4px solid;
        }

        .status-card, .monitor-card, .notify-card {
            padding: 10px;
            border: 1px solid #333;
            margin: 5px;
            border-radius: 5px;
        }

        .header {
            display:flex;
            justify-content:space-between;
            align-items:center;
            padding:10px;
            border-bottom:1px solid #333;
        }

        .footer-stats {
            display:flex;
            gap:10px;
            padding:10px;
            background:#111;
        }

        .action-buttons {
            padding:10px;
            display:flex;
            gap:5px;
        }
    </style>
    """)

# =========================
# CORE UI
# =========================

def draw_technical_coords(size, panel, sensor, real_name):
    return ui.div(
        ui.h4(f"📱 {real_name}"),
        ui.p(f"📏 {size or 'غير محدد'} | 🖥 {panel or 'غير محدد'} | 🔍 {sensor or 'غير محدد'}"),
        class_="tech-coords-card"
    )

# =========================
# MODALS (FIXED)
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
# STATUS UI
# =========================

def draw_database_status(total):
    return ui.div(f"📊 قاعدة البيانات: {total}", class_="status-card")

def draw_monitor_component(status):
    return ui.div(
        f"المراقب: {status.get('status', 'OFFLINE') if isinstance(status, dict) else status}",
        class_="monitor-card"
    )

def draw_notifications(status):
    return ui.div("🔔 النظام نشط", class_="notify-card")

# =========================
# APP UI (IMPORTANT FIXES)
# =========================

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),

    # Drawer (settings)
    ui.div(
        ui.h2("🛠 الإعدادات"),
        ui.input_action_button("btn_close_drawer_trigger", "إغلاق"),
        id="settings-drawer"
    ),

    # Header
    ui.div(
        ui.div(
            ui.h1("📱 النظام الذكي"),
            ui.input_action_button("btn_settings", "⚙️"),
            class_="header"
        ),

        ui.input_text("search_query", "", placeholder="🔍 ابحث هنا..."),

        ui.output_ui("suggestions_curtain"),

        # 🔥 FIX 1: لازم يكون موجود للنتائج
        ui.output_ui("results_workflow_view"),

        ui.output_ui("dynamic_modal_container"),

        ui.div(
            ui.output_ui("database_status_area"),
            ui.output_ui("monitor_area"),
            ui.output_ui("notifications_area"),
            class_="footer-stats"
        ),

        ui.div(
            ui.input_action_button("show_add_panel", "➕ لوحة"),
            ui.input_action_button("show_add_sensor", "➕ مستشعر"),
            ui.input_action_button("trigger_plan_2", "📋 خ2"),
            ui.input_action_button("trigger_plan_3", "📋 خ3"),
            class_="action-buttons"
        )
    )
)
