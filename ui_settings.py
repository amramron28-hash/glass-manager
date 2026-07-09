from shiny import ui

# ==========================================================
# SETTINGS DRAWER (مصحح 100% مع كافة الدوال المطلوبة)
# ==========================================================

def draw_settings_drawer():
    return ui.div(
        ui.div(
            ui.div(
                ui.span("⚙", class_="drawer-icon"),
                ui.span("الإعدادات", class_="drawer-title"),
                class_="drawer-title-row"
            ),
            # الزر المصحح مع الـ ID المطلوب للإغلاق
            ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"),
            class_="drawer-header"
        ),
        ui.div(
            ui.output_ui("system_info_area"),
            ui.output_ui("database_status_area"),
            ui.output_ui("monitor_area"),
            ui.output_ui("silent_inspector_area"),
            class_="drawer-body"
        ),
        id="settings-drawer",
        class_="drawer"
    )

# ==========================================================
# المكونات الفرعية (المطلوبة للـ server.py)
# ==========================================================

def draw_system_info():
    return ui.div("نظام Glass Manager - v2.0", class_="setting-item-text")

def draw_database_status(count):
    return ui.div(f"قاعدة البيانات: {count} هاتف مسجل", class_="setting-item-text")

def draw_monitor_component(status):
    return ui.div(f"الحالة: {status}", class_="setting-item-text")

def draw_silent_inspector():
    return ui.div(
        ui.tags.button("تشغيل الفحص", id="btn_run_inspector", class_="btn-run-inspector"),
        class_="setting-item-action"
    )

def draw_notification_component():
    return ui.div("الإشعارات مفعلة", class_="setting-item-text")
