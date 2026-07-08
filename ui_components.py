from shiny import ui

# ==========================================================
# CSS + JavaScript
# ==========================================================

def inject_styles():
    return ui.tags.head(
        ui.tags.link(rel="stylesheet", href="style_v2.css"),
        ui.tags.script(src="https://code.jquery.com/jquery-3.6.0.min.js")
    )


def draw_drawer_js_handler():
    return ui.HTML("""
    <script>
    $(document).ready(function(){

        $(document).on("click","#btn_settings",function(){
            $("#settings-drawer").addClass("open");
        });

        $(document).on("click","#btn_close_drawer_trigger",function(){
            $("#settings-drawer").removeClass("open");
        });

        $(document).on("click",".suggestion-row",function(){
            Shiny.setInputValue(
                "search_query",
                $(this).text(),
                {priority:"event"}
            );
        });

    });
    </script>
    """)


# ==========================================================
# Welcome
# ==========================================================

def draw_welcome_section():

    return ui.div(

        ui.tags.img(
            src="phone_image.webp",
            style="""
            width:220px;
            max-width:90%;
            display:block;
            margin:auto;
            border-radius:18px;
            """
        ),

        ui.h2(
            "ZEGAAR AMMAR GLASS MANAGER",
            class_="brand-neon-main"
        ),

        ui.p(
            "النظام الذكي لمطابقة حماية الشاشات",
            class_="coord-line"
        ),

        class_="glass-card-container"
    )


# ==========================================================
# Technical Card
# ==========================================================

def draw_technical_coords(coords):

    if not coords:
        return None

    return ui.div(

        ui.h3(coords.get("real_name","")),

        ui.div(
            f"المقاس : {coords.get('size','-')}",
            class_="coord-line"
        ),

        ui.div(
            f"الشاشة : {coords.get('panel','-')}",
            class_="coord-line"
        ),

        ui.div(
            f"المستشعر : {coords.get('sensor','-')}",
            class_="coord-line"
        ),

        class_="glass-card-container"
    )


# ==========================================================
# Compatibility Cards
# ==========================================================

def draw_neon_section(title, models, cls):

    if not models:
        return None

    return ui.div(

        ui.h3(title),

        *[
            ui.div(
                model,
                class_=f"ammar-flat-card {cls}"
            )
            for model in models
        ],

        class_="glass-card-container"
    )


# ==========================================================
# Drawer Components
# ==========================================================

def draw_system_info():

    return ui.div(

        ui.h4("معلومات النظام"),

        ui.div("الإصدار : 2026.07"),

        class_="metric-box"
    )


def draw_database_status(total):

    return ui.div(

        ui.h4("قاعدة البيانات"),

        ui.div(str(total)),

        class_="metric-box"
    )


def draw_monitor_component(status):

    return ui.div(

        ui.h4("المراقب الصامت"),

        ui.div(str(status)),

        class_="metric-box"
    )


def draw_silent_inspector():

    return ui.div(

        ui.input_action_button(
            "btn_run_inspector",
            "🚀 تشغيل التنظيف"
        ),

        class_="glass-card-container"
    )


# ==========================================================
# PLAN 2
# ==========================================================

def draw_plan_2_modal():

    return ui.div(

        ui.h3("الخطة الثانية"),

        ui.p("يرجى استكمال البيانات"),

        ui.input_action_button(
            "btn_close_modal",
            "إغلاق"
        ),

        class_="glass-card-container"
    )


# ==========================================================
# PLAN 3
# ==========================================================

def draw_plan_3_modal():

    return ui.div(

        ui.h3("الخطة الثالثة"),

        ui.p("لا توجد نتائج مطابقة"),

        ui.input_action_button(
            "btn_close_modal",
            "إغلاق"
        ),

        class_="glass-card-container"
    )


# ==========================================================
# MAIN UI
# ==========================================================

app_ui = ui.page_fluid(

    inject_styles(),

    draw_drawer_js_handler(),

    ui.div(

        ui.tags.button(
            "✕",
            id="btn_close_drawer_trigger",
            class_="drawer-close-btn"
        ),

        ui.h3("⚙️ الإعدادات"),

        ui.output_ui("system_info_area"),

        ui.output_ui("database_status_area"),

        ui.output_ui("monitor_area"),

        ui.output_ui("silent_inspector_area"),

        id="settings-drawer",
        class_="drawer"

    ),

    ui.div(

        ui.tags.button(
            "⚙️",
            id="btn_settings",
            class_="btn-settings-open"
        ),

        ui.div(
            "ZEGAAR AMMAR GLASS MANAGER",
            class_="brand-neon-main"
        ),

        ui.div(

            ui.input_text(
                "search_query",
                "",
                placeholder="ابحث عن موديل..."
            ),

            ui.output_ui("suggestions_curtain"),

            class_="search-box"

        ),

        ui.output_ui("welcome_area"),

        ui.output_ui("results_workflow_view"),

        ui.output_ui("dynamic_modal_container"),

        class_="container-fluid"

    )

)
