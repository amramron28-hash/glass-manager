from shiny import ui

def inject_pwa_and_styles():
    return ui.HTML('<link rel="stylesheet" href="style_v2.css">')

# --- الدوال المطلوبة للسيرفر والواجهة ---
def draw_welcome_section(src="phone_image.webp"): 
    return ui.div(ui.tags.img(src=src, class_="welcome-phone-image"), class_="glass-card")

def draw_technical_coords(size, panel, sensor, name): 
    return ui.div(ui.h3(f"📱 {name}"), ui.p(f"المقاس: {size}"), ui.p(f"الشاشة: {panel}"), ui.p(f"المستشعر: {sensor}"), class_="glass-card")

def draw_neon_section(title, models, color, icon, cls): 
    return ui.div(ui.h4(f"{icon} {title}"), *[ui.div(m, class_=f"ammar-flat-card flat-{cls}") for m in models], class_="glass-card")

def draw_plan_2_modal(p, pnl, sns): 
    return ui.div(ui.h3("خطة 2"), ui.input_text("p2_size", "المقاس"), ui.input_selectize("p2_panel", "الشاشة", choices=pnl or []), ui.input_selectize("p2_sensor", "المستشعر", choices=sns or []), ui.input_action_button("exec_plan2", "بحث"), class_="glass-card")

def draw_plan_3_modal(p): 
    return ui.div(ui.h3("🚨 خطة 3"), ui.input_action_button("btn_close_modal", "إغلاق"), class_="glass-card")

def draw_database_status(t): 
    return ui.div(ui.div("إجمالي الهواتف", class_="metric-title"), ui.div(str(t), class_="metric-value"), class_="metric-box")

def draw_monitor_component(s): 
    return ui.div(ui.div("حالة المراقب", class_="metric-title"), ui.div(s.get("status", "N/A"), class_="metric-value"), class_="metric-box")

def draw_notifications(s): 
    return ui.div(ui.div("🔔 التنبيهات", class_="metric-title"), ui.div(s.get("source", "Supabase"), class_="metric-value"), class_="metric-box")

def draw_silent_inspector(): 
    return ui.div(ui.input_action_button("btn_run_inspector", "🚀 تشغيل التنظيف", class_="btn-neon"), class_="glass-card")

def draw_system_info(): 
    return ui.div("📅 التاريخ: متصل بالسحابة", class_="coord-line")

def draw_drawer_js_handler(): 
    return ui.HTML("<script>document.addEventListener('click', e => { if(e.target.id==='btn_settings') document.getElementById('settings-drawer').classList.add('open'); if(e.target.id==='btn_close_drawer_trigger') document.getElementById('settings-drawer').classList.remove('open'); });</script>")

# --- الواجهة الرئيسية الكاملة ---
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    draw_drawer_js_handler(),
    # القائمة الجانبية (Drawer)
    ui.div(
        ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"),
        ui.h3("⚙️ الإعدادات"),
        ui.output_ui("system_info_area"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        ui.output_ui("notifications_area"),
        ui.output_ui("silent_inspector_area"),
        id="settings-drawer", class_="drawer"
    ),
    # المحتوى الرئيسي
    ui.div(
        ui.div(
            ui.div(ui.tags.span("ZEGAAR AMMAR", class_="brand-neon-main"), ui.tags.span("GLASS MANAGER", class_="brand-neon-sub"), class_="brand-neon-title"),
            ui.tags.button("⚙️", id="btn_settings", class_="btn-dots-menu"),
            class_="header-bar"
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
