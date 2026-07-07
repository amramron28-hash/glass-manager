from shiny import ui
import datetime

# ==========================================================
# PWA + GLOBAL STYLES
# ==========================================================
def inject_pwa_and_styles():
    """حقن روابط الملفات الثابتة وملف الـ CSS"""
    return ui.HTML("""
    <link rel="manifest" href="/manifest.json">
    <link rel="stylesheet" href="/style.css">
    """)


# ==========================================================
# WELCOME SECTION (صورة الهاتف)
# ==========================================================
def draw_welcome_section(image_src: str = "/phone_image.webp"):
    """تظهر صورة الهاتف فقط عند عدم وجود نتائج بحث"""
    return ui.div(
        ui.tags.img(
            src=image_src,
            alt="Phone Interface",
            class_="welcome-phone-image",
            style="max-width: 300px; width: 100%; height: auto; display: block; margin: 0 auto;"
        ),
        class_="glass-card welcome-image-card",
        style="text-align: center; padding: 30px 20px;"
    )


# ==========================================================
# TECHNICAL CARD
# ==========================================================
def draw_technical_coords(size: str, panel: str, sensor: str, real_name: str):
    return ui.div(
        ui.h3(f"📱 {real_name}", class_="tech-title"),
        ui.div(f" المقاس : {size if size else '-'}", class_="coord-line"),
        ui.div(f"📺 الشاشة : {panel if panel else '-'}", class_="coord-line"),
        ui.div(f"🔧 المستشعر : {sensor if sensor else '-'}", class_="coord-line"),
        class_="glass-card tech-card"
    )


# ==========================================================
# COMPATIBLE SECTION
# ==========================================================
def draw_neon_section(title: str, models: list = None, color: str = "#3498db", icon: str = "", type_class: str = "default"):
    if not models:
        return None
    return ui.div(
        ui.h4(f"{icon} {title}", class_="neon-section-title", style=f"color:{color};"),
        *[ui.div(model, class_=f"ammar-flat-card flat-{type_class}") for model in models],
        class_="glass-card neon-section",
        style=f"border-right:4px solid {color};"
    )


# ==========================================================
# PLAN MODALS
# ==========================================================
def draw_plan_2_modal(phone: str, panels: list = None, sensors: list = None):
    panels_list = sorted(list(panels)) if panels else []
    sensors_list = sorted(list(sensors)) if sensors else []
    
    return ui.div(
        ui.h3(" خطة 2"),
        ui.p(f"الموديل: {phone}", style="font-weight:bold;"),
        ui.input_text("p2_size", "المقاس"),
        ui.input_selectize("p2_panel", "نوع الشاشة", choices=panels_list),
        ui.input_selectize("p2_sensor", "المستشعر", choices=sensors_list),
        ui.input_action_button("exec_plan2", "🔍 بحث", class_="btn-neon"),
        class_="glass-card modal-content"
    )


def draw_plan_3_modal(phone: str):
    return ui.div(
        ui.h3("🚨 خطة 3"),
        ui.p(f"الموديل: {phone}"),
        ui.p("لم يتم العثور على مجموعة مطابقة."),
        ui.input_action_button("btn_close_modal", "إغلاق", class_="btn-neon"),
        class_="glass-card modal-content"
    )


# ==========================================================
# STATUS & INSPECTOR COMPONENTS
# ==========================================================
def draw_database_status(total: int):
    return ui.div(
        ui.div(" إجمالي الهواتف المسجلة", class_="metric-title"),
        ui.div(str(total), class_="metric-value"),
        class_="metric-box"
    )


def draw_monitor_component(status):
    st = status.get("status", "OFFLINE") if isinstance(status, dict) else str(status)
    return ui.div(
        ui.div("🛰️ حالة المراقب", class_="metric-title"),
        ui.div(st, class_="metric-value"),
        class_="metric-box"
    )


def draw_notifications(status):
    src = status.get("source", "N/A") if isinstance(status, dict) else "N/A"
    return ui.div(
        ui.div(" مصدر البيانات", class_="metric-title"),
        ui.div(src, class_="metric-value"),
        class_="metric-box"
    )


def draw_silent_inspector():
    """واجهة تشغيل المراقب الصامت"""
    return ui.div(
        ui.h4("🧹 المراقب الصامت", class_="metric-title"),
        ui.p("يقوم بفحص شجرة البيانات في Supabase وإزالة التكرارات تلقائياً.", 
             style="font-size: 0.85em; color: #aaa; margin-bottom: 10px;"),
        ui.input_action_button("btn_run_inspector", "🚀 تشغيل المراقب الآن", 
                               class_="btn-neon", style="width: 100%;"),
        class_="glass-card metric-box"
    )


def draw_system_info():
    """عرض معلومات النظام"""
    return ui.div(
        ui.div(f"📅 تاريخ اليوم: {datetime.date.today().strftime('%Y-%m-%d')}", class_="coord-line"),
        ui.div("📊 حالة الاتصال: متصل وسحابي (Supabase)", class_="coord-line"),
        class_="glass-card metric-box"
    )


# ✅ جديد: معالج JavaScript لتشغيل الـ Drawer
def draw_drawer_js_handler():
    """كود JavaScript لفتح وإغلاق القائمة الجانبية"""
    return ui.HTML("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const drawer = document.getElementById('settings-drawer');
        const btnSettings = document.getElementById('btn_settings');
        const btnCloseDrawer = document.getElementById('btn_close_drawer_trigger');
        
        if (btnSettings && drawer) {
            btnSettings.addEventListener('click', function() {
                drawer.classList.add('open');
            });
        }
        
        if (btnCloseDrawer && drawer) {
            btnCloseDrawer.addEventListener('click', function() {
                drawer.classList.remove('open');
            });
        }
    });
    </script>
    """)


# ==========================================================
# MAIN APP UI
# ==========================================================
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    
    # 1. DRAWER
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
        # Header
        ui.div(
            ui.div(
                ui.tags.span("ZEGAAR", class_="brand-neon-main"),
                ui.tags.span("GLASS MANAGER", class_="brand-neon-sub"),
                class_="brand-neon-title"
            ),
            ui.tags.button("⋮", id="btn_settings", class_="btn-dots-menu"),
            class_="header-bar"
        ),
        
        # Search
        ui.div(
            ui.input_text("search_query", "", placeholder=" ابحث عن موديل الهاتف..."),
            ui.output_ui("suggestions_curtain"),
            class_="search-box"
        ),
        
        # Welcome Area
        ui.output_ui("welcome_area"),
        
        # Results
        ui.output_ui("results_workflow_view"),
        
        # Dynamic Modal
        ui.output_ui("dynamic_modal_container"),
        
        class_="container-fluid"
    ),
    
    # 3. Drawer JS Handler ✅
    ui.output_ui("drawer_js_handler")
)
