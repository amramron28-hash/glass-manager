from shiny import ui
import datetime

def inject_pwa_and_styles():
    # استخدام اسم ملف CSS جديد لتجاوز مشكلة الكاش
    return ui.HTML("""
    <link rel="manifest" href="/manifest.json">
    <link rel="stylesheet" href="/style_v2.css">
    """)

def draw_welcome_section(image_src: str = "phone_image.webp"):
    return ui.div(
        ui.tags.img(
            src=image_src,
            alt="Phone Interface",
            class_="welcome-phone-image"
        ),
        class_="glass-card welcome-image-card"
    )

# ... (باقي الدوال draw_technical_coords, draw_neon_section, إلخ تبقى كما هي) ...

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    
    # 1. DRAWER (يبقى كما هو)
    ui.div(
        ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"),
        ui.h3("⚙️ إعدادات النظام والمراقبة"),
        ui.output_ui("system_info_area"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        ui.output_ui("notifications_area"),
        ui.output_ui("silent_inspector_area"),
        id="settings-drawer",
        class_="drawer"
    ),
    
    # 2. MAIN PAGE
    ui.div(
        ui.div(
            ui.div(
                ui.tags.span("ZEGAAR AMMAR", class_="brand-neon-main"),
                ui.tags.span("GLASS MANAGER", class_="brand-neon-sub"),
                class_="brand-neon-title"
            ),
            ui.tags.button("⋮", id="btn_settings", class_="btn-dots-menu"),
            class_="header-bar"
        ),
        ui.div(
            ui.input_text("search_query", "", placeholder=" ابحث عن موديل الهاتف..."),
            ui.output_ui("suggestions_curtain"),
            class_="search-box"
        ),
        ui.output_ui("welcome_area"),
        ui.output_ui("results_workflow_view"),
        ui.output_ui("dynamic_modal_container"),
        class_="container-fluid"
    ),
    ui.output_ui("drawer_js_handler")
)
