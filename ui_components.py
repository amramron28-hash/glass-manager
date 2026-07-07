from shiny import ui

def inject_pwa_and_styles():
    # نستخدم 'v2' في اسم الملف لإجبار المتصفح على تحميل نسخة جديدة دائماً
    return ui.HTML("""
    <link rel="stylesheet" href="style_v2.css">
    <script>
        document.addEventListener('click', function(e) {
            if (e.target.id === 'btn_settings') {
                document.getElementById('settings-drawer').classList.add('open');
            }
            if (e.target.id === 'btn_close_drawer_trigger') {
                document.getElementById('settings-drawer').classList.remove('open');
            }
        });
    </script>
    """)

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    
    # القائمة الجانبية (Drawer)
    ui.div(
        ui.tags.button("✕", id="btn_close_drawer_trigger", class_="drawer-close-btn"),
        ui.h3("⚙️ إعدادات النظام"),
        ui.output_ui("system_info_area"),
        ui.output_ui("database_status_area"),
        ui.output_ui("monitor_area"),
        id="settings-drawer",
        class_="drawer"
    ),
    
    # الصفحة الرئيسية
    ui.div(
        ui.div(
            ui.div(
                ui.tags.span("ZEGAAR AMMAR", class_="brand-neon-main"),
                ui.tags.span("GLASS MANAGER", class_="brand-neon-sub"),
                class_="brand-neon-title"
            ),
            ui.tags.button("⚙️", id="btn_settings", class_="btn-dots-menu"),
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
    )
)
