from shiny import ui


# ==========================================================
# SYSTEM INFO
# ==========================================================

def draw_system_info():

    return ui.div(

        ui.h4("معلومات النظام"),

        ui.div(
            "ZEGAAR AMMAR GLASS MANAGER"
        ),

        ui.div(
            "Version 2026.07"
        ),

        class_="metric-box glass-card"

    )



# ==========================================================
# DATABASE STATUS
# ==========================================================

def draw_database_status(total):

    return ui.div(

        ui.h4("عدد الهواتف"),

        ui.div(

            str(total),

            class_="metric-value"

        ),

        class_="metric-box glass-card"

    )



# ==========================================================
# SILENT MONITOR
# ==========================================================

def draw_monitor_component(status):

    online = (
        str(status).upper()
        ==
        "ONLINE"
    )


    return ui.div(

        ui.h4("المراقب الصامت"),

        ui.div(

            "🟢 ONLINE"
            if online
            else
            "🔴 OFFLINE",

            class_="metric-value"

        ),

        class_="metric-box glass-card"

    )



# ==========================================================
# INSPECTOR BUTTON
# ==========================================================

def draw_silent_inspector():

    return ui.div(

        ui.input_action_button(

            "btn_run_inspector",

            "🛠 تشغيل الفحص الذكي",

            class_="btn-neon"

        ),

        class_="glass-card"

    )



# ==========================================================
# NOTIFICATIONS
# ==========================================================

def draw_notification_component(count=0):

    return ui.div(

        ui.h4("جرس الإشعارات"),

        ui.div(

            f"🔔 {count}",

            class_="metric-value"

        ),

        class_="metric-box glass-card"

    )



# ==========================================================
# SETTINGS DRAWER
# ==========================================================

def draw_settings_drawer():

    return ui.div(

        ui.div(

            ui.h2("⚙️ الإعدادات"),


            ui.tags.button(

                "✖",

                id="btn_close_drawer_trigger",

                class_="drawer-close-btn"

            ),

            class_="drawer-header"

        ),


        ui.div(

            ui.output_ui(
                "system_info_area"
            ),

            ui.output_ui(
                "database_status_area"
            ),

            ui.output_ui(
                "monitor_area"
            ),

            draw_notification_component(),


            ui.output_ui(
                "silent_inspector_area"
            ),


            class_="drawer-body"

        ),


        id="settings-drawer",

        class_="drawer"

    )
