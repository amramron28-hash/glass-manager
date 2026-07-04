from shiny import ui

def inject_pwa_and_styles():
    return ui.HTML("""
    <link rel="manifest" href="manifest.json">
    <link rel="stylesheet" href="style.css">
    <style>
        body { background-color: #0a0e17; color: white; direction: rtl; font-family: sans-serif; }
        #settings-drawer { display:none; position:fixed; right:0; top:0; width:300px; height:100%; background:#161b22; z-index:9999; padding:20px; box-shadow: -2px 0 10px #000; }
        .modal-content { background: #1a1f2e; padding: 25px; border-radius: 12px; border: 1px solid #333; margin: 20px auto; max-width: 500px; }
        .tech-coords-card { background: #1a1f2e; padding: 15px; border-radius: 8px; border-right: 4px solid #3498db; margin-bottom: 15px; }
        .neon-section { background: #111; padding: 15px; margin: 10px 0; border-radius: 8px; border-right: 4px solid; }
        .status-card, .monitor-card, .notify-card { padding: 10px; border: 1px solid #333; margin: 5px; border-radius: 5px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #333; }
        .footer-stats { display: flex; gap: 10px; padding: 10px; background: #111; }
        .action-buttons { padding: 10px; display: flex; gap: 5px; }
        .alert-warning { color: #e74c3c; padding: 15px; background: #2a1111; border-radius: 5px; }
    </style>
    <script>
        Shiny.addCustomMessageHandler('toggle_drawer', function(action) {
            const el = document.getElementById('settings-drawer');
            if(el) el.style.display = (action === 'open') ? 'block' : 'none';
        });
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('service-worker.js');
        }
    </script>
    """)

# --- المكونات الفنية (الرسم) ---
def draw_technical_coords(size, panel, sensor, real_name):
    return ui.div(
        ui.h4(f"📱 الموديل: {real_name}"),
        ui.p(f"📏 المقاس: {size or 'غير محدد'} | 🖥 الشاشة: {panel or 'غير محدد'} | 🔍 الحساس: {sensor or 'غير محدد'}"),
        class_="tech-coords-card"
    )

def draw_neon_section(title, models_list, color, emoji, section_id):
    if not models_list: return ui.div(ui.p(f"{title}: لا توجد نتائج."), class_="neon-section", style=f"border-right: 4px solid {color};")
    return ui.div(ui.h5(f"{emoji} {title}"), ui.tags.ul(*[ui.tags.li(m) for m in models_list]), class_="neon-section", style=f"border-right: 4px solid {color};")

def draw_warning_card(message):
    return ui.div(message, class_="alert alert-warning")

# --- النوافذ المنبثقة (Modal Content) ---
def draw_plan_2_modal(phone, panels, sensors):
    p_count = len(panels) if isinstance(panels, (dict, list)) else 0
    s_count = len(sensors) if isinstance(sensors, (dict, list)) else 0
    return ui.div(ui.h3(f"خطة 2: {phone}"), ui.div(f"اللوحات: {p_count} | المستشعرات: {s_count}"), ui.input_action_button("btn_cancel_add", "إغلاق"), class_="modal-content")

def draw_plan_3_modal(phone, panels, sensors):
    return ui.div(ui.h3(f"خطة 3: {phone}"), ui.div("بيانات الخطة 3 متاحة."), ui.input_action_button("btn_cancel_add", "إغلاق"), class_="modal-content")

def build_add_panel_modal():
    return ui.div(ui.h4("إضافة لوحة"), ui.input_text("new_panel_name", "اسم اللوحة"), ui.input_action_button("btn_confirm_add_panel", "تأكيد"), ui.input_action_button("btn_cancel_add", "إلغاء"), class_="modal-content")

def build_add_sensor_modal():
    return ui.div(ui.h4("إضافة مستشعر"), ui.input_text("new_sensor_name", "اسم المستشعر"), ui.input_action_button("btn_confirm_add_sensor", "تأكيد"), ui.input_action_button("btn_cancel_add", "إلغاء"), class_="modal-content")

# --- المكونات الأخرى ---
def draw_database_status(total): return ui.div(f"📊 القاعدة: {total} جهاز", class_="status-card")
def draw_monitor_component(status): return ui.div(f"المراقب: {status.get('status', 'OFFLINE') if isinstance(status, dict) else status}", class_="monitor-card")
def draw_notifications(status): return ui.div("🔔 الإشعارات نشطة", class_="notify-card")

# --- الهيكل العام ---
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.div(ui.h2("🛠 الإعدادات"), ui.input_action_button("btn_close_drawer_trigger", "إغلاق"), id="settings-drawer"),
    ui.div(
        ui.div(ui.h1("📱 النظام الذكي"), ui.input_action_button("btn_settings", "⚙️"), class_="header"),
        ui.input_text("search_query", "", placeholder="🔍 ابحث هنا..."),
        ui.output_ui("suggestions_curtain"),
        ui.output_ui("results_workflow_view"),
        ui.output_ui("dynamic_modal_container"),
        ui.div(ui.output_ui("database_status_area"), ui.output_ui("monitor_area"), ui.output_ui("notifications_area"), class_="footer-stats"),
        ui.div(ui.input_action_button("show_add_panel", "➕ لوحة"), ui.input_action_button("show_add_sensor", "➕ مستشعر"), ui.input_action_button("trigger_plan_2", "📋 خ2"), ui.input_action_button("trigger_plan_3", "📋 خ3"), class_="action-buttons")
    )
)
