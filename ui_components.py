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
# ==========================================================
# NEON RESULT SECTION
# ==========================================================

def draw_neon_section(
    title,
    models,
    color,
    icon,
    phone=""
):

    if not models:
        return None

    return ui.div(

        # عنوان القسم
        ui.div(

            ui.span(
                icon,
                class_="result-icon"
            ),

            ui.span(
                title,
                class_="result-title-text"
            ),

            class_="result-title",

            style=f"""
                border-right:5px solid {color};
                color:{color};
                box-shadow:0 0 18px {color};
            """

        ),

        # بطاقات الهواتف
        *[

            ui.div(

                # الكرة المضيئة
                ui.div(

                    class_="result-orb",

                    style=f"""
                        background:{color};
                        box-shadow:
                            0 0 12px {color},
                            0 0 28px {color};
                    """

                ),

                # اسم الهاتف فقط
                ui.div(

                    model,

                    class_="model-name"

                ),

                class_="ammar-flat-card glass-result-card",

                style=f"""
                    border-right:6px solid {color};
                """

            )

            for model in models

        ],

        class_="glass-card neon-container"

    )
# ==========================================================
# DRAWER + AUTOCOMPLETE EVENTS
# ==========================================================

def draw_drawer_js_handler():

    return ui.HTML("""

<script>

document.addEventListener("DOMContentLoaded",function(){

    //==============================
    // Settings Drawer
    //==============================

    document.addEventListener("click",function(e){

        if(e.target.id==="btn_settings"){

            document
                .getElementById("settings-drawer")
                ?.classList.add("drawer-open");

        }

        if(e.target.id==="btn_close_drawer_trigger"){

            document
                .getElementById("settings-drawer")
                ?.classList.remove("drawer-open");

        }

    });


    //==============================
    // Auto Complete
    //==============================

    document.addEventListener("click",function(e){

        const row=e.target.closest(".suggestion-row");

        if(!row) return;

        const value=row.dataset.value;

        const input=document.getElementById("search_query");

        if(input){

            input.value=value;

            input.dispatchEvent(
                new Event(
                    "input",
                    {bubbles:true}
                )
            );

        }

        const curtain=document.querySelector(".suggestions-curtain");

        if(curtain){

            curtain.style.display="none";

        }

    });

});

</script>

""")
# ==========================================================
# AUTO COMPLETE CURTAIN
# ==========================================================

def draw_suggestions_curtain(suggestions):

    if not suggestions:
        return None

    return ui.div(

        *[

            ui.div(

                ui.div(

                    "📱",

                    class_="suggestion-icon"

                ),

                ui.div(

                    model,

                    class_="suggestion-text"

                ),

                class_="suggestion-row",

                **{"data-value": model}

            )

            for model in suggestions

        ],

        class_="suggestions-curtain glass-card"

                  )
# ==========================================================
# HEAD
# ==========================================================

def inject_styles():

    return ui.tags.head(

        ui.tags.meta(
            charset="utf-8"
        ),

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

        ui.HTML("""

<script>

if("serviceWorker" in navigator){

window.addEventListener("load",function(){

navigator.serviceWorker
.register("/service-worker.js")
.catch(function(err){

console.log(err);

});

});

}

</script>

""")

    )
# ==========================================================
# MAIN UI
# ==========================================================

app_ui = ui.page_fluid(

    inject_styles(),

    draw_drawer_js_handler(),

    # ==========================
    # الخلفية الثابتة
    # ==========================
    ui.div(
        class_="fixed-background"
    ),

    # ==========================
    # درج الإعدادات
    # ==========================
    draw_settings_modal(),

    # ==========================
    # الواجهة الرئيسية
    # ==========================
    ui.div(

        # زر الإعدادات
        ui.tags.button(
            "⚙",
            id="btn_settings",
            class_="btn-settings-open"
        ),

        # شعار التطبيق
        ui.div(

            ui.div(
                "ZEGAAR AMMAR",
                class_="brand-neon-main"
            ),

            ui.div(
                "GLASS MANAGER",
                class_="brand-neon-sub"
            ),

            class_="brand-wrapper"

        ),

        # مربع البحث
        ui.div(

            ui.input_text(
                "search_query",
                "",
                placeholder="ابحث عن موديل الهاتف..."
            ),

            ui.output_ui(
                "suggestions_curtain"
            ),

            class_="search-box"

        ),

        # شاشة البداية
        ui.output_ui(
            "welcome_area"
        ),

        # النتائج
        ui.output_ui(
            "results_workflow_view"
        ),

        # النوافذ المنبثقة
        ui.output_ui(
            "dynamic_modal_container"
        ),

        class_="main-layout"

    )

)
