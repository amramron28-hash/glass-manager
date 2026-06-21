import os
import base64
from html import escape
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
        # استدعاء دالة الحقن الرسمية من ملفك ui_components.py
        ui.HTML(inject_pwa_and_styles()),
        ui.tags.style("""
            /* نظام الدارك مود وتأثير الزجاج الضبابي الفاخر */
            body { 
                background: #0d1117; 
                color: #f5f6fa; 
                font-family: 'Segoe UI', system-ui, sans-serif; 
                margin: 0; 
            }
            
            /* حل مشكلة اختفاء النقاط الثلاث عبر رفع طبقة شريط العناوين */
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
                z-index: 10005; /* تضمن بقاء الأزرار في الأعلى دائماً */
            }
            
            /* لوحة الإعدادات الجانبية محصنة فوق كل شيء في التطبيق */
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
            
            /* حاوية الخطوات بتصميم الـ Glassmorphism ومستقرة هندسياً لمنع الاختفاء */
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
                z-index: 999; /* تحمي أزرار الطوارئ والخطوات من السقوط خلف الاقتراحات المخصصة */
            }
            
            .search-box { 
                position: relative; 
                max-width: 500px; 
                margin: auto; 
                padding: 25px 15px; 
                z-index: 500; /* تضمن وجود مربع البحث تحت شريط القائمة الرئيسي */
            }
            
            /* قائمة الاقتراحات المخصصة معزولة لمنع تغطية الخطوات السفلى */
            #custom_suggestions { 
                position: absolute; 
                width: calc(100% - 30px); 
                background: rgba(22, 27, 34, 0.95); 
                backdrop-filter: blur(10px);
                border: 1px solid #00bfff; 
                border-radius: 10px; 
                z-index: 998; /* تقع تحت صندوق البحث وفوق بطاقة الخطوات بانسيابية */
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

    # لوحة الإعدادات الجانبية بتأثير الـ Glassmorphism
    ui.HTML("""<div id="drawer" class="drawer">
        <h3 class="neon-text" style="margin-bottom: 20px;">⚙️ الإعدادات السحابية</h3>
        <p style="margin: 15px 0;">⚡ الجدول المتصل: phones</p>
        <p style="margin: 15px 0;">🔔 جرس التنبيهات</p>
        <p style="margin: 15px 0;">🔇 المراقب الصامت</p>
        <hr style="border:0.5px solid rgba(0, 191, 255, 0.2); margin: 20px 0;">
        <p style="font-size: 1.05rem;">📊 إجمالي الموديلات: <span id="model_count" class="neon-text">...</span></p>
        <button onclick="toggleDrawer()" class="btn-neon" style="color: white; background: #e74c3c;">إغلاق</button>
    </div>"""),

    # شريط العناوين الثابت والمحمي تماماً من التداخل البصري
    ui.div(
        ui.HTML('<div style="cursor:pointer; font-size:28px; color:#00bfff;" onclick="toggleDrawer()">☰</div>'),
        ui.h2("ZEGAAR AMMAR", style="color:#00bfff; margin:0; font-size: 1.5rem; font-weight:600;"),
        ui.HTML('<div style="color:#00bfff; font-size:20px; cursor:pointer;">🔔</div>'), 
        class_="header-bar"
    ),

    # صندوق البحث المطور والواجهات المتفاعلة
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف...", attributes={"autocomplete": "off"}),
        ui.HTML("<div id='custom_suggestions'></div>"),
        ui.output_ui("main_content_ui"),
        class_="search-box"
    )
)

# ==============================================================================
# 5. منطق السيرفر المتفاعل (Server Logic)
# ==============================================================================

def server(input, output, session):
    # مستشعر داخلي لإجبار الواجهة على جلب تحديثات البيانات السحابية فوراً عند الإضافة
    trigger_refresh = reactive.value(0)
    current_step = reactive.value(0)
    
    # ذاكرة مؤقتة تفاعلية تحفظ الموديلات من Supabase لتسريع التصفية الفورية
    @reactive.calc
    def cloud_models():
        trigger_refresh()  
        return fetch_all_models_from_supabase()

    # تحديث إجمالي عدد الموديلات الحقيقي في درج الإعدادات الجانبي ديناميكياً
    @reactive.effect
    def _update_drawer_count():
        total = len(cloud_models())
        ui.insert_ui(
            ui.HTML(f"<script>document.getElementById('model_count').innerText = '{total}';</script>"),
            selector="#model_count",
            where="beforeBegin",
