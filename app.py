import os
import base64
from shiny import App, ui, render, reactive
from database import load_db, save_db
from workflows import run_system_workflows
from ui_components import inject_pwa_and_styles

# ==============================================================================
# 1. الموارد والتهيئات
# ==============================================================================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return f"data:image/webp;base64,{base64.b64encode(f.read()).decode()}"
    return ""

bg_img = get_base64_image("phone_image.webp")

# ==============================================================================
# 2. الواجهة الرسومية (UI) - التصميم الزجاجي الكامل
# ==============================================================================
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML(inject_pwa_and_styles()),
        ui.HTML(f"""
        <style>
            body {{ background: url('{bg_img}') no-repeat center center fixed; background-size: cover; color: white; margin: 0; font-family: sans-serif; }}
            .drawer {{ position: fixed; top: 0; left: -300px; width: 280px; height: 100%; background: rgba(13,17,23,0.85); backdrop-filter: blur(15px); border-right: 1px solid rgba(255,255,255,0.1); transition: 0.4s; z-index: 9999; padding: 25px; }}
            .drawer.open {{ left: 0; }}
            
            .glass-card {{ margin: 15px auto; padding: 20px; border-radius: 20px; width: 90%; max-width: 500px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}
            .card-green {{ background: rgba(46, 204, 113, 0.4); border-left: 8px solid #2ecc71; }}
            .card-blue {{ background: rgba(52, 152, 219, 0.4); border-left: 8px solid #3498db; }}
            .card-orange {{ background: rgba(230, 126, 34, 0.4); border-left: 8px solid #e67e22; }}
            
            .search-container {{ max-width: 600px; margin: auto; padding: 20px; position: relative; }}
            .status-badge {{ float: right; font-size: 0.75rem; background: rgba(0,0,0,0.4); padding: 3px 8px; border-radius: 10px; }}
            .btn-neon {{ background: #00bfff; border: none; padding: 12px; border-radius: 10px; color: black; width: 100%; font-weight: bold; cursor: pointer; margin-top: 10px; }}
        </style>
        """)
    ),
    
    # الدرج الجانبي
    ui.HTML("""<div id="drawer" class="drawer">
        <h3 style="color:#00bfff;">الاعدادات</h3>
        <p>⚙️ ضبط النظام | 🔔 الاشعارات | 🔇 المراقب الصامت</p>
        <hr><p>📊 إجمالي الموديلات: 364</p>
        <button onclick="document.getElementById('drawer').classList.remove('open')" class="btn-neon">إغلاق</button>
    </div>"""),

    # الشريط العلوي
    ui.div(
        ui.HTML('<div style="cursor:pointer; font-size:24px; color:#00bfff;" onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')">☰</div>'),
        ui.h2("ZEGAAR AMMAR", style="margin:0; color:#00bfff; text-shadow:0 0 5px #00bfff;"),
        ui.HTML('<div>🔔</div>'),
        style="display:flex; justify-content:space-between; padding:20px; align-items:center;"
    ),

    # البحث
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.output_ui("autocomplete_ui"),
        ui.output_ui("main_content_ui"),
        class_="search-container"
    )
)

# ==============================================================================
# 3. منطق السيرفر (Server Logic)
# ==============================================================================
def server(input, output, session):
    db = reactive.value(load_db())
    current_step = reactive.value(0)

    # 1. قائمة الاقتراحات الذكية
    @render.ui
    def autocomplete_ui():
        all_models = [m for s in db.get().values() for p in s.values() for sen in p.values() for m in sen.get("models", [])]
        options = "".join([f"<option value='{m}'>" for m in set(all_models)])
        return ui.HTML(f"<datalist id='models_list'>{options}</datalist>"
                       "<script>document.getElementById('search_query').setAttribute('list', 'models_list');</script>")

    # 2. تسلسل الخطط والنتائج
    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query: 
            current_step.set(0)
            return ui.div()
        
        results = run_system_workflows(query, db.get(), [])
        if results: return ui.HTML(results)
        
        # إذا لم نجد الموديل: نبدأ التتابع
        if current_step() == 0: current_step.set(1)
        
        if current_step() == 1:
            return ui.div(ui.h4("📏 الخطوة 1: أدخل المقاس"), ui.input_text("v1", ""), 
                          ui.input_action_button("nxt1", "التالي للخطوة 2", class_="btn-neon"), class_="glass-card card-blue")
        if current_step() == 2:
            return ui.div(ui.h4("📺 الخطوة 2: شكل الشاشة"), ui.input_select("v2", "", ["Notch", "Punch", "Curved"]), 
                          ui.input_action_button("nxt2", "التالي للخطوة 3", class_="btn-neon"), class_="glass-card card-blue")
        if current_step() == 3:
            return ui.div(ui.h4("🔌 الخطوة 3: المستشعر"), ui.input_select("v3", "", ["Hardware", "Virtual"]), 
                          ui.input_action_button("fin", "إتمام وحفظ", class_="btn-neon"), class_="glass-card card-blue")
        return ui.div()

    @reactive.effect
    @reactive.event(input.nxt1)
    def _(): current_step.set(2)
    @reactive.effect
    @reactive.event(input.nxt2)
    def _(): current_step.set(3)
    @reactive.effect
    @reactive.event(input.fin)
    def _():
        save_db(db.get(), input.search_query(), input.v1(), input.v2(), input.v3())
        db.set(load_db())
        current_step.set(0)

app = App(app_ui, server)
