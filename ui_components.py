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

        ui.tags.script(src="service-worker.js"),

        ui.HTML("""

<script>

if("serviceWorker" in navigator){

window.addEventListener("load",()=>{

navigator.serviceWorker.register("/service-worker.js")

.catch(console.error);

});

}

</script>

""")
    )


# ==========================================================
# DRAWER EVENTS
# ==========================================================

def draw_drawer_js_handler():

    return ui.HTML("""

<script>

$(document).ready(function(){

$(document).on("click","#btn_settings",function(){

$("#settings-drawer").addClass("drawer-open");

});

$(document).on("click","#btn_close_drawer_trigger",function(){

$("#settings-drawer").removeClass("drawer-open");

});

$(document).on("click",".suggestion-row",function(){

let value=$(this).text();

Shiny.setInputValue(
"search_query",
value,
{priority:"event"}
);

});

});

</script>

""")
# ==========================================================
# WELCOME
# ==========================================================

def draw_welcome_section():

    return ui.div(

        ui.tags.img(
            src="phone_image.webp",
            class_="main-phone-image"
        ),

        ui.div(

            "ZEGAAR AMMAR",

            class_="brand-neon-main"

        ),

        ui.div(

            "GLASS MANAGER",

            class_="brand-neon-sub"

        ),

        class_="welcome-screen"

    )


# ==========================================================
# TECHNICAL CARD
# ==========================================================

def draw_technical_coords(coords):

    if not coords:
        return None

    return ui.div(

        ui.h3(
            coords.get("real_name",""),
            class_="phone-title"
        ),

        ui.div(
            f"المقاس : {coords.get('size','-')}",
            class_="coord-line"
        ),

        ui.div(
            f"نوع الشاشة : {coords.get('panel','-')}",
            class_="coord-line"
        ),

        ui.div(
            f"المستشعر : {coords.get('sensor','-')}",
            class_="coord-line"
        ),

        class_="glass-card neon-card"
    )


# ==========================================================
# NEON RESULT CARD
# ==========================================================

def draw_neon_section(title, models, cls):

    if not models:
        return None

    color_map = {

        "exact": "#2ecc71",

        "plus": "#3498db",

        "minus": "#e67e22"

    }

    glow = color_map.get(cls, "#00e5ff")

    return ui.div(

        ui.div(

            title,

            class_="result-title",

            style=f"""

            border-left:4px solid {glow};

            color:{glow};

            """

        ),

        *[

            ui.div(

                model,

                class_="ammar-flat-card",

                style=f"""

                border:1px solid {glow};

                box-shadow:0 0 15px {glow};

                """

            )

            for model in models

        ],

        class_="glass-card neon-container"

    )
# ==========================================================
# SETTINGS DRAWER
# ==========================================================

def draw_system_info():

    return ui.div(

        ui.h4("معلومات النظام"),

        ui.div("ZEGAAR AMMAR GLASS MANAGER"),

        ui.div("Version 2026.07"),

        class_="metric-box glass-card"

    )


def draw_database_status(total):

    return ui.div(

        ui.h4("عدد الهواتف"),

        ui.div(

            str(total),

            class_="metric-value"

        ),

        class_="metric-box glass-card"

    )


def draw_monitor_component(status):

    online = str(status).upper() == "ONLINE"

    return ui.div(

        ui.h4("المراقب الصامت"),

        ui.div(

            "🟢 ONLINE" if online else "🔴 OFFLINE",

            class_="metric-value"

        ),

        class_="metric-box glass-card"

    )


def draw_notification_component(count=0):

    return ui.div(

        ui.h4("جرس الإشعارات"),

        ui.div(

            f"🔔 {count}",

            class_="metric-value"

        ),

        class_="metric-box glass-card"

    )


def draw_silent_inspector():

    return ui.div(

        ui.input_action_button(

            "btn_run_inspector",

            "🛠 تشغيل الفحص الذكي",

            class_="btn-neon"

        ),

        class_="glass-card"

    )


def draw_settings_modal():

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

            ui.output_ui("system_info_area"),

            ui.output_ui("database_status_area"),

            ui.output_ui("monitor_area"),

            draw_notification_component(),

            ui.output_ui("silent_inspector_area"),

            class_="drawer-body"

        ),

        id="settings-drawer",

        class_="drawer"

    )
# ==========================================================
# AUTO COMPLETE
# ==========================================================

def draw_suggestions_curtain(suggestions):

    if not suggestions:
        return None

    return ui.div(

        *[
            ui.div(

                ui.span("📱", class_="suggestion-icon"),

                ui.span(model, class_="suggestion-text"),

                class_="suggestion-row"

            )

            for model in suggestions
        ],

        class_="suggestions-curtain glass-card"

    )


# ==========================================================
# PLAN 2
# ==========================================================

def draw_plan_2_modal(phone="", panels=None, sensors=None):

    panels = panels or []
    sensors = sensors or []

    return draw_modal_overlay(

        ui.div(

            ui.h2("الخطة الثانية"),

            ui.p(f"الهاتف: {phone}"),

            ui.input_select(

                "p2_panel",

                "نوع الشاشة",

                choices=panels

            ),

            ui.input_select(

                "p2_sensor",

                "المستشعر",

                choices=sensors

            ),

            ui.div(

                ui.input_action_button(

                    "btn_plan2_save",

                    "💾 حفظ",

                    class_="btn-neon"

                ),

                ui.input_action_button(

                    "btn_close_modal",

                    "إغلاق",

                    class_="btn-close"

                ),

                class_="modal-buttons"

            ),

            class_="glass-card modal-card"

        )

    )


# ==========================================================
# PLAN 3
# ==========================================================

def draw_plan_3_modal(phone="", result=None):

    return draw_modal_overlay(

        ui.div(

            ui.h2("الخطة الثالثة"),

            ui.p(

                f"لم يتم العثور على نتائج للهاتف: {phone}"

            ),

            ui.input_text(

                "p3_size",

                "المقاس"

            ),

            ui.input_text(

                "p3_panel",

                "نوع الشاشة"

            ),

            ui.input_text(

                "p3_sensor",

                "المستشعر"

            ),

            ui.div(

                ui.input_action_button(

                    "btn_plan3_save",

                    "💾 إضافة",

                    class_="btn-neon"

                ),

                ui.input_action_button(

                    "btn_close_modal",

                    "إغلاق",

                    class_="btn-close"

                ),

                class_="modal-buttons"

            ),

            class_="glass-card modal-card"

        )

    )


# ==========================================================
# MODAL OVERLAY
# ==========================================================

def draw_modal_overlay(inner):

    if inner is None:
        return None

    return ui.div(

        inner,

        class_="modal-overlay"

    )
# ==========================================================
# MAIN UI
# ==========================================================

app_ui = ui.page_fluid(

    inject_styles(),

    draw_drawer_js_handler(),

    # ----------------------------
    # خلفية ثابتة
    # ----------------------------
    ui.div(
        class_="fixed-background"
    ),

    # ----------------------------
    # درج الإعدادات
    # ----------------------------
    draw_settings_modal(),

    # ----------------------------
    # الواجهة الرئيسية
    # ----------------------------
    ui.div(

        # ترس الإعدادات
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

            ui.output_ui("suggestions_curtain"),

            class_="search-box"

        ),

        # شاشة الترحيب
        ui.output_ui("welcome_area"),

        # النتائج
        ui.output_ui("results_workflow_view"),

        # المودالات
        ui.output_ui("dynamic_modal_container"),

        class_="main-layout"

    )

)
