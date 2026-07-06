from shiny import ui

# ==========================================================
# PWA + GLOBAL STYLES
# ==========================================================

def inject_pwa_and_styles():
    return ui.HTML("""
<link rel="manifest" href="manifest.json">
<link rel="stylesheet" href="style.css">
""")


# ==========================================================
# WELCOME SECTION
# ==========================================================

def draw_welcome_section():
    return ui.div(
        ui.div(
            ui.h2(
                "👋 مرحباً بك",
                style="""
                text-align:center;
                color:var(--primary-color);
                margin-bottom:10px;
                """
            ),

            ui.p(
                "ابدأ بكتابة موديل الهاتف للحصول على القياسات والموديلات المتوافقة.",
                style="""
                text-align:center;
                opacity:.8;
                margin-bottom:20px;
                """
            ),

            class_="glass-card"
        ),
        style="margin-top:20px;"
    )


# ==========================================================
# TECHNICAL CARD
# ==========================================================

def draw_technical_coords(size, panel, sensor, real_name):
    return ui.div(

        ui.h3(
            f"📱 {real_name}",
            style="margin-bottom:10px;"
        ),

        ui.div(
            f"📏 المقاس : {size if size else '-'}",
            class_="coord-line"
        ),

        ui.div(
            f"🖥 الشاشة : {panel if panel else '-'}",
            class_="coord-line"
        ),

        ui.div(
            f"🔍 المستشعر : {sensor if sensor else '-'}",
            class_="coord-line"
        ),

        class_="glass-card tech-card"
    )


# ==========================================================
# COMPATIBLE SECTION
# ==========================================================

def draw_neon_section(title, models, color, icon="", type_class="default"):

    if not models:
        return None

    cards = []

    for model in models:
        cards.append(
            ui.div(
                model,
                class_=f"ammar-flat-card flat-{type_class}"
            )
        )

    return ui.div(

        ui.h4(
            f"{icon} {title}",
            style=f"""
            color:{color};
            margin-bottom:12px;
            """
        ),

        *cards,

        class_="glass-card neon-section",
        style=f"border-right:4px solid {color};margin-top:15px;"
    )
# ==========================================================
# SETTINGS / PLAN MODALS
# ==========================================================

def draw_settings_modal():
    return ui.div(
        ui.h3("⚙️ إعدادات النظام"),
        ui.p("يمكن إدارة إعدادات التطبيق من هذه النافذة."),
        ui.input_action_button(
            "btn_close_modal",
            "إغلاق",
            class_="btn-neon"
        ),
        class_="glass-card modal-content"
    )


def draw_plan_2_modal(phone, panels, sensors):
    return ui.div(

        ui.h3("📋 خطة 2"),

        ui.p(
            f"الموديل: {phone}",
            style="font-weight:bold;"
        ),

        ui.input_text(
            "p2_size",
            "المقاس"
        ),

        ui.input_selectize(
            "p2_panel",
            "نوع الشاشة",
            choices=panels if panels else []
        ),

        ui.input_selectize(
            "p2_sensor",
            "المستشعر",
            choices=sensors if sensors else []
        ),

        ui.input_action_button(
            "exec_plan2",
            "🔍 بحث",
            class_="btn-neon"
        ),

        class_="glass-card modal-content"
    )


def draw_plan_3_modal(phone, result=None):
    return ui.div(

        ui.h3("🚨 خطة 3"),

        ui.p(
            f"الموديل: {phone}"
        ),

        ui.p(
            "لم يتم العثور على مجموعة مطابقة."
        ),

        ui.input_action_button(
            "btn_close_modal",
            "إغلاق",
            class_="btn-neon"
        ),

        class_="glass-card modal-content"
    )


# ==========================================================
# STATUS COMPONENTS
# ==========================================================

def draw_database_status(total):

    return ui.div(

        ui.div(
            "📊 عدد الموديلات",
            class_="metric-title"
        ),

        ui.div(
            str(total),
            class_="metric-value"
        ),

        class_="metric-box"
    )


def draw_monitor_component(status):

    if isinstance(status, dict):
        st = status.get("status", "OFFLINE")
    else:
        st = str(status)

    return ui.div(

        ui.div(
            "🛰️ حالة المراقب",
            class_="metric-title"
        ),

        ui.div(
            st,
            class_="metric-value"
        ),

        class_="metric-box"
    )


def draw_notifications(status):

    if isinstance(status, dict):
        src = status.get("source", "N/A")
    else:
        src = "N/A"

    return ui.div(

        ui.div(
            "🔔 مصدر البيانات",
            class_="metric-title"
        ),

        ui.div(
            src,
            class_="metric-value"
        ),

        class_="metric-box"
        )
# ==========================================================
# MAIN APP UI
# ==========================================================

app_ui = ui.page_fluid(

    inject_pwa_and_styles(),

    # ======================================================
    # SETTINGS DRAWER
    # ======================================================
    ui.div(

        ui.tags.button(
            "✕",
            id="btn_close_drawer_trigger",
            class_="drawer-close-btn"
        ),

        ui.h3("🛠 الإعدادات"),

        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        ui.output_ui("notifications_area"),

        id="settings-drawer",
        class_="drawer"
    ),

    # ======================================================
    # HEADER
    # ======================================================
    ui.div(

        ui.div(

            ui.div(

                ui.tags.span(
                    "ZEGAAR",
                    class_="brand-neon-main"
                ),

                ui.tags.span(
                    "GLASS MANAGER",
                    class_="brand-neon-sub"
                ),

                class_="brand-neon-title"
            ),

            ui.tags.button(
                "⋮",
                id="btn_settings",
                class_="btn-dots-menu"
            ),

            class_="header-bar"
        ),

        # ==================================================
        # SEARCH
        # ==================================================
        ui.div(

            ui.input_text(
                "search_query",
                "",
                placeholder="🔍 ابحث عن موديل الهاتف..."
            ),

            ui.output_ui("suggestions_curtain"),

            class_="search-box"
        ),

        # ==================================================
        # WELCOME
        # ==================================================
        ui.output_ui("welcome_area"),

        # ==================================================
        # RESULTS
        # ==================================================
        ui.output_ui("results_workflow_view"),

        # ==================================================
        # DYNAMIC MODAL
        # ==================================================
        ui.output_ui("dynamic_modal_container"),

        # ==================================================
        # ACTION BUTTONS
        # ==================================================
        ui.div(

            ui.input_action_button(
                "show_add_panel",
                "➕ لوحة"
            ),

            ui.input_action_button(
                "show_add_sensor",
                "➕ مستشعر"
            ),

            ui.input_action_button(
                "trigger_plan_2",
                "📋 خ2"
            ),

            ui.input_action_button(
                "trigger_plan_3",
                "📋 خ3"
            ),

            class_="action-buttons"
        ),

        class_="container-fluid"
    ),

    # ======================================================
    # EMPTY CONTAINERS REQUIRED BY server.py
    # ======================================================
    ui.output_ui("drawer_js_handler")
)
