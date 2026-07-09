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
# BRAND
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
# MAIN IMAGE ONLY
# ==========================================================

def draw_main_image():

    return ui.tags.img(

        src="phone_image.webp",

        class_="main-phone-image"

    )


# ==========================================================
# MAIN HEADER
# ==========================================================

def draw_header():

    return ui.div(

        draw_settings_button(),

        draw_brand(),

        class_="main-header"

    )


# ==========================================================
# WELCOME SCREEN
# ==========================================================

def draw_welcome_header():

    return ui.div(

        draw_main_image(),

        class_="welcome-screen"

    )
