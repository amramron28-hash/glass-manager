import os
from html import escape
from shiny import App, ui, render, reactive
from supabase import create_client, Client
from dotenv import load_dotenv

# ==========================================================
# 1) إعداد Supabase
# ==========================================================
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mgmphimlcdchtbiyhhbt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "ضع_مفتاحك_هنا")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# استدعاء الـ workflows
try:
    from workflows import run_system_workflows
except:
    def run_system_workflows(model, data, db):
        return f"<div class='glass-card'><h3 class='neon-text'>{model}</h3><p>Workflow غير متوفر</p></div>"

# ==========================================================
# 2) الواجهة (UI)
# ==========================================================
app_ui = ui.page_fluid(
    ui.head_content(ui.tags.style("""
        body { background:#0d1117; color:white; font-family:'Segoe UI',sans-serif; }
        .header-bar { display:flex; justify-content:space-between; align-items:center; padding:15px 25px; background:rgba(13,17,23,.55); backdrop-filter:blur(12px); border-bottom:1px solid rgba(0,191,255,.25); }
        .drawer { position:fixed; top:0; left:-320px; width:290px; height:100%; background:rgba(22,27,34,.95); backdrop-filter:blur(20px); border-right:2px solid #00bfff; transition:.4s; z-index:20000; padding:30px; }
        .drawer.open { left:0; }
        .glass-card { background:rgba(255,255,255,.05); backdrop-filter:blur(15px); border:1px solid rgba(0,191,255,.3); border-radius:20px; padding:25px; margin:25px auto; max-width:500px; }
        .neon-text { color:#00bfff; }
        .btn-neon { width:100%; padding:12px; border-radius:10px; border:none; background:#00bfff; font-weight:bold; cursor:pointer; }
        #custom_suggestions { position:absolute; width:100%; background:#161b22; border:1px solid #00bfff; border-radius:10px; display:none; max-height:250px; overflow:auto; z-index:9999; }
        .suggestion-item { padding:12px; cursor:pointer; }
        .suggestion-item:hover { background:rgba(0,191,255,.15); }
    """)),
    ui.HTML('<div id="drawer" class="drawer">'),
    ui.h3("⚙️ Supabase", class_="neon-text"),
    ui.output_text("model_count_display"),
    ui.HTML("</div>"),
    ui.div(ui.HTML('<div onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')" style="font-size:28px;cursor:pointer;color:#00bfff">☰</div>'), ui.h2("ZEGAAR AMMAR", style="color:#00bfff"), class_="header-bar"),
    ui.div(ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."), ui.HTML('<div id="custom_suggestions"></div>'), ui.output_ui("main_content_ui"), class_="search-box")
)

# ==========================================================
# 3) السيرفر (Server)
# ==========================================================
def server(input, output, session):
    refresh_trigger = reactive.value(0)
    current_step = reactive.value(0)

    @reactive.calc
    def cloud_database():
        refresh_trigger.get()
        try:
            res = supabase.table("phones").select("*").execute()
            return res.data if hasattr(res, 'data') else []
        except: return []

    @render.text
    def model_count_display():
        return f"📱 عدد الموديلات: {len(cloud_database())}"

    @reactive.effect
    def update_suggestions():
        q = input.search_query().lower()
        db = cloud_database()
        names = [x["model_name"] for x in db if x.get("model_name")]
        matches = [m for m in names if q in m.lower()][:10]
        
        js = f"document.getElementById('custom_suggestions').innerHTML = '';"
        if matches and q:
            js += "document.getElementById('custom_suggestions').style.display='block';"
            for m in matches:
                js += f"document.getElementById('custom_suggestions').innerHTML += '<div class=\"suggestion-item\" onclick=\"Shiny.setInputValue(\\'search_query\\', \\'{m}\\', {{priority: \\'event\\'}});\">{m}</div>';"
        else:
            js += "document.getElementById('custom_suggestions').style.display='none';"
        ui.run_javascript(js)

    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        db = cloud_database()
        phone = next((x for x in db if x.get("model_name") == query), None)
        
        if phone:
            return ui.HTML(run_system_workflows(query, phone, db))
        
        if not query: return ui.div()
        
        # منطق المعالج (Wizard)
        step = current_step()
        if step == 0: current_step.set(1)
        
        if current_step() == 1:
            return ui.div(ui.h4("📏 الخطوة 1: أدخل المقاس", class_="neon-text"), ui.input_text("v1", "المقاس"), ui.input_action_button("next1", "التالي ➡️", class_="btn-neon"), class_="glass-card")
        if current_step() == 2:
            return ui.div(ui.h4("📺 الخطوة 2: الشاشة", class_="neon-text"), ui.input_select("v2", "النوع", ["Notch", "Punch", "Curved"]), ui.input_action_button("next2", "التالي ➡️", class_="btn-neon"), class_="glass-card")
        if current_step() == 3:
            return ui.div(ui.h4("🔌 الخطوة 3: المستشعر", class_="neon-text"), ui.input_select("v3", "المستشعر", ["hardware", "under_display"]), ui.input_action_button("save", "حفظ في السحاب", class_="btn-neon"), class_="glass-card")

    @reactive.effect
    @reactive.event(input.next1)
    def _(): current_step.set(2)
    @reactive.effect
    @reactive.event(input.next2)
    def _(): current_step.set(3)
    @reactive.effect
    @reactive.event(input.save)
    def _():
        try:
            supabase.table("phones").insert({"model_name": input.search_query(), "size": input.v1(), "panel": input.v2(), "sensor": input.v3()}).execute()
            refresh_trigger.set(refresh_trigger() + 1)
            current_step.set(0)
            ui.run_javascript("alert('تم الحفظ!');")
        except Exception as e: print(e)

app = App(app_ui, server)
