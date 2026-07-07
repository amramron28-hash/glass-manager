from shiny import ui

# --- 1. دوال رسم المكونات (تم دمجها بالكامل) ---

def inject_styles():
    return ui.tags.head(
        ui.tags.link(rel="stylesheet", href="style_v2.css")
    )

def draw_neon_section(title, models, color, icon, cls): 
    # كرات ونسب الحالة
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
    return ui.div(ui.h3("مرحباً بك في GLASS MANAGER"), class_="glass-card-container")

# --- 2. الواجهة الرئيسية (app_ui) ---

app_ui = ui.page_fluid(
    inject_styles(),
    # القائمة الجانبية (Drawer)
    ui.div(
        ui.h3("⚙️ الإعدادات"),
        ui.output_ui("system_info_area"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        id="settings-drawer", class_="drawer"
    ),
    # المحتوى الرئيسي
    ui.div(
        ui.div(
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
        class_="container-fluid"
    )
)

