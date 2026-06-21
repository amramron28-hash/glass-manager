import os
import base64
from shiny import App, ui, render, reactive
from database import load_db, save_db
from workflows import run_system_workflows
from ui_components import inject_pwa_and_styles

# ==============================================================================
# 1. الواجهة (UI) مع تحسينات الـ CSS والـ JavaScript
# ==============================================================================
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML(inject_pwa_and_styles()),
        ui.HTML("""
        <style>
            body { background: #0d1117; color: white; font-family: sans-serif; }
            
            /* تصميم زجاجي موحد بدون إطارات */
            .glass-card {
                background: rgba(255, 255, 255, 0.1) !important;
                backdrop-filter: blur(15px) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 20px !important;
                padding: 20px !important;
                margin: 15px auto !important;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
                width: 90%; max-width: 500px;
            }
            
            /* إزالة أي إطارات زرقاء عند التركيز */
            input:focus { outline: none !important; box-shadow: none !important; border: 1px solid #00bfff !important; }
            
            /* تثبيت قائمة الاقتراحات */
            #models_list { position: fixed !important; top: 80px !important; left: 5% !important; width: 90% !important; z-index: 9999 !important; background: #161b22; border-radius: 10px; }
            .btn-neon { background: #00bfff; border: none; padding: 12px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        </style>
        """),
        ui.HTML("""
        <script>
            // منع ظهور القائمة فوق الكيبورد
            window.addEventListener('focusin', function(e) {
                if (e.target.id === 'search_query') {
                    var list = document.getElementById('models_list');
                    list.style.display = 'block';
                }
            });
        </script>
        """)
    ),
    
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.output_ui("autocomplete_ui"),
        ui.output_ui("main_content_ui"),
        style="padding: 20px;"
    )
)

# ==============================================================================
# 2. السيرفر (Logic)
# ==============================================================================
def server(input, output, session):
    db = reactive.value(load_db())
    current_step = reactive.value(0)
    
    @render.ui
    def autocomplete_ui():
        all_models = [m for s in db.get().values() for p in s.values() for sen in p.values() for m in sen.get("models", [])]
        options = "".join([f"<option value='{m}'>" for m in set(all_models)])
        return ui.HTML(f"<datalist id='models_list'>{options}</datalist>"
                       "<script>document.getElementById('search_query').setAttribute('list', 'models_list');</script>")

    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query: 
            current_step.set(0)
            return ui.div()
        
        # النتائج
        results = run_system_workflows(query, db.get(), [])
        if results: return ui.HTML(results)
        
        # الخطوات المتتابعة
        if current_step() == 0: current_step.set(1)
        
        if current_step() == 1:
            return ui.div(ui.h4("📏 الخطوة 1"), ui.input_text("v1", "المقاس:"), 
                          ui.input_action_button("nxt1", "التالي", class_="btn-neon"), class_="glass-card")
        if current_step() == 2:
            return ui.div(ui.h4("📺 الخطوة 2"), ui.input_select("v2", "الشكل:", ["Notch", "Punch"]), 
                          ui.input_action_button("nxt2", "التالي", class_="btn-neon"), class_="glass-card")
        if current_step() == 3:
            return ui.div(ui.h4("🔌 الخطوة 3"), ui.input_select("v3", "المستشعر:", ["Hardware", "Virtual"]), 
                          ui.input_action_button("fin", "حفظ", class_="btn-neon"), class_="glass-card")
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
