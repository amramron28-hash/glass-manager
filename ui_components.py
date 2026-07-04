from shiny import ui

# --- الدوال الأساسية للواجهة ---
def inject_pwa_and_styles():
    return ui.HTML("""
    <link rel="stylesheet" href="style.css">
    <script>
        Shiny.addCustomMessageHandler('toggle_drawer', function(action) {
            const drawer = document.getElementById('settings-drawer');
            if(drawer) drawer.style.display = (action === 'open') ? 'block' : 'none';
        });
    </script>
    """)

# --- دوال العرض (مربوطة بـ server.py) ---
def draw_database_status(total):
    return ui.div(f"📊 إجمالي الهواتف: {total}", class_="status-card")

def draw_monitor_component(status_data):
    return ui.div(f"الحالة: {status_data.get('status', 'OFFLINE')}", class_="monitor-card")

def draw_notifications(status_data):
    return ui.div("🔔 التنبيهات نشطة", class_="notify-card")

# --- النوافذ المنبثقة (النسخة المتوافقة) ---
def draw_plan_2_modal(phone, panels, sensors):
    return ui.div(
        ui.h3(f"إعدادات الخطة 2 - {phone}"),
        ui.div(f"العناصر: {len(panels)} لوحات، {len(sensors)} مستشعرات"),
        ui.input_action_button("btn_cancel_add", "إغلاق"),
        class_="modal-content"
    )

def draw_plan_3_modal(phone, panels, sensors):
    return ui.div(
        ui.h3(f"إعدادات الخطة 3 - {phone}"),
        ui.input_action_button("btn_cancel_add", "إغلاق"),
        class_="modal-content"
    )

def build_add_panel_modal():
    return ui.div(
        ui.h4("إضافة لوحة"),
        ui.input_text("new_panel_name", "اسم اللوحة"),
        ui.input_action_button("btn_confirm_add_panel", "حفظ"),
        ui.input_action_button("btn_cancel_add", "إلغاء"),
        class_="modal-content"
    )

def build_add_sensor_modal():
    return ui.div(
        ui.h4("إضافة مستشعر"),
        ui.input_text("new_sensor_name", "اسم المستشعر"),
        ui.input_action_button("btn_confirm_add_sensor", "حفظ"),
        ui.input_action_button("btn_cancel_add", "إلغاء"),
        class_="modal-content"
    )

# --- الواجهة الرئيسية (نقطة الدخول لـ app.py) ---
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    # الإعدادات
    ui.div(
        ui.h3("الإعدادات"),
        ui.input_action_button("btn_close_drawer_trigger", "إغلاق"),
        id="settings-drawer", 
        style="display:none; position:fixed; right:0; top:0; width:300px; height:100%; background:#1a1f2e; z-index:9999; padding:20px;"
    ),
    # المحتوى
    ui.div(
        ui.input_action_button("btn_settings", "⚙️"),
        ui.input_text("search_query", "", placeholder="بحث..."),
        ui.output_ui("suggestions_curtain"),
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
        ),
        class_="main-content"
    )
)
