from shiny import ui

def inject_styles():
    return ui.tags.head(ui.tags.link(rel="stylesheet", href="style_v2.css"))

# --- الدوال المطلوبة للعمل ---

def draw_technical_coords(size, panel, sensor, name):
    return ui.div(ui.h3(f"📱 {name}"), ui.p(f"المقاس: {size}"), ui.p(f"الشاشة: {panel}"), ui.p(f"المستشعر: {sensor}"), class_="glass-card-container")

def draw_neon_section(title, models, color, icon, cls): 
    dot_colors = {"exact": "#2ecc71", "plus": "#3498db", "minus": "#e67e22", "warn": "#e74c3c"}
    percentages = {"exact": "0.00", "plus": "+0.03", "minus": "-0.03", "warn": "⚠️"}
    return ui.div(
        ui.div(
            ui.span("● ", style=f"color: {dot_colors.get(cls, '#fff')}; font-size: 14px;"),
            ui.strong(title),
            ui.span(f" ({percentages.get(cls, '')})", style="font-size: 11px; opacity: 0.7; margin-left: 5px;"),
            style="margin-bottom: 10px; display: flex; align-items: center;"
        ),
        *[ui.div(m, class_=f"ammar-flat-card flat-{cls}") for m in models], 
        class_="glass-card-container"
    )

def draw_welcome_section():
    return ui.div(ui.tags.img(src="phone_image.webp", style="width:100%; border-radius:15px;"), ui.h3("مرحباً بك في GLASS MANAGER"), class_="glass-card-container")

def draw_plan_2_modal(phone, panels, sensors):
    return ui.div(ui.h3("🚨 إعدادات إضافية (Plan 2)"), ui.p(f"للهاتف: {phone}"), ui.input_text("p2_size", "المقاس"), ui.input_selectize("p2_panel", "الشاشة", choices=panels or []), ui.input_selectize("p2_sensor", "المستشعر", choices=sensors or []), ui.input_action_button("exec_plan2", "تطبيق"), ui.input_action_button("btn_close_modal", "إغلاق"), class_="glass-card-container")

def draw_plan_3_modal(phone):
    return ui.div(ui.h3("⚠️ تنبيه (Plan 3)"), ui.p(f"لا توجد تطابقات لـ: {phone}"), ui.input_action_button("btn_close_modal", "إغلاق"), class_="glass-card-container")

def draw_database_status(t): return ui.div(ui.div("إجمالي الموديلات", class_="metric-title"), ui.div(str(t), class_="metric-value"), class_="metric-box")
def draw_monitor_component(s): return ui.div(ui.div("حالة المراقب", class_="metric-title"), ui.div(s.get("status", "N/A"), class_="metric-value"), class_="metric-box")
def draw_notifications(s): return ui.div(ui.div("🔔 التنبيهات", class_="metric-title"), ui.div(s.get("source", "Supabase"), class_="metric-value"), class_="metric-box")
def draw_silent_inspector(): return ui.div(ui.input_action_button("btn_run_inspector", "🚀 تشغيل التنظيف", class_="btn-neon"), class_="glass-card-container")
def draw_system_info(): return ui.div("📅 متصل بالسحابة", class_="coord-line")
def draw_drawer_js_handler(): return ui.HTML("<script>document.addEventListener('click', e => { if(e.target.id==='btn_settings') document.getElementById('settings-drawer').classList.add('open'); if(e.target.id==='btn_close_drawer_trigger') document.getElementById('settings-drawer').classList.remove('open'); });</script>")

# --- الواجهة الرئيسية ---

app_ui = ui.page_fluid(
    inject_styles(),
    draw_drawer_js_handler(),
    ui.div(ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"), ui.h3("⚙️ الإعدادات"), 
           ui.output_ui("system_info_area"), ui.output_ui("database_status_area"), 
           ui.output_ui("monitor_area"), ui.output_ui("notifications_area"), 
           ui.output_ui("silent_inspector_area"), id="settings-drawer", class_="drawer"),
    ui.div(
        ui.div(ui.div("ZEGAAR AMMAR", class_="brand-neon-main"), ui.div("GLASS MANAGER", class_="brand-neon-sub"), class_="brand-neon-title"),
        ui.div(ui.input_text("search_query", "", placeholder=" ابحث عن موديل..."), ui.output_ui("suggestions_curtain"), class_="search-box"),
        ui.output_ui("welcome_area"), ui.output_ui("results_workflow_view"), ui.output_ui("dynamic_modal_container"), class_="container-fluid"
    )
)
