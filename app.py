import os
import base64
from shiny import App, ui, render, reactive
from database import load_db, save_db
from workflows import run_system_workflows
from ui_components import inject_pwa_and_styles

# ==============================================================================
# 1. تهيئة الموارد والصور
# ==============================================================================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            return f"data:image/webp;base64,{base64.b64encode(image_file.read()).decode()}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# ==============================================================================
# 2. الواجهة الرسومية (UI)
# ==============================================================================
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML(inject_pwa_and_styles()),
        ui.HTML(f"""
        <style>
            body {{ background: url('{bg_img_base64}') no-repeat center center fixed; background-size: cover; color: white; margin: 0; font-family: sans-serif; }}
            .drawer {{ position: fixed; top: 0; left: -300px; width: 280px; height: 100%; background: rgba(13,17,23,0.98); border-right: 2px solid #00bfff; transition: 0.5s; z-index: 9999; padding: 25px; }}
            .drawer.open {{ left: 0; }}
            .header-bar {{ display: flex; justify-content: space-between; padding: 20px; align-items: center; background: rgba(0,0,0,0.3); }}
            .icon-btn {{ cursor: pointer; font-size: 24px; color: #00bfff; }}
            .step-container {{ background: rgba(13,17,23,0.9); border: 2px solid #00bfff; padding: 25px; border-radius: 15px; margin: 20px auto; width: 90%; max-width: 500px; box-shadow: 0 0 15px rgba(0,191,255,0.3); }}
            .neon-text {{ color: #00bfff; text-shadow: 0 0 5px #00bfff; }}
            .btn-neon {{ background: #00bfff; border: none; padding: 10px; border-radius: 5px; color: black; width: 100%; margin-top: 10px; font-weight: bold; cursor: pointer; }}
        </style>
        """)
    ),
    
    # الدرج المنزلق
    ui.HTML("""
    <div id="drawer" class="drawer">
        <h3 class="neon-text">الإعدادات</h3>
        <p>⚙️ ضبط النظام</p>
        <p>🔔 جرس الإشعارات</p>
        <p>🔇 المراقب الصامت</p>
        <hr style="border:0.5px solid #00bfff;">
        <p>📊 إجمالي الموديلات: 364</p>
        <button onclick="document.getElementById('drawer').classList.remove('open')" class="btn-neon">إغلاق</button>
    </div>
    """),

    # الشريط العلوي
    ui.div(
        ui.HTML('<div class="icon-btn" onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')">☰</div>'),
        ui.h2("ZEGAAR AMMAR", class_="neon-text", style="margin:0;"),
        ui.HTML('<div class="icon-btn">🔔</div>'),
        class_="header-bar"
    ),

    # البحث و Auto-complete
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.output_ui("autocomplete_ui"),
        ui.output_ui("main_content_ui"),
        style="max-width: 600px; margin: auto; padding: 20px;"
    )
)

# ==============================================================================
# 3. السيرفر (Server Logic)
# ==============================================================================
def server(input, output, session):
    db = reactive.value(load_db())
    current_step = reactive.value(0)
    
    # 1. تحديث قائمة البحث تلقائياً
    @render.ui
    def autocomplete_ui():
        all_models = []
        for size_cat in db.get().values():
            for panel_cat in size_cat.values():
                for sensor_cat in panel_cat.values():
                    all_models.extend(sensor_cat.get("models", []))
        options = "".join([f"<option value='{m}'>" for m in set(all_models)])
        return ui.HTML(f"<datalist id='models_list'>{options}</datalist>"
                       "<script>document.getElementById('search_query').setAttribute('list', 'models_list');</script>")

    # 2. منطق النتائج وخطوات الطوارئ
    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query: 
            current_step.set(0)
            return ui.div()
        
        results = run_system_workflows(query, db.get(), [])
        
        if not results:
            if current_step() == 0: current_step.set(1)
            
            # عرض الخطوات بالترتيب
            if current_step() == 1:
                return ui.div(ui.h4("📏 الخطوة 1: أدخل المقاس", class_="neon-text"),
                              ui.input_text("val_size", "المقاس:"),
                              ui.input_action_button("next1", "التالي", class_="btn-neon"), class_="step-container")
            elif current_step() == 2:
                return ui.div(ui.h4("📺 الخطوة 2: شكل الشاشة", class_="neon-text"),
                              ui.input_select("val_panel", "اختر الشكل:", ["Notch", "Punch", "Curved"]),
                              ui.input_action_button("next2", "التالي", class_="btn-neon"), class_="step-container")
            elif current_step() == 3:
                return ui.div(ui.h4("🔌 الخطوة 3: المستشعر", class_="neon-text"),
                              ui.input_select("val_sensor", "اختر المستشعر:", ["Hardware", "Virtual"]),
                              ui.input_action_button("save_all", "إتمام وحفظ", class_="btn-neon"), class_="step-container")
        return ui.HTML(results)

    # 3. تنقل الخطوات
    @reactive.effect
    @reactive.event(input.next1)
    def _(): current_step.set(2)
    @reactive.effect
    @reactive.event(input.next2)
    def _(): current_step.set(3)
    @reactive.effect
    @reactive.event(input.save_all)
    def _():
        save_db(db.get(), input.search_query(), input.val_size(), input.val_panel(), input.val_sensor())
        db.set(load_db())
        current_step.set(0)

app = App(app_ui, server)
