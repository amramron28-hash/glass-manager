from shiny import ui
from html import escape


def draw_settings_button():
    return ui.input_action_button(
        "btn_settings",
        "⋮",
        class_="btn-dots-menu"
    )


def draw_notification_status(
    message="النظام يعمل بكفاءة",
    color="#2ecc71"
):
    return ui.div(
        f"🔔 جرس الإشعارات: {message}",
        class_="metric-box",
        style=f"color:{color};"
    )


def draw_silent_monitor_status(
    status="متصل وقيد التشغيل",
    color="#00bfff"
):
    return ui.div(
        f"🔒 المراقب الصامت: {status}",
        class_="metric-box",
        style=f"color:{color};"
    )


def draw_database_status(total):
    return ui.div(
        ui.div(
            f"📊 قاعدة البيانات: {total} هاتف",
            class_="metric-box"
        )
    )


def draw_maintenance_button():
    return ui.input_action_button(
        "btn_open_maintenance",
        "🛠 مركز الصيانة المتقدم",
        style="""
        width:100%;
        background:#e67e22;
        color:white;
        padding:12px;
        border-radius:10px;
        border:none;
        font-weight:bold;
        margin-top:15px;
        """
    )


def draw_settings_drawer():

    return ui.div(

        ui.tags.button(
            "×",
            id="btn_close_drawer",
            class_="drawer-close-btn",
            onclick="""
            Shiny.setInputValue(
                'btn_close_drawer_trigger',
                Math.random(),
                {priority:'event'}
            );
            """
        ),

        ui.h3(
            "⚙️ الإعدادات العامة",
            style="""
            color:#00bfff;
            text-align:center;
            margin-bottom:25px;
            font-weight:800;
            """
        ),

        ui.output_ui(
            "database_status_area"
        ),

        draw_notification_status(),

        draw_silent_monitor_status(),

        draw_maintenance_button(),
        id="settings_drawer",
        class_="drawer"
    )


def draw_settings_panel():

    return [

        ui.div(

            ui.div(
                "ZEGAAR AMMAR",
                class_="brand-neon-main"
            ),

            ui.div(
                "GLASS MANAGER",
                class_="brand-neon-sub"
            ),

            class_="brand-neon-title"

        ),

        draw_settings_button(),

        draw_settings_drawer()

    ]


def init_settings_server(
    input,
    output,
    session,
    database_data
):

    from shiny import reactive, render

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer():

        await session.send_custom_message(
            "toggle_drawer",
            "open"
        )


    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def close_drawer():

        await session.send_custom_message(
            "toggle_drawer",
            "close"
        )


    @render.ui
    def database_status_area():

        db = database_data()

        total = 0

        for size, panels in db.items():

            for panel, sensors in panels.items():

                for sensor, data in sensors.items():

                    if isinstance(data, dict):

                        total += len(
                            data.get(
                                "models",
                                []
                            )
                        )

        return draw_database_status(
            total
        )
        id="settings_drawer",
        class_="drawer"
    )


def draw_settings_panel():

    return [

        ui.div(

            ui.div(
                "ZEGAAR AMMAR",
                class_="brand-neon-main"
            ),

            ui.div(
                "GLASS MANAGER",
                class_="brand-neon-sub"
            ),

            class_="brand-neon-title"

        ),

        draw_settings_button(),

        draw_settings_drawer()

    ]


def init_settings_server(
    input,
    output,
    session,
    database_data
):

    from shiny import reactive, render

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer():

        await session.send_custom_message(
            "toggle_drawer",
            "open"
        )


    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def close_drawer():

        await session.send_custom_message(
            "toggle_drawer",
            "close"
        )


    @render.ui
    def database_status_area():

        db = database_data()

        total = 0

        for size, panels in db.items():

            for panel, sensors in panels.items():

                for sensor, data in sensors.items():

                    if isinstance(data, dict):

                        total += len(
                            data.get(
                                "models",
                                []
                            )
                        )

        return draw_database_status(
            total
    )
# ===========================
# نهاية ملف settings_panel.py
# ===========================

__all__ = [

    "draw_settings_button",

    "draw_settings_drawer",

    "draw_settings_panel",

    "draw_database_status",

    "draw_notification_status",

    "draw_silent_monitor_status",

    "draw_maintenance_button",

    "init_settings_server"

]
