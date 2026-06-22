import os
from shiny import App, ui, render, reactive
from supabase import create_client

# إعداد الاتصال بالسحابة
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# التنسيق النهائي (Glassmorphism & Neon)
css = """
    body { background-color: #0a0e17 !important; color: white !important; font-family: sans-serif; }
    .app-title { text-align: center; color: #00bfff; font-size: 2.2em; font-weight: 800; margin-bottom: 0px; text-shadow: 0 0 10px #00bfff; }
    .app-sub { text-align: center; color: #fff; font-size: 1.2em; margin-bottom: 20px; }
    .glass-card { background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; margin: 10px 0; }
    .suggestions-curtain { background: #0a0e17 !important; border: 1px solid #00bfff; border-radius: 10px; z-index: 9999; position: absolute; width: 100%; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
    .suggestion-row { padding: 12px; color: white; cursor: pointer; border-bottom: 1px solid #1c2538; }
    .suggestion-row:hover { background: #00bfff; color: black; }
    .badge { display:inline-block; width:30px; height:30px; border-radius:50%; text-align:center; line-height:30px; margin-left:10px; border:1px solid #fff; }
    .card-exact { border-right: 6px solid #00ff88; }
    .card-plus { border-right: 6px solid #00bfff; }
    .card-minus { border-right: 6px solid #ffaa00; }
    .card-warn { border-right: 6px solid #ff3333; }
"""

app_ui = ui.page_fluid(
    ui.head_content(ui.tags.style(css)),
    ui.sidebar(
        ui.h3("🛠️ الإعدادات", style="text-align:center;"),
        ui.hr(),
        ui.div("🔔 جرس الإشعارات: نشط"),
        ui.div("🛡️ المراقب الصامت: يعمل"),
        ui.output_ui("sidebar_counter"),
        ui.input_action_button("btn_refresh", "🔄 تحديث البيانات", class_="btn-neon")
    ),
    ui.div(ui.h1("ZEGAAR AMMAR", class_="app-title"), ui.p("GLASS MANAGER", class_="app-sub")),
    ui.div(ui.input_text("search_query", "", placeholder="🔍 ابحث عن الموديل..."), ui.output_ui("suggestions_curtain"), class_="search-box"),
    ui.output_ui("main_area")
)

def server(input, output, session):
    plan = reactive.value(1)
    
    @reactive.calc
    def fetch_data():
        input.btn_refresh()
        return supabase.table("phones").select("*").execute().data

    @render.ui
    def sidebar_counter():
        return ui.div(f"📱 إجمالي الموديلات: {len(fetch_data())}")

    @render.ui
    def suggestions_curtain():
        q = input.search_query().lower()
        if not q: return None
        matches = [d['model_name'] for d in fetch_data() if q in d['model_name'].lower()][:6]
        return ui.div(*[ui.div(m, class_="suggestion-row", onclick=f"Shiny.setInputValue('selected_model', '{m}')") for m in matches], class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model)
    def _(): ui.update_text("search_query", value=input.selected_model())

    @render.ui
    def main_area():
        return ui.div(ui.input_action_button("btn_search", "فحص الموديل"), ui.output_ui("results"))

    @render.ui
    def results():
        if not input.btn_search(): return None
        data = fetch_data()
        target = next((d for d in data if d['model_name'].lower() == input.search_query().lower()), None)
        if not target: return ui.div("الموديل غير موجود.", class_="glass-card")
        
        res = []
        for d in data:
            # 1. التحذير (الحساس)
            if d['sensor'] != target['sensor']:
                res.append(ui.div(ui.span("🔴", class_="badge"), f"تحذير حساس: {d['model_name']}", class_="glass-card card-warn"))
                continue
            
            # 2. المنطق الرياضي (التسامح 0.03)
            diff = round(d['size'] - target['size'], 3)
            if diff == 0: res.append(ui.div(ui.span("🟢", class_="badge"), f"مطابق: {d['model_name']}", class_="glass-card card-exact"))
            elif 0 < diff <= 0.03: res.append(ui.div(ui.span("🔵", class_="badge"), f"أكبر (Plus): {d['model_name']}", class_="glass-card card-plus"))
            elif -0.03 <= diff < 0: res.append(ui.div(ui.span("🟠", class_="badge"), f"أصغر (Minus): {d['model_name']}", class_="glass-card card-minus"))
        
        return ui.div(*res)

app = App(app_ui, server)
