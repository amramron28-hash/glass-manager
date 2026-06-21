from shiny import App, ui, render, reactive
import json

# ==============================================================================
# الكود الكامل: يشمل التنسيق الثابت، نظام الاقتراحات، والخطوات التتابعية
# ==============================================================================

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""
            body { background: #0d1117; color: white; font-family: sans-serif; margin: 0; }
            /* الدرج الجانبي الثابت */
            .drawer { position: fixed; top: 0; left: -300px; width: 280px; height: 100%; 
                      background: #161b22; border-right: 2px solid #00bfff; 
                      transition: 0.5s; z-index: 9999; padding: 25px; }
            .drawer.open { left: 0; }
            .header-bar { display: flex; justify-content: space-between; padding: 20px; align-items: center; background: #0d1117; }
            
            /* البطاقات والبحث */
            .glass-card { background: rgba(255,255,255,0.05); border: 1px solid #333; border-radius: 20px; padding: 20px; margin: 15px auto; width: 90%; max-width: 500px; }
            .search-box { position: relative; max-width: 500px; margin: auto; padding: 20px; }
            #custom_suggestions { position: absolute; width: 90%; background: #161b22; border: 1px solid #00bfff; border-radius: 10px; z-index: 9998; display: none; }
            .suggestion-item { padding: 15px; border-bottom: 1px solid #333; cursor: pointer; }
            .btn-neon { background: #00bfff; color: black; border: none; padding: 12px; width: 100%; border-radius: 10px; font-weight: bold; }
        """),
        ui.tags.script("""
            function toggleDrawer() { document.getElementById('drawer').classList.toggle('open'); }
            function selectModel(m) { 
                document.getElementById('search_query').value = m; 
                document.getElementById('custom_suggestions').style.display = 'none';
                Shiny.setInputValue('search_query', m, {priority: 'event'});
            }
        """)
    ),

    # الهيكل الثابت للواجهة
    ui.HTML("""<div id="drawer" class="drawer">
        <h3 style="color:#00bfff;">القائمة</h3>
        <p>⚙️ إعدادات | 🔔 تنبيهات | 🔇 صامت</p>
        <button onclick="toggleDrawer()" class="btn-neon">إغلاق</button>
    </div>"""),

    ui.div(
        ui.HTML('<div style="cursor:pointer; font-size:28px;" onclick="toggleDrawer()">☰</div>'),
        ui.h2("ZEGAAR AMMAR", style="color:#00bfff; margin:0;"),
        ui.HTML('<div>🔔</div>'), class_="header-bar"
    ),

    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.HTML("<div id='custom_suggestions'></div>"),
        ui.output_ui("main_content_ui"),
        class_="search-box"
    )
)

def server(input, output, session):
    current_step = reactive.value(0)
    
    # 1. نظام الاقتراحات (قاعدة بيانات ثابتة للاختبار)
    @reactive.effect
    def _():
        models = ["Redmi 9", "Infinix Smart 9", "Realme 14X", "Vivo Y300T"]
        query = input.search_query()
        if not query:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")
            return
        
        filtered = [m for m in models if query.lower() in m.lower()]
        items = "".join([f"<div class='suggestion-item' onclick=\"selectModel('{m}')\">{m}</div>" for m in filtered])
        
        if items:
            ui.update_html("custom_suggestions", content=items)
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'block';")
        else:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")

    # 2. منطق الخطوات (ثابت ولا يمس الواجهة العلوية)
    @render.ui
    def main_content_ui():
        # إذا تم اختيار موديل والخطوة صفر، ننتقل للخطوة 1
        if input.search_query() and current_step() == 0: current_step.set(1)
        
        if current_step() == 1:
            return ui.div(ui.h4("📏 الخطوة 1: المقاس"), ui.input_text("v1", ""), 
                          ui.input_action_button("nxt1", "التالي", class_="btn-neon"), class_="glass-card")
        if current_step() == 2:
            return ui.div(ui.h4("📺 الخطوة 2: الشاشة"), ui.input_select("v2", "", ["Notch", "Punch"]), 
                          ui.input_action_button("nxt2", "التالي", class_="btn-neon"), class_="glass-card")
        if current_step() == 3:
            return ui.div(ui.h4("🔌 الخطوة 3: المستشعر"), ui.input_select("v3", "", ["Hardware", "Virtual"]), 
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
    def _(): current_step.set(0)

app = App(app_ui, server)
