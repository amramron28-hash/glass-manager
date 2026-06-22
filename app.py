import os
import requests
from shiny import App, ui, render, reactive
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. الإعدادات
load_dotenv()
# ضع الرابط الخاص بمشروعك هنا
SUPABASE_URL = "https://your-project-id.supabase.co" 
# ضع المفتاح الذي يبدأ بـ eyJ هنا
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. الواجهة الرسومية (UI)
app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""
            body { background: #0d1117; color: #f5f6fa; font-family: sans-serif; }
            .header-bar { display: flex; justify-content: space-between; padding: 15px; background: rgba(13, 17, 23, 0.45); border-bottom: 1px solid #00bfff; }
            .drawer { position: fixed; top: 0; left: -320px; width: 290px; height: 100%; background: #161b22; border-right: 2px solid #00bfff; transition: 0.4s; padding: 30px; z-index: 10010; }
            .drawer.open { left: 0; }
            .btn-neon { background: #00bfff; color: black; border: none; padding: 10px; width: 100%; border-radius: 8px; cursor: pointer; }
            .neon-text { color: #00bfff; font-weight: bold; }
        """),
        ui.tags.script("""
            function toggleDrawer() { document.getElementById('drawer').classList.toggle('open'); }
        """)
    ),
    ui.HTML('<div id="drawer" class="drawer">'),
    ui.h3("⚙️ الإعدادات السحابية", class_="neon-text"),
    ui.p("📊 إجمالي الموديلات: ", ui.output_text("model_count", inline=True, class_="neon-text")),
    ui.input_action_button("close_btn", "إغلاق", onclick="toggleDrawer()", class_="btn-neon"),
    ui.HTML('</div>'),
    ui.div(
        ui.HTML('<div style="cursor:pointer; font-size:28px;" onclick="toggleDrawer()">☰</div>'),
        ui.h2("ZEGAAR AMMAR", style="color:#00bfff;"),
        class_="header-bar"
    )
)

# 3. السيرفر (Server)
def server(input, output, session):
    @render.text
    def model_count():
        try:
            response = supabase.table("phones").select("model_name").execute()
            if response.data:
                models = {r["model_name"] for r in response.data}
                return str(len(models))
            return "0"
        except Exception as e:
            return "Error"

# 4. تشغيل التطبيق
app = App(app_ui, server)
def server(input, output, session):
    trigger_refresh = reactive.value(0)
    current_step = reactive.value(0)

    @reactive.calc
    def cloud_models():
        trigger_refresh()  
        return fetch_all_models_from_supabase()

    @reactive.effect
    def _update_drawer_count():
        total = len(cloud_models())
        script_html = f"<script>document.getElementById('model_count').innerText = '{total}';</script>"
        ui.insert_ui(ui.HTML(script_html), selector="#model_count", where="beforeBegin", immediate=True)

    @reactive.effect
    def _handle_suggestions():
        query = input.search_query().strip()
        if not query:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")
            return
        models = cloud_models()
        filtered = [m for m in models if query.lower() in m.lower()]
        items = "".join([f"<div class='suggestion-item' onclick=\"selectModel('{escape(m)}')\">{m}</div>" for m in filtered])
        if items:
            ui.update_html("custom_suggestions", content=items)
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'block';")
        else:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")

    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query:
            return ui.div()
        models_list = cloud_models()
        if query in models_list:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")
            results = run_system_workflows(query, {}, [])  
            return ui.HTML(results)
        if query not in models_list and current_step() == 0: 
            current_step.set(1)
        step = current_step()
        if step == 1:
            return ui.div(
                ui.h4("📏 الخطوة 1: أدخل المقاس", class_="neon-text"), 
                ui.input_text("v1", "المقاس الحجم:", value=input.v1() if "v1" in input else ""), 
                ui.input_action_button("nxt1", "التالي ➡️", class_="btn-neon"), 
                class_="glass-card"
            )
        if step == 2:
            return ui.div(
                ui.h4("📺 الخطوة 2: شكل الشاشة", class_="neon-text"), 
                ui.input_select("v2", "اختر الشكل:", ["Notch Screen", "Punch Screen", "Curved Screen"], selected=input.v2() if "v2" in input else "Notch Screen"), 
                ui.input_action_button("nxt2", "التالي ➡️", class_="btn-neon"), 
                class_="glass-card"
            )
        if step == 3:
            return ui.div(
                ui.h4("🔌 الخطوة 3: نوع المستشعر", class_="neon-text"), 
                ui.input_select("v3", "اختر المستشعر المعتمد:", ["hardware", "under_display", "virtual"], selected=input.v3() if "v3" in input else "hardware"), 
                ui.input_action_button("fin", "✅ رفع وحفظ بـ Supabase", class_="btn-neon", style="background: linear-gradient(135deg, #2ecc71, #27ae60); color: white;"), 
                class_="glass-card"
            )
        return ui.div()

    @reactive.effect
    @reactive.event(input.nxt1)
    def _goto_step2(): 
        current_step.set(2)

    @reactive.effect
    @reactive.event(input.nxt2)
    def _goto_step3(): 
        current_step.set(3)

    @reactive.effect
    @reactive.event(input.fin)
    def _execute_cloud_save(): 
        model_name = input.search_query().strip()
        size = input.v1().strip() if "v1" in input else ""
        panel = input.v2() if "v2" in input else "Notch Screen"
        sensor = input.v3() if "v3" in input else "hardware"
        success = insert_model_to_supabase(model_name, size, panel, sensor)
        if success:
            trigger_refresh.set(trigger_refresh() + 1)
            current_step.set(0)
            ui.insert_ui(ui.HTML("<script>alert('تم الحفظ بنجاح بـ Supabase!');</script>"), selector="body", where="beforeEnd", immediate=True)
        else:
            ui.insert_ui(ui.HTML("<script>alert('خطأ أثناء عملية الحفظ!');</script>"), selector="body", where="beforeEnd", immediate=True)

app = App(app_ui, server)
