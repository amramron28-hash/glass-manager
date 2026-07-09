from shiny import ui

# ==========================================================
# HEAD
# ==========================================================

def inject_styles():

    return ui.tags.head(

        ui.tags.meta(charset="utf-8"),

        ui.tags.meta(
            name="viewport",
            content="width=device-width, initial-scale=1"
        ),

        ui.tags.link(
            rel="stylesheet",
            href="style_v2.css"
        ),

        ui.tags.link(
            rel="manifest",
            href="manifest.json"
        ),

        ui.tags.script(
            src="https://code.jquery.com/jquery-3.7.1.min.js"
        ),

        ui.HTML("""

<script>

if ("serviceWorker" in navigator) {

    window.addEventListener("load", function () {

        navigator.serviceWorker
            .register("/service-worker.js")
            .catch(console.error);

    });

}

$(document).ready(function(){

    // فتح درج الإعدادات
    $(document).on("click","#btn_settings",function(){

        $("#settings-drawer").addClass("drawer-open");

    });

    // إغلاق درج الإعدادات
    $(document).on("click","#btn_close_drawer_trigger",function(){

        $("#settings-drawer").removeClass("drawer-open");

    });

    // اختيار اقتراح من الستارة
    $(document).on("click",".suggestion-row",function(){

        let value = $(this).data("model");

        $("#search_query").val(value);

        Shiny.setInputValue(
            "search_query",
            value,
            {priority:"event"}
        );

        $(".suggestions-curtain").hide();

    });

});

</script>

""")
    )
# ==========================================================
# SETTINGS BUTTON
# ==========================================================

def draw_settings_button():

    return ui.tags.button(

        "⚙️",

        id="btn_settings",

        class_="btn-settings-open",

        title="الإعدادات"

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
# MAIN IMAGE
# ==========================================================

def draw_main_image():

    return ui.tags.img(

        src="phone_image.webp",

        class_="main-phone-image",

        loading="lazy"

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
# WELCOME SCREEN
# ==========================================================

def draw_welcome_section():

    return ui.div(

        draw_main_image(),

        class_="welcome-screen"

    )


# للحفاظ على التوافق مع server.py

draw_welcome_header = draw_welcome_section
# ==========================================================
# TECHNICAL CARD
# ==========================================================

def draw_technical_coords(coords):

    if not coords:
        return None

    return ui.div(

        ui.div(

            "📱 " + coords.get("real_name", ""),

            class_="phone-title"

        ),

        ui.div(

            ui.span("📐 "),
            ui.span(coords.get("size", "-")),

            class_="coord-line"

        ),

        ui.div(

            ui.span("🖥 "),
            ui.span(coords.get("panel", "-")),

            class_="coord-line"

        ),

        ui.div(

            ui.span("📡 "),
            ui.span(coords.get("sensor", "-")),

            class_="coord-line"

        ),

        class_="glass-card phone-card"

    )
