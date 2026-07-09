from shiny import ui


# ==========================================================
# SETTINGS BUTTON
# ==========================================================

def draw_settings_button():

    return ui.tags.button(
        "⚙",
        id="btn_settings",
        class_="btn-settings-open"
    )


# ==========================================================
# APP BRAND
# ==========================================================

def draw_brand():

    return ui.div(

        ui.div(
            "ZEGAAR AMMAR",
            class_="brand-neon-main"
        ),

        ui.div(
            "GLASS MANAGER",
            class_="brand-neon-sub"
        ),

        class_="brand-wrapper"

    )


# ==========================================================
# MAIN IMAGE
# ==========================================================

def draw_main_image():

    return ui.tags.img(

        src="phone_image.webp",

        alt="Phone",

        class_="main-phone-image"

    )


# ==========================================================
# HEADER
# ==========================================================

def draw_header():

    return ui.div(

        draw_settings_button(),

        draw_brand(),

        class_="main-header"

    )


# ==========================================================
# WELCOME HEADER
# ==========================================================

def draw_welcome_header():

    return ui.div(

        draw_header(),

        draw_main_image(),

        class_="welcome-screen"

    )
