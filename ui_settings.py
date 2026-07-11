from shiny import ui

print("USING ui_settings.py:", __file__)

# ==========================================================
# SETTINGS DRAWER
# ==========================================================

def draw_settings_drawer():

    return ui.div(

        ui.div(

            ui.div(

                ui.span("⚙️", class_="drawer-icon"),

                ui.span("الإعدادات", class_="drawer-title"),

                class_="drawer-title-row",

            ),

            ui.tags.button(

                "✕",

                id="btn_close_drawer_trigger",

                class_="drawer-close-btn",

                title="إغلاق",

            ),

            class_="drawer-header",

        ),

        ui.div(

            ui.output_ui("system_info_area"),

            ui.output_ui("database_status_area"),

            ui.output_ui("monitor_area"),

            ui.output_ui("notification_area"),

            ui.output_ui("silent_inspector_area"),

            class_="drawer-body",

        ),

        id="settings-drawer",

        class_="drawer",

    )


# ==========================================================
# SYSTEM INFO
# ==========================================================

def draw_system_info():

    return ui.div(

        ui.h4("معلومات النظام"),

        ui.div("ZEGAAR AMMAR GLASS MANAGER"),

        ui.div("Version 2026.07"),

        class_="metric-box glass-card",

    )


# ==========================================================
# DATABASE STATUS
# ==========================================================

def draw_database_status(count):

    return ui.div(

        ui.h4("عدد الهواتف"),

        ui.div(str(count), class_="metric-value"),

        class_="metric-box glass-card",

    )


# ==========================================================
# MONITOR
# ==========================================================

def draw_monitor_component(status):

    online = str(status).upper() == "ONLINE"

    return ui.div(

        ui.h4("المراقب الصامت"),

        ui.div(

            "🟢 ONLINE" if online else "🔴 OFFLINE",

            class_="metric-value",

        ),

        class_="metric-box glass-card",

    )


# ==========================================================
# NOTIFICATIONS
# ==========================================================

def draw_notification_component(count=0):

    return ui.div(

        ui.h4("الإشعارات"),

        ui.div(

            f"🔔 {count}",

            class_="metric-value",

        ),

        class_="metric-box glass-card",

    )


# ==========================================================
# SILENT INSPECTOR
# ==========================================================

def draw_silent_inspector():

    return ui.div(

        ui.input_action_button(

            "btn_run_inspector",

            "🛠 تشغيل الفحص الذكي",

            class_="btn-neon",

        ),

        class_="glass-card",

    )


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "draw_settings_drawer",

    "draw_system_info",

    "draw_database_status",

    "draw_monitor_component",

    "draw_notification_component",

    "draw_silent_inspector",

]
