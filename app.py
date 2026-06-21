import os
from html import escape
import base64
from shiny import App, ui, render, reactive

# 1. استيراد المكونات وسيرفرات الفحص من ملفات مشروعك المحفوظة في الذاكرة
from workflows import run_system_workflows
from ui_components import inject_pwa_and_styles

# 2. إعداد واستدعاء مكتبات الربط السحابي وإدارة المتغيرات السرية
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("الرجاء التأكد من إعداد SUPABASE_URL و SUPABASE_KEY في إعدادات المنصة السحابية")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================================================================
# 3. دوال الاتصال المباشر بقاعدة البيانات لجدول phones الحقيقي
# ==============================================================================

def fetch_all_models_from_supabase():
    """جلب كافة الموديلات الحية من جدول phones في السحاب وتجهيزها للاقتراحات"""
    try:
        response = supabase.table("phones").select("model_name").execute()
        records = response.data
        if records:
            raw_list = [r["model_name"] for r in records if r.get("model_name")]
            return sorted(list(set(raw_list)))
    except Exception as e:
        print(f"خطأ سحابي أثناء جلب البيانات: {e}")
    return []

def insert_model_to_supabase(model_name, size, panel, sensor):
    """رفع البيانات السحابية مطابقة تماماً لأعمدة جدولك الفعلية: size, panel, sensor"""
    try:
        data = {
            "model_name": model_name,
            "size": size,
            "panel": panel,   
            "sensor": sensor  
        }
        supabase.table("phones").insert(data).execute()
        return True
    except Exception as e:
        print(f"خطأ سحابي أثناء الرفع والحفظ: {e}")
        return False

# ==============================================================================
# 4. الواجهة الرسومية (UI) - معزولة كلياً ومحمية بالـ Glassmorphism
# ==============================================================================
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML(inject_pwa_and_styles()),
        ui.tags.style("""
            body { 
                background: #0d1117; 
                color: #f5f6fa; 
                font-family: 'Segoe UI', system-ui, sans-serif; 
                margin: 0; 
            }
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
            /* تصفير الـ autocomplete من خلال الجافاسكريبت بعد التحميل لتفادي خطأ الأكواد */
            document.addEventListener("DOMContentLoaded", function() {
                var searchInput = document.getElementById("search_query");
                if (searchInput) { searchInput.setAttribute("autocomplete", "off"); }
            });
        """)
    ),
    ui.HTML("""<div id="drawer" class="drawer">
        <h3 class="neon-text" style="margin-bottom: 20px;">⚙️ الإعدادات السحابية</h3>
        <p style="margin: 15px 0;">⚡ الجدول المتصل: phones</p>
        <p style="margin: 15px 0;">🔔 جرس التنبيهات</p>
        <p style="margin: 15px 0;">🔇 المراقب الصامت</p>
        <hr style="border:0.5px solid rgba(0, 191, 255, 0.2); margin: 20px 0;">
        <p style="font-size: 1.05rem;">📊 إجمالي الموديلات: <span id="model_count" class="neon-text">...</span></p>
        <button onclick="toggleDrawer()" class="btn-neon" style="color: white; background: #e74c3c;">إغلاق</button>
    </div>"""),
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
