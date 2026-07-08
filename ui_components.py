from shiny import ui

def inject_styles():
    return ui.tags.head(
        ui.tags.link(rel="stylesheet", href="style_v2.css?v=1.2"), # إضافة كود للتحديث القسري
        ui.tags.script(src="https://code.jquery.com/jquery-3.6.0.min.js")
    )

def draw_drawer_js_handler():
    return ui.HTML("""
    <script>
    $(document).ready(function() {
        $(document).on('click', '#btn_settings', function(e) {
            e.preventDefault();
            $('#settings-drawer').addClass('open');
        });
        $(document).on('click', '#btn_close_drawer_trigger', function(e) {
            e.preventDefault();
            $('#settings-drawer').removeClass('open');
        });
    });
    </script>
    """)

# --- المكونات ---
def draw_technical_coords(size, panel, sensor, name):
    return ui.div(ui.h3(f"📱 {name}"), ui.p(f"المقاس: {size}"), ui.p(f"الشاشة: {panel}"), ui.p(f"المستشعر: {sensor}"), class_="glass-card-container")

def draw_neon_section(title, models, color, icon, cls):
    return ui.div(ui.strong(title), *[ui.div(m, class_=f"ammar-flat-card") for m in (models or [])], class_="glass-card-container")

def draw_welcome_section():
    return ui.div(ui.tags.img(src="phone_image.webp", style="width:100%; border-radius:20px;"), ui.h3("مرحباً بك في GLASS MANAGER"), class_="glass-card-container", style="text-align:center;")

# --- الواجهة ---
app_ui = ui.page_fluid(
    inject_styles(),
    draw_drawer_js_handler(),
    
    # القائمة الجانبية (تم إضافة class إضافي لضمان الظهور)
    ui.div(
        ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"),
        ui.h3("⚙️ الإعدادات"),
        ui.output_ui("system_info_area"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        ui.output_ui("silent_inspector_area"),
        id="settings-drawer", class_="drawer"
    ),
    
    # المحتوى
    ui.div(
        ui.div(ui.tags.button("⚙️", id="btn_settings", class_="btn-settings-open"), ui.h1("GLASS MANAGER"), class_="header-section"),
        ui.div(ui.input_text("search_query", "", placeholder="ابحث عن موديل..."), ui.output_ui("suggestions_curtain"), class_="search-box"),
        ui.output_ui("welcome_area"),
        ui.output_ui("results_workflow_view"),
        ui.output_ui("dynamic_modal_container"),
        class_="container-fluid"
    )
)
