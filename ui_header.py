from shiny import ui

def draw_settings_button():
    return ui.tags.button("⚙", id="btn_settings", class_="btn-settings-open")

def draw_brand():
    return ui.div(
        ui.div("ZEGAAR AMMAR", class_="brand-neon-main"),
        ui.div("GLASS MANAGER", class_="brand-neon-sub"),
        class_="brand-wrapper"
    )

def draw_header():
    return ui.div(
        draw_settings_button(),
        draw_brand(),
        class_="main-header"
    )

def draw_welcome_header():
    # لاحظ: لا نستدعي draw_header هنا لتجنب التكرار
    return ui.div(
        ui.tags.img(src="phone_image.webp", alt="Phone", class_="main-phone-image"),
        class_="welcome-screen"
    )
