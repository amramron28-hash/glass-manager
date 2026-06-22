import os
from shiny import App, ui, render, reactive
from supabase import create_client

# إعداد الاتصال بالسحابة
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# التنسيق الزجاجي العائم
css = """
    body { background-color: #0a0e17 !important; color: white !important; font-family: sans-serif; }
    .app-title { text-align: center; color: #00bfff; font-size: 2.2em; font-weight: 800; margin: 0; text-shadow: 0 0 10px #00bfff; }
    .app-sub { text-align: center; color: #fff; font-size: 1.5em; margin: 0; }
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
    ui.head_content(
        ui.tags.link(rel="manifest", href="manifest.json"),
        ui.tags.meta(name="apple-mobile-web-app-capable", content="yes"),
        ui.tags.style(css)
    ),
    # زر الإعدادات في الزاوية
    ui.div(ui.input_action_button("btn_settings", "⚙️", class_="btn-neon"), style="position:fixed; top:10px; right:10px; z-index:1000;"),
    
    # الشعار في سطرين
    ui.div(
        ui.h1("ZEGAAR AMMAR", class_="app-title"),
        ui.h2("GLASS MANAGER", class_="app-sub"),
        style="margin-top: 20px; margin-bottom: 30px;"
    ),
    
    ui.div(ui.input_text("search_query", "", placeholder="🔍 ابحث عن الموديل..."), ui.output_ui("suggestions_curtain"), class_="search-box"),
    ui.output_ui("results_area")
)

def server(input, output, session):
    @reactive.calc
    def fetch_data(): return supabase.table("phones").select("*").execute().data

    # نافذة الإعدادات المنبثقة
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _():
        m = ui.modal(
            ui.div("🔔 جرس الإشعارات: نشط", ui.br(), "🛡️ المراقب الصامت: يعمل", ui.br(), f"📱 إجمالي الموديلات: {len(fetch_data())}"),
            title="⚙️ إعدادات النظام", easy_close=True
        )
        ui.modal_show(m)

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
    def results_area():
        q = input.search_query().strip().lower()
        if not q: return None
        data = fetch_data()
        target = next((d for d in data if d['model_name'].lower() == q), None)
        if not target: return ui.div("الموديل غير موجود.", class_="glass-card")
        
        res = []
        for d in data:
            if d['sensor'] != target['sensor']:
                res.append(ui.div(ui.span("🔴", class_="badge"), f"تحذير حساس: {d['model_name']}", class_="glass-card card-warn"))
                continue
            diff = round(d['size'] - target['size'], 3)
            if diff == 0: res.append(ui.div(ui.span("🟢", class_="badge"), f"مطابق: {d['model_name']}", class_="glass-card card-exact"))
            elif 0 < diff <= 0.03: res.append(ui.div(ui.span("🔵", class_="badge"), f"أكبر: {d['model_name']}", class_="glass-card card-plus"))
            elif -0.03 <= diff < 0: res.append(ui.div(ui.span("🟠", class_="badge"), f"أصغر: {d['model_name']}", class_="glass-card card-minus"))
        return ui.div(*res)

app = App(app_ui, server)
