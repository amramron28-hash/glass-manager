import os
import requests
from html import escape
from shiny import App, ui, render, reactive
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. الإعدادات والربط السحابي
load_dotenv()

# ⚠️ تأكد من وضع رابط مشروعك الفعلي ومفتاحك الحديث الذي يبدأ بـ sb_publishable بدقة مكان النصوص أدناه
SUPABASE_URL = "https://supabase.co" 
SUPABASE_KEY = "sb_publishable_..." 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================================================================
# 2. الواجهة الرسومية (UI) - هيكلية الـ Glassmorphism المعزولة والمحصنة تماماً
# ==============================================================================
app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""
            /* الدارك مود والـ Glassmorphism الفاخر */
            body { 
                background: #0d1117; 
                color: #f5f6fa; 
                font-family: 'Segoe UI', system-ui, sans-serif; 
                margin: 0; 
            }
            
            /* حماية شريط العناوين والنقاط الثلاث لتبقى دائماً في الطبقة العليا */
            .header-bar { 
                display: flex; 
                justify-content: space-between; 
                padding: 15px 25px; 
                align-items: center; 
                background: rgba(13, 17, 23, 0.45); 
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border-bottom: 1px solid rgba(0, 191, 255, 0.2); 
                position: relative;
                z-index: 10005;
            }
            
            /* تحصين درج الإعدادات الجانبي فوق كل شيء in التطبيق */
            .drawer { 
                position: fixed; 
                top: 0; 
                left: -320px; 
                width: 290px; 
                height: 100%; 
                background: rgba(22, 27, 34, 0.9); 
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-right: 2px solid #00bfff; 
                transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
                z-index: 10010; 
                padding: 30px 25px; 
                box-shadow: 5px 0 30px rgba(0,0,0,0.7);
            }
            .drawer.open { left: 0; }
            
            /* حاويات الخطوات معزولة in موضع مستقر ومحمي من السقوط خلف الاقتراحات */
            .glass-card { 
                background: rgba(255, 255, 255, 0.05); 
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(0, 191, 255, 0.25); 
                border-radius: 20px; 
                padding: 30px; 
                margin: 25px auto; 
                width: 92%; 
                max-width: 500px; 
                box-shadow: 0 8px 32px 0 rgba(0, 191, 255, 0.15);
                position: relative;
                z-index: 999; 
            }
            
            .search-box { 
                position: relative; 
                max-width: 500px; 
                margin: auto; 
                padding: 25px 15px; 
                z-index: 500; 
            }
            
            /* قائمة الاقتراحات المخصصة محددة الطبقة تقع تحت صندوق البحث وفوق الخطوات */
            #custom_suggestions { 
                position: absolute; 
                width: calc(100% - 30px); 
                background: rgba(22, 27, 34, 0.95); 
                backdrop-filter: blur(10px);
                border: 1px solid #00bfff; 
                border-radius: 10px; 
                z-index: 998; 
                display: none; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.5);
                max-height: 250px;
                overflow-y: auto;
                margin-top: 5px;
            }
            
            .suggestion-item { 
                padding: 12px 20px; 
                border-bottom: 1px solid rgba(255,255,255,0.05); 
                cursor: pointer; 
                transition: 0.2s;
            }
            .suggestion-item:hover { 
                background: rgba(0, 191, 255, 0.15); 
                color: #00bfff; 
            }
            
            .btn-neon { 
                background: linear-gradient(135deg, #00bfff, #0080ff); 
                color: black; 
                border: none; 
                padding: 12px; 
                width: 100%; 
                border-radius: 10px; 
                font-weight: bold; 
                cursor: pointer;
                transition: 0.2s;
                box-shadow: 0 4px 15px rgba(0, 191, 255, 0.3);
            }
            .btn-neon:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 6px 20px rgba(0, 191, 255, 0.5); 
            }
            
            input[type="text"], select {
                background: rgba(255, 255, 255, 0.07) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                color: white !important;
                border-radius: 8px !important;
                padding: 11px 15px !important;
            }
            input[type="text"]:focus, select:focus {
                border-color: #00bfff !important;
                box-shadow: 0 0 10px rgba(0, 191, 255, 0.5) !important;
            }
            .neon-text { color: #00bfff; text-shadow: 0 0 8px rgba(0, 191, 255, 0.6); font-weight: 600; }
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
    ui.HTML('<div id="drawer" class="drawer">'),
    ui.h3("⚙️ الإعدادات السحابية", class_="neon-text"),
    ui.p("📊 إجمالي الموديلات الحية: ", ui.span(ui.output_text("model_count", inline=True), class_="neon-text")),
    ui.p("🔇 المراقب الصامت: نشط", style="margin: 15px 0; font-size:0.9rem; color:#888;"),
    ui.p("🔔 تنبيهات المتصل: مستقرة", style="margin: 15px 0; font-size:0.9rem; color:#888;"),
    ui.hr(style="border:0.5px solid rgba(0, 191, 255, 0.2); margin: 20px 0;"),
    ui.input_action_button("close_btn", "إغلاق النافذة", onclick="toggleDrawer()", class_="btn-neon", style="background:#e74c3c; color:white;"),
    ui.HTML('</div>'),
    ui.div(
        ui.HTML('<div style="cursor:pointer; font-size:28px; color:#00bfff;" onclick="toggleDrawer()">☰</div>'),
        ui.h2("ZEGAAR AMMAR", style="color:#00bfff; margin:0; font-size: 1.5rem; font-weight:600;"),
        ui.HTML('<div style="color:#00bfff; font-size:20px; cursor:pointer;">🔔</div>'),
        class_="header-bar"
    ),
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.HTML("<div id='custom_suggestions'></div>"),
        ui.output_ui("main_content_ui"),
        class_="search-box"
    )
)
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
