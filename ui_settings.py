from shiny import ui

def draw_settings_drawer():
    return ui.div(
        ui.div(
            ui.div(
                ui.span("⚙", class_="drawer-icon"),
                ui.span("الإعدادات", class_="drawer-title"),
                class_="drawer-title-row"
            ),
            # الزر المصحح مع الـ ID المطلوب
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
