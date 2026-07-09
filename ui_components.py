from shiny import ui

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
# DRAWER + AUTOCOMPLETE EVENTS
# ==========================================================

def draw_drawer_js_handler():

    return ui.HTML("""

<script>

document.addEventListener("DOMContentLoaded", function () {

    // ==========================
    // فتح وإغلاق درج الإعدادات
    // ==========================

    document.addEventListener("click", function (e) {

        if (e.target.id === "btn_settings") {

            document
                .getElementById("settings-drawer")
                ?.classList.add("drawer-open");

        }

        if (e.target.id === "btn_close_drawer_trigger") {

            document
                .getElementById("settings-drawer")
                ?.classList.remove("drawer-open");

        }

    });

    // ==========================
    // اختيار عنصر من الاقتراحات
    // ==========================

    document.addEventListener("click", function (e) {

        const row = e.target.closest(".suggestion-row");

        if (!row) return;

        const value = row.dataset.value;

        const input = document.getElementById("search_query");

        if (!input) return;

        input.value = value;

        input.dispatchEvent(
            new Event("input", { bubbles: true })
        );

        const curtain = document.querySelector(".suggestions-curtain");

        if (curtain) {

            curtain.style.display = "none";

        }

    });

});

</script>

""")
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


# للتوافق مع server.py
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

            ui.span("📐"),

            ui.span(coords.get("size", "-")),

            class_="coord-line"

        ),

        ui.div(

            ui.span("🖥"),

            ui.span(coords.get("panel", "-")),

            class_="coord-line"

        ),

        ui.div(

            ui.span("📡"),

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

    cards = []

    for model in models:

        cards.append(

            ui.div(

                ui.div(

                    class_="result-orb",

                    style=f"""
                    background:{color};
                    box-shadow:
                        0 0 8px {color},
                        0 0 18px {color},
                        0 0 28px {color};
                    """

                ),

                ui.div(

                    model,

                    class_="model-name"

                ),

                class_="glass-result-card",

                style=f"""
                border-right:5px solid {color};
                """

            )

        )

    return ui.div(

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
            """

        ),

        *cards,

        class_="neon-container"

    )
# ==========================================================
# AUTO COMPLETE CURTAIN
# ==========================================================

def draw_suggestions_curtain(suggestions):

    if not suggestions:
        return None

    rows = []

    for model in suggestions:

        rows.append(

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

        )

    return ui.div(

        *rows,

        class_="suggestions-curtain glass-card"

    )


# ==========================================================
# SEARCH BOX
# ==========================================================

def draw_search_box():

    return ui.div(

        ui.input_text(

            "search_query",

            "",

            placeholder="ابحث عن موديل الهاتف..."

        ),

        ui.output_ui(

            "suggestions_curtain"

        ),

        class_="search-box"

    )
# ==========================================================
# SYSTEM INFO
# ==========================================================

def draw_system_info():

    return ui.div(

        ui.h4(

            "معلومات النظام"

        ),

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

        ui.h4(

            "عدد الهواتف"

        ),

        ui.div(

            str(total),

            class_="metric-value"

        ),

        class_="metric-box glass-card"

    )


# ==========================================================
# MONITOR
# ==========================================================

def draw_monitor_component(status):

    online = str(status).upper() == "ONLINE"

    return ui.div(

        ui.h4(

            "المراقب الصامت"

        ),

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
# NOTIFICATIONS
# ==========================================================

def draw_notification_component(count=0):

    return ui.div(

        ui.h4(

            "الإشعارات"

        ),

        ui.div(

            f"🔔 {count}",

            class_="metric-value"

        ),

        class_="metric-box glass-card"

    )


# ==========================================================
# SILENT INSPECTOR
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
# SETTINGS DRAWER
# ==========================================================

def draw_settings_modal():

    return ui.div(

        ui.div(

            ui.h2(

                "⚙️ الإعدادات"

            ),

            ui.tags.button(

                "✖",

                id="btn_close_drawer_trigger",

                class_="drawer-close-btn",

                title="إغلاق"

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
# PLAN 2 MODAL
# ==========================================================

def draw_plan_2_modal(phone="", panels=None, sensors=None):

    panels = panels or []

    sensors = sensors or []

    return draw_modal_overlay(

        ui.div(

            ui.h2(

                "الخطة الثانية"

            ),

            ui.p(

                f"الهاتف: {phone}"

            ),

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
# PLAN 3 MODAL
# ==========================================================

def draw_plan_3_modal(phone="", result=None):

    return draw_modal_overlay(

        ui.div(

            ui.h2(

                "الخطة الثالثة"

            ),

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
# MAIN UI
# ==========================================================

app_ui = ui.page_fluid(

    inject_styles(),

    draw_drawer_js_handler(),

    # ======================================================
    # الخلفية الثابتة
    # ======================================================

    ui.div(
        class_="fixed-background"
    ),

    # ======================================================
    # درج الإعدادات
    # ======================================================

    draw_settings_modal(),

    # ======================================================
    # الواجهة الرئيسية
    # ======================================================

    ui.div(

        draw_header(),

        draw_search_box(),

        ui.output_ui(
            "welcome_area"
        ),

        ui.output_ui(
            "results_workflow_view"
        ),

        ui.output_ui(
            "dynamic_modal_container"
        ),

        class_="main-layout"

    )

)
