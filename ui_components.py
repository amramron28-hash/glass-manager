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
    """
    تظهر صورة البداية فقط عند عدم وجود نتائج بحث.
    """
    return ui.div(
        ui.tags.img(
            src="phone_image.webp",
            alt="Phone",
            class_="welcome-phone-image",
            style="""
                display:block;
                margin:auto;
                width:100%;
                max-width:320px;
                height:auto;
                user-select:none;
                pointer-events:none;
            """
        ),
        class_="glass-card welcome-card"
    )


# ==========================================================
# TECHNICAL CARD
# ==========================================================
def draw_technical_coords(size, panel, sensor, real_name):
    return ui.div(

        ui.h3(
            real_name or "-",
            class_="tech-title"
        ),

        ui.div(
            f"📏 المقاس : {size if size else '-'}",
            class_="coord-line"
        ),

        ui.div(
            f"🖥 نوع الشاشة : {panel if panel else '-'}",
            class_="coord-line"
        ),

        ui.div(
            f"🔍 المستشعر : {sensor if sensor else '-'}",
            class_="coord-line"
        ),

        class_="glass-card tech-card"
    )
# ==========================================================
# COMPATIBLE RESULTS (Neon Glass Cards)
# ==========================================================
def draw_neon_section(title, models, color, icon="", type_class="default"):
    """
    بطاقات النتائج الزجاجية الشفافة.
    """
    if not models:
        return None

    return ui.div(

        ui.h4(
            f"{icon} {title}",
            style=f"""
                color:{color};
                font-weight:700;
                margin-bottom:12px;
            """
        ),

        *[
            ui.div(
                model,
                class_=f"ammar-flat-card flat-{type_class}"
            )
            for model in models
        ],

        class_="glass-card neon-section",
        style=f"""
            border-right:4px solid {color};
            margin-top:18px;
        """
    )


# ==========================================================
# SETTINGS MODAL
# ==========================================================
def draw_settings_modal():
    return ui.div(

        ui.h3("⚙️ إعدادات النظام"),

        ui.hr(),

        ui.p(
            "يمكن إدارة خصائص النظام من هذه النافذة.",
            style="opacity:.85;"
        ),

        ui.input_action_button(
            "btn_close_modal",
            "إغلاق",
            class_="btn-neon"
        ),

        class_="glass-card modal-content"
    )


# ==========================================================
# PLAN 2 MODAL
# ==========================================================
def draw_plan_2_modal(phone, panels, sensors):
    return ui.div(

        ui.h3("📋 خطة 2"),

        ui.p(
            f"الموديل : {phone}",
            style="font-weight:bold;"
        ),

        ui.input_text(
            "p2_size",
            "المقاس"
        ),

        ui.input_selectize(
            "p2_panel",
            "نوع الشاشة",
            choices=panels or []
        ),

        ui.input_selectize(
            "p2_sensor",
            "المستشعر",
            choices=sensors or []
        ),

        ui.input_action_button(
            "exec_plan2",
            "🔍 بحث",
            class_="btn-neon"
        ),

        class_="glass-card modal-content"
    )


# ==========================================================
# PLAN 3 MODAL
# ==========================================================
def draw_plan_3_modal(phone, result=None):
    return ui.div(

        ui.h3("🚨 خطة 3"),

        ui.p(
            f"الموديل : {phone}"
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
# STATUS COMPONENTS (داخل نافذة الإعدادات فقط)
# ==========================================================

def draw_database_status(total):
    return ui.div(

        ui.div(
            "📊 عدد الهواتف",
            class_="metric-title"
        ),

        ui.div(
            str(total),
            class_="metric-value"
        ),

        class_="metric-box glass-card"
    )


def draw_monitor_component(status):

    if isinstance(status, dict):
        monitor_status = status.get("status", "OFFLINE")
    else:
        monitor_status = str(status)

    color = (
        "#2ecc71"
        if monitor_status == "ONLINE"
        else "#e67e22"
        if monitor_status == "FALLBACK"
        else "#ff5252"
    )

    return ui.div(

        ui.div(
            "🛰️ المراقب الصامت",
            class_="metric-title"
        ),

        ui.div(
            monitor_status,
            class_="metric-value",
            style=f"color:{color};"
        ),

        class_="metric-box glass-card"
    )


def draw_notifications(status):

    if isinstance(status, dict):
        source = status.get("source", "N/A")
    else:
        source = "N/A"

    return ui.div(

        ui.div(
            "🔔 مصدر البيانات",
            class_="metric-title"
        ),

        ui.div(
            source,
            class_="metric-value"
        ),

        class_="metric-box glass-card"
    )
