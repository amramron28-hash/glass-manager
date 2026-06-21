from shiny import App, ui, render, reactive
import json

# ==============================================================================
# الملف الكامل: app.py
# ==============================================================================

# 1. الواجهة (UI) - تم دمج جميع العناصر لضمان عدم اختفاء أي منها
app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""
            body { background: #0d1117; color: white; font-family: 'Segoe UI', sans-serif; margin: 0; }
            /* الدرج الجانبي - ثابت ومستقر */
            .drawer { position: fixed; top: 0; left: -300px; width: 280px; height: 100%; 
                      background: rgba(13,17,23,0.98); backdrop-filter: blur(20px); 
                      border-right: 2px solid #00bfff; transition: 0.5s; z-index: 9999; padding: 25px; }
            .drawer.open { left: 0; }
            .header-bar { display: flex; justify-content: space-between; padding: 20px; align-items: center; background: rgba(0,0,0,0.2); }
            
            /* البطاقات الزجاجية - بدون إطارات زرقاء داخلية */
            .glass-card { background: rgba(255,255,255,0.08); backdrop-filter: blur(12px); 
                          border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; 
                          padding: 20px; margin: 15px auto; width: 90%; max-width: 500px; }
            .card-blue { border-left: 10px solid #3498db; }
            
            /* نظام الاقتراحات المخصص (يظهر تحت البحث مباشرة) */
            .search-box { position: relative; max-width: 500px; margin: auto; padding: 20px; }
            #custom_suggestions { position: absolute; width: 90%; background: #161b22; border: 1px solid #00bfff; border-radius: 10px; z-index: 9998; display: none; max-height: 200px; overflow-y: auto; }
            .suggestion-item { padding: 15px; border-bottom: 1px solid #222; cursor: pointer; }
            .suggestion-item:hover { background: #00bfff; color: black; }
            .btn-neon { background: #00bfff; border: none; padding: 12px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 10px; }
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

    # الدرج الجانبي
    ui.HTML("""<div id="drawer" class="drawer">
        <h3 style="color:#00bfff;">الإعدادات</h3>
        <p>⚙️ ضبط النظام | 🔔 الإشعارات | 🔇 صامت</p>
        <hr><p>📊 إجمالي الموديلات: 364</p>
        <button onclick="toggleDrawer()" style="width:100%; padding:12px; background:#00bfff; border:none; border-radius:10px;">إغلاق</button>
    </div>"""),

    # الشريط العلوي
    ui.div(
        ui.HTML('<div style="cursor:pointer; font-size:28px;" onclick="toggleDrawer()">☰</div>'),
        ui.h2("ZEGAAR AMMAR", style="color:#00bfff; margin:0;"),
        ui.HTML('<div>🔔</div>'), class_="header-bar"
    ),

    # منطقة البحث
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.HTML("<div id='custom_suggestions'></div>"),
        ui.output_ui("main_content_ui"),
        class_="search-box"
    )
)

# 2. السيرفر (Logic)
def server(input, output, session):
    current_step = reactive.value(0)
    
    # الاقتراحات المخصصة
    @reactive.effect
    def _():
        models = ["Redmi 9", "Infinix Smart 9", "Realme 14X", "Vivo Y300T"]
        query = input.search_query()
        filtered = [m for m in models if query and query.lower() in m.lower()]
        items = "".join([f"<div class='suggestion-item' onclick=\"selectModel('{m}')\">{m}</div>" for m in filtered])
        if items:
            ui.update_html("custom_suggestions", content=items)
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'block';")
        else:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")

    # تتابع الخطوات (النتائج لا تظهر إلا بعد إتمام الخطوات)
    @render.ui
    def main_content_ui():
        if input.search_query() and current_step() == 0: current_step.set(1)
        
        if current_step() == 1:
            return ui.div(ui.h4("📏 الخطوة 1: المقاس"), ui.input_text("v1", ""), 
                          ui.input_action_button("nxt1", "التالي للخطوة 2", class_="btn-neon"), class_="glass-card card-blue")
        if current_step() == 2:
            return ui.div(ui.h4("📺 الخطوة 2: الشكل"), ui.input_select("v2", "", ["Notch", "Punch"]), 
                          ui.input_action_button("nxt2", "التالي للخطوة 3", class_="btn-neon"), class_="glass-card card-blue")
        if current_step() == 3:
            return ui.div(ui.h4("🔌 الخطوة 3: المستشعر"), ui.input_select("v3", "", ["Hard", "Virt"]), 
                          ui.input_action_button("fin", "حفظ البيانات", class_="btn-neon"), class_="glass-card card-blue")
        return ui.div()

    @reactive.effect
    @reactive.event(input.nxt1)
    def _(): current_step.set(2)
    @reactive.effect
    @reactive.event(input.nxt2)
    def _(): current_step.set(3)
    @reactive.effect
    @reactive.event(input.fin)
    def _(): current_step.set(0) # تصفير بعد الحفظ

app = App(app_ui, server)

