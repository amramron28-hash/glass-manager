import os
from html import escape
from shiny import App, render, reactive, ui
from ui import app_ui  # استيراد الواجهة من الملف الأول المطور

# 1. تهيئة مكتبة وأدوات اتصال Supabase السحابية
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("الرجاء التأكد من إعداد SUPABASE_URL و SUPABASE_KEY في إعدادات المنصة السحابية")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================================================================
# 2. دوال الاتصال المباشر بقاعدة البيانات لجدول phones
# ==============================================================================

def fetch_all_models_from_supabase():
    """جلب كافة الموديلات الحية من جدول phones في السحاب وتجهيزها للاقتراحات المخصصة"""
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
    """رفع البيانات السحابية مطابقة تماماً لأعمدة جدولك: size, panel, sensor"""
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
# 3. منطق السيرفر المتفاعل (Server Logic)
# ==============================================================================

def server(input, output, session):
    # مستشعر داخلي لإجبار الواجهة على جلب تحديثات البيانات السحابية فوراً عند إضافة موديل جديد
    trigger_refresh = reactive.value(0)
    current_step = reactive.value(0)
    
    # ذاكرة مؤقتة تفاعلية تحفظ الموديلات من Supabase لتسريع التصفية الفورية
    @reactive.calc
    def cloud_models():
        trigger_refresh()  # يتأثر تلقائياً عند تغيير قيمة المستشعر لإعادة الجلب
        return fetch_all_models_from_supabase()

    # محرك الاقتراحات المخصصة المتصل بـ Supabase
    @reactive.effect
    def _handle_suggestions():
        query = input.search_query().strip()
        if not query:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")
            return
        
        # جلب الموديلات الحقيقية من السيرفر السحابي
        models = cloud_models()
        filtered = [m for m in models if query.lower() in m.lower()]
        
        # تحويل الاقتراحات المفلترة لعناصر HTML تفاعلية آمنة
        items = "".join([f"<div class='suggestion-item' onclick=\"selectModel('{escape(m)}')\">{m}</div>" for m in filtered])
        
        if items:
            ui.update_html("custom_suggestions", content=items)
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'block';")
        else:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")

    # معالج واجهات خطوات الطوارئ والإضافة محمي بوضعية مستقرة من التداخل البصري
    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query:
            return ui.div()
            
        models_list = cloud_models()
        
        # إذا تطابق نص البحث مع موديل موجود سحابياً، يتم إغلاق معالج الخطوات وعرض بيانات الموديل فوراً
        if query in models_list:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display = 'none';")
            # [يمكنك هنا استدعاء محرك الـ workflow لعرض البيانات المسترجعة للمطابقة]
            return ui.div(ui.h4(f"✅ تم العثور على الموديل: {query}", style="color:#2ecc71;"), class_="glass-card")
            
        # تشغيل واجهة الطوارئ والخطوة الأولى تلقائياً عند عدم العثور على الموديل
        if query not in models_list and current_step() == 0: 
            current_step.set(1)
        
        step = current_step()
        
        if step == 1:
            return ui.div(
                ui.h4("📏 الخطوة 1: أدخل المقاس", style="color:#00bfff;"), 
                ui.input_text("v1", "المقاس الحجم:", value=input.v1() if "v1" in input else ""), 
                ui.input_action_button("nxt1", "التالي ➡️", class_="btn-neon"), 
                class_="glass-card"
            )
        if step == 2:
            return ui.div(
                ui.h4("📺 الخطوة 2: شكل الشاشة", style="color:#00bfff;"), 
                ui.input_select("v2", "اختر الشكل:", ["Notch Screen", "Punch Screen", "Curved Screen"], selected=input.v2() if "v2" in input else "Notch Screen"), 
                ui.input_action_button("nxt2", "التالي ➡️", class_="btn-neon"), 
                class_="glass-card"
            )
        if step == 3:
            return ui.div(
                ui.h4("🔌 الخطوة 3: نوع المستشعر", style="color:#00bfff;"), 
                ui.input_select("v3", "اختر المستشعر المعتمد:", ["hardware", "under_display", "virtual"], selected=input.v3() if "v3" in input else "hardware"), 
                ui.input_action_button("fin", "✅ رفع وحفظ بـ Supabase", class_="btn-neon", style="background: linear-gradient(135deg, #2ecc71, #27ae60); color: white;"), 
                class_="glass-card"
            )
        return ui.div()

    # التنقل السلس بين الخطوات السحابية
    @reactive.effect
    @reactive.event(input.nxt1)
    def _goto_step2(): 
        current_step.set(2)
        
    @reactive.effect
    @reactive.event(input.nxt2)
    def _goto_step3(): 
        current_step.set(3)
        
    # التنفيذ السحابي النهائي للمزامنة والحفظ وإعادة التصفير التلقائي للواجهات
    @reactive.effect
    @reactive.event(input.fin)
    def _execute_cloud_save(): 
        model_name = input.search_query().strip()
        size = input.v1().strip() if "v1" in input else ""
        panel = input.v2() if "v2" in input else "Notch Screen"
        sensor = input.v3() if "v3" in input else "hardware"
        
        # الرفع المباشر للأعمدة الصحيحة في جدول phones
        success = insert_model_to_supabase(model_name, size, panel, sensor)
        
        if success:
            # إجبار الكود على إعادة جلب البيانات وتحديث الاقتراحات السحابية فوراً
            trigger_refresh.set(trigger_refresh() + 1)
            current_step.set(0)
            
            ui.insert_ui(
                ui.HTML("<script>alert('تم رفع وحفظ الموديل الجديد بنجاح في قاعدة بيانات Supabase السحابية!');</script>"),
                selector="body",
                where="beforeEnd",
                immediate=True
            )
        else:
            ui.insert_ui(
                ui.HTML("<script>alert('خطأ أثناء عملية الحفظ! يرجى التحقق من اتصال السيرفر');</script>"),
                selector="body",
                where="beforeEnd",
                immediate=True
            )

app = App(app_ui, server)
