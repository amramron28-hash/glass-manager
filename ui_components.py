from shiny import ui

def inject_styles():
    return ui.tags.head(
        ui.tags.link(rel="stylesheet", href="style_v2.css"),
        ui.tags.script(src="https://code.jquery.com/jquery-3.6.0.min.js")
    )

# --- دوال المكونات ---

def draw_technical_coords(size, panel, sensor, name):
    return ui.div(
        ui.h3(f"📱 {name}", style="color: #fff;"),
        ui.p(f"المقاس: {size}"),
        ui.p(f"الشاشة: {panel}"),
        ui.p(f"المستشعر: {sensor}"),
        class_="glass-card-container"
    )

def draw_neon_section(title, models, color, icon, cls):
    # البطاقات الزجاجية (Glass Card)
    return ui.div(
        ui.div(ui.strong(title), style="margin-bottom: 10px; display: block; color: #fff;"),
        *[ui.div(m, class_=f"ammar-flat-card flat-{cls}") for m in (models or [])],
        class_="glass-card-container"
    )

def draw_welcome_section():
    return ui.div(
        ui.tags.img(src="phone_image.webp", style="width:100%; max-width:250px; border-radius:20px; margin-bottom:15px;"),
        ui.h3("مرحباً بك في GLASS MANAGER", style="color: #3498db;"),
        class_="glass-card-container", style="text-align:center;"
    )

def draw_plan_2_modal(phone, panels, sensors):
    return ui.div(
        ui.h3("🚨 إعدادات إضافية"),
        ui.p(f"للهاتف: {phone}"),
        ui.input_text("p2_size", "المقاس"),
        ui.input_selectize("p2_panel", "نوع الشاشة", choices=panels or []),
        ui.input_action_button("exec_plan2", "تطبيق", class_="btn-neon"),
        ui.input_action_button("btn_close_modal", "إغلاق"),
        class_="glass-card-container modal-style"
    )

def draw_plan_3_modal(phone):
    return ui.div(ui.h3("⚠️ تنبيه"), ui.p(f"لا توجد نتائج لـ: {phone}"), ui.input_action_button("btn_close_modal", "إغلاق"), class_="glass-card-container")

def draw_database_status(t): return ui.div(ui.div("إجمالي الموديلات"), ui.div(str(t), style="font-size:20px; font-weight:bold;"), class_="metric-box")
def draw_monitor_component(s): return ui.div(ui.div("حالة المراقب"), ui.div(s.get("status", "N/A"), style="color:#2ecc71;"), class_="metric-box")
def draw_notifications(s): return ui.div(ui.div("🔔 التنبيهات"), ui.div("Supabase Active", style="font-size:12px;"), class_="metric-box")
def draw_silent_inspector(): return ui.div(ui.input_action_button("btn_run_inspector", "🚀 تشغيل التنظيف", class_="btn-neon"), class_="glass-card-container")
def draw_system_info(): return ui.div("📅 الإصدار: 2026.07", class_="coord-line")

def draw_drawer_js_handler():
    return ui.HTML("""
    <script>
    $(document).on('click', '#btn_settings', function() { $('#settings-drawer').addClass('open'); });
    $(document).on('click', '#btn_close_drawer_trigger', function() { $('#settings-drawer').removeClass('open'); });
    </script>
    """)

# --- الواجهة الرئيسية ---

app_ui = ui.page_fluid(
    inject_styles(),
    draw_drawer_js_handler(),
    # القائمة الجانبية
    ui.div(
        ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"),
        ui.h3("⚙️ الإعدادات"),
        ui.output_ui("system_info_area"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        ui.output_ui("silent_inspector_area"),
        id="settings-drawer", class_="drawer"
    ),
    # المحتوى الرئيسي
    ui.div(
        ui.div(
            ui.tags.button("⚙️", id="btn_settings", class_="btn-settings-open"),
            ui.div("ZEGAAR AMMAR", class_="brand-neon-main"), 
            ui.div("GLASS MANAGER", class_="brand-neon-sub"), 
            class_="brand-neon-title"
        ),
        ui.div(
            ui.input_text("search_query", "", placeholder=" ابحث عن موديل..."),
            ui.output_ui("suggestions_curtain"),
            class_="search-box"
        ),
        ui.output_ui("welcome_area"),
        ui.output_ui("results_workflow_view"),
        ui.output_ui("dynamic_modal_container"),
        class_="container-fluid"
    )
)
