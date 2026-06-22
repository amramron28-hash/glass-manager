import os
import json
from shiny import App, ui, render, reactive
from supabase import create_client, Client
from dotenv import load_dotenv

# ==========================================================
# 1) إعداد Supabase والحماية
# ==========================================================
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# إنشاء عميل السحاب بأمان
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"تنبيه أمان: فشل تهيئة عميل السحاب، تأكد من المتغيرات البيئية: {e}")

# استدعاء الـ workflows الاحتياطية
try:
    from workflows import run_system_workflows
except ImportError:
    def run_system_workflows(model, data, db):
        return f"<div class='glass-card'><h3 class='neon-text'>{model}</h3><p>Workflow غير متوفر</p></div>"

# مسار ملف الـ JSON المحلي للتخمينات
JSON_INDEX_PATH = "models_id_db.json"

def load_local_json():
    if os.path.exists(JSON_INDEX_PATH):
        try:
            with open(JSON_INDEX_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_local_json(data):
    try:
        with open(JSON_INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ أثناء تحديث الفهرس المحلي: {e}")

# ==========================================================
# 2) الواجهة الرسومية (UI)
# ==========================================================
app_ui = ui.page_fluid(
    ui.head_content(ui.tags.style("""
        body { background:#0d1117; color:white; font-family:'Segoe UI',sans-serif; direction: rtl; }
        .header-bar { display:flex; justify-content:space-between; align-items:center; padding:15px 25px; background:rgba(13,17,23,.55); backdrop-filter:blur(12px); border-bottom:1px solid rgba(0,191,255,.25); }
        .drawer { position:fixed; top:0; right:-320px; width:290px; height:100%; background:rgba(22,27,34,.95); backdrop-filter:blur(20px); border-left:2px solid #00bfff; transition:.4s; z-index:20000; padding:30px; }
        .drawer.open { right:0; }
        .glass-card { background:rgba(255,255,255,.05); backdrop-filter:blur(15px); border:1px solid rgba(0,191,255,.3); border-radius:20px; padding:25px; margin:25px auto; max-width:500px; }
        .neon-text { color:#00bfff; }
        .btn-neon { width:100%; padding:12px; border-radius:10px; border:none; background:#00bfff; font-weight:bold; cursor:pointer; color:black; margin-top:10px; }
        .btn-plus { background:#21262d; color:#00bfff; border:1px solid #00bfff; border-radius:5px; padding:2px 10px; font-weight:bold; cursor:pointer; margin-top:5px; display:inline-block; }
        .search-box { max-width: 500px; margin: 30px auto; padding: 0 15px; }
        .form-group-custom { margin-bottom: 15px; }
        .flex-container { display: flex; align-items: center; justify-content: space-between; }
    """)),
    ui.HTML('<div id="drawer" class="drawer">'),
    ui.h3("⚙️ Supabase", class_="neon-text"),
    ui.output_text("model_count_display"),
    ui.HTML("</div>"),
    ui.div(
        ui.HTML('<div onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')" style="font-size:28px;cursor:pointer;color:#00bfff">☰</div>'), 
        ui.h2("ZEGAAR AMMAR", style="color:#00bfff"), 
        class_="header-bar"
    ),
    ui.div(
        # تم استبدال حقل النص العادي بقائمة تخمين مدمجة وآمنة تمنع الكراش
        ui.input_selectize("search_query", "ابحث أو اكتب موديل الهاتف الجديد...", choices=[], options={"create": True, "placeholder": "اكتب هنا واضغط Enter..."}),
        ui.input_action_button("btn_search", "افحص الهاتف 🔍", class_="btn-neon"),
        ui.output_ui("main_content_ui"), 
        class_="search-box"
    )
)

# ==========================================================
# 3) بداية السيرفر (Server)
# ==========================================================
def server(input, output, session):
    refresh_trigger = reactive.value(0)
    
    # إدارة الخطط منطقياً (0 = البداية، 1 = الخطة1، 2 = الخطة2، 3 = الخطة3 الطوارئ)
    current_plan = reactive.value(0)
    wizard_step = reactive.value(1) # الخطوات الداخلية للخطة 2 (1=مقاس، 2=شاشة، 3=مستشعر)

    # قوائم الخيارات الديناميكية التي يمكن تمديدها بـ (+)
    screen_options = reactive.value(["Notch", "Punch", "Curved"])
    sensor_options = reactive.value(["hardware", "under_display"])

    # قراءة سحابية آمنة
    @reactive.calc
    def cloud_database():
        refresh_trigger.get()
        try:
            res = supabase.table("phones").select("*").execute()
            return res.data if hasattr(res, 'data') else []
        except Exception as e: 
            print(f"خطأ شبكة في السحاب: {e}")
            return []

    @render.text
    def model_count_display():
        return f"📱 عدد الموديلات بالسحاب: {len(cloud_database())}"

    # مزامنة وتحديث قائمة التخمينات من الملف المحلي بشكل حي وآمن
    @reactive.effect
    def _():
        refresh_trigger.get()
        local_data = load_local_json()
        models = list(local_data.keys())
        ui.update_selectize("search_query", choices=models, server=True)
    # ==========================================================
    # 4) منطق تفاعل الخطط المتسلسلة (الخطة 1 و 2 و 3)
    # ==========================================================
    
    # عند الضغط على زر "افحص الهاتف" تبدأ الخطة 1
    @reactive.effect
    @reactive.event(input.btn_search)
    def _():
        query = input.search_query().strip()
        if not query:
            ui.notification_show("الرجاء كتابة أو اختيار اسم الهاتف أولاً!", type="warning")
            return
            
        db = cloud_database()
        phone = next((x for x in db if str(x.get("model_name")).lower() == query.lower()), None)
        
        if phone:
            # الخطة 1: نجاح العثور بالاسم
            current_plan.set(1)
            ui.notification_show("تم العثور على الهاتف بنجاح في السحاب! (الخطة 1)", type="message")
        else:
            # الخطة 1: فشل العثور بالاسم -> الانتقال التلقائي للخطة 2 قف!
            ui.notification_show("لم يتم العثور على الاسم. ننتقل لفحص المواصفات... (الخطة 2)", type="warning")
            current_plan.set(2)
            wizard_step.set(1)

    # ----------------------------------------------------------
    # نوافذ الزيادة الفرعية الحية (Modal Dialogs) لتفعيل أزرار (+)
    # ----------------------------------------------------------
    @reactive.effect
    @reactive.event(input.add_screen_btn)
    def _():
        ui.modal_show(ui.modal(
            ui.input_text("new_screen_name", "أدخل شكل الشاشة المبتكر الجديد:"),
            ui.input_action_button("save_new_screen", "تأكيد الإضافة ➕", class_="btn-neon"),
            title="إضافة شكل شاشة جديد", easy_close=True
        ))

    @reactive.effect
    @reactive.event(input.save_new_screen)
    def _():
        new_val = input.new_screen_name().strip()
        if new_val and new_val not in screen_options():
            screen_options.set(screen_options() + [new_val])
            ui.update_select("v2", choices=screen_options(), selected=new_val)
            ui.notification_show(f"تمت إضافة '{new_val}' إلى الخيارات مؤقتاً", type="message")
        ui.modal_remove()

    @reactive.effect
    @reactive.event(input.add_sensor_btn)
    def _():
        ui.modal_show(ui.modal(
            ui.input_text("new_sensor_name", "أدخل نوع المستشعر الجديد في الأسواق:"),
            ui.input_action_button("save_new_sensor", "تأكيد الإضافة ➕", class_="btn-neon"),
            title="إضافة نوع مستشعر جديد", easy_close=True
        ))

    @reactive.effect
    @reactive.event(input.save_new_sensor)
    def _():
        new_val = input.new_sensor_name().strip()
        if new_val and new_val not in sensor_options():
            sensor_options.set(sensor_options() + [new_val])
            ui.update_select("v3", choices=sensor_options(), selected=new_val)
            ui.notification_show(f"تمت إضافة '{new_val}' إلى الخيارات مؤقتاً", type="message")
        ui.modal_remove()

    # ----------------------------------------------------------
    # محرك تحريك معالج الخطة 2 (Wizard Step Control)
    # ----------------------------------------------------------
    @reactive.effect
    @reactive.event(input.next1)
    def _():
        if not input.v1().strip():
            ui.notification_show("يرجى إدخال مقاس الشاشة أولاً!", type="error")
            return
        wizard_step.set(2)

    @reactive.effect
    @reactive.event(input.next2)
    def _():
        wizard_step.set(3)

    # فحص التطابق الثلاثي الكامل للخصائص في نهاية الخطة 2
    @reactive.effect
    @reactive.event(input.check_spec_match)
    def _():
        db = cloud_database()
        size_in = input.v1().strip()
        panel_in = input.v2()
        sensor_in = input.v3()
        
        # البحث بأسلوب Strict Matching (التطابق الكامل للثلاثة خصائص معاً)
        matches = [
            x for x in db 
            if str(x.get("size")) == size_in 
            and str(x.get("panel")).lower() == panel_in.lower() 
            and str(x.get("sensor")).lower() == sensor_in.lower()
        ]
        
        if matches:
            # الخطة 2: نجاح! عثرنا على هواتف تطابق نفس المواصفات والمجموعة
            current_plan.set(22) # رمز خاص لعرض الهواتف المطابقة في المواصفات
            ui.notification_show("تم العثور على مجموعة هواتف تطابق هذه المواصفات تماماً!", type="message")
        else:
            # الخطة 2: فشل! قف هنا، انتقل فوراً لخطة الطوارئ 3 (مجموعة جديدة كلياً)
            ui.notification_show("مواصفات فريدة! لا يوجد تطابق. ننتقل لخطة الطوارئ 3...", type="warning")
            current_plan.set(3)

    # ----------------------------------------------------------
    # الخطة 3 (خطة الطوارئ): الحفظ التلقائي المزدوج في السحاب والملف
    # ----------------------------------------------------------
    @reactive.effect
    @reactive.event(input.emergency_save)
    def _():
        query = input.search_query().strip()
        size_in = input.v1().strip()
        panel_in = input.v2()
        sensor_in = input.v3()
        
        try:
            # 1. الإرسال والحفظ في سحابة Supabase تلقائياً
            supabase.table("phones").insert({
                "model_name": query,
                "size": size_in,
                "panel": panel_in,
                "sensor": sensor_in
            }).execute()
            
            # 2. الحفظ التلقائي المزدوج وتحديث شجرة الـ JSON المحلية
            local_data = load_local_json()
            local_data[query] = {
                "1_size": size_in,
                "2_screen_shape": panel_in,
                "3_sensor_type": sensor_in
            }
            save_local_json(local_data)
            
            # تحديث الواجهة والرجوع لحالة الصفر والجاهزية بنجاح
            ui.notification_show("تم تسجيل المجموعة الجديدة تلقائياً في السحاب والملف المحلي بنجاح!", type="message")
            refresh_trigger.set(refresh_trigger() + 1)
            current_plan.set(0)
            
        except Exception as e:
            ui.notification_show(f"خطأ أثناء الحفظ في الطوارئ: {e}", type="error")

    # ==========================================================
    # 5) بناء محتوى الواجهة التفاعلية (Render HTML UI)
    # ==========================================================
    @render.ui
    def main_content_ui():
        plan = current_plan()
        query = input.search_query().strip()
        
        if not query:
            return ui.div()
            
        # الحالة 1: نجاح الخطة 1 وعرض الـ Workflow المباشر للهاتف
        if plan == 1:
            db = cloud_database()
            phone = next((x for x in db if str(x.get("model_name")).lower() == query.lower()), None)
            return ui.HTML(run_system_workflows(query, phone, db))
            
        # الحالة 2: جاري تشغيل معالج مواصفات الخطة 2 بالتسلسل
        if plan == 2:
            step = wizard_step()
            if step == 1:
                return ui.div(
                    ui.h4("📏 الخطة 2 - الخطوة 1: المقاس اليدوي", class_="neon-text"),
                    ui.input_text("v1", "أدخل مقاس الشاشة بدقة:", placeholder="مثال: 6.7"),
                    ui.input_action_button("next1", "التالي (شكل الشاشة) ➡️", class_="btn-neon"),
                    class_="glass-card"
                )
            elif step == 2:
                return ui.div(
                    ui.h4("📺 الخطة 2 - الخطوة 2: شكل الشاشة", class_="neon-text"),
                    ui.div(
                        ui.input_select("v2", "اختر الشكل الحالي:", choices=screen_options()),
                        ui.input_action_button("add_screen_btn", "+ إضافة شكل مبتكر", class_="btn-plus"),
                        class_="form-group-custom"
                    ),
                    ui.input_action_button("next2", "التالي (المستشعر) ➡️", class_="btn-neon"),
                    class_="glass-card"
                )
            elif step == 3:
                return ui.div(
                    ui.h4("🔌 الخطة 2 - الخطوة 3: مستشعر التقارب", class_="neon-text"),
                    ui.div(
                        ui.input_select("v3", "اختر نوع المستشعر:", choices=sensor_options()),
                        ui.input_action_button("add_sensor_btn", "+ إضافة نوع مستشعر", class_="btn-plus"),
                        class_="form-group-custom"
                    ),
                    ui.input_action_button("check_spec_match", "فحص تطابق المجموعة 🔍", class_="btn-neon"),
                    class_="glass-card"
                )

        # الحالة 22: نجاح الفحص بالمواصفات وعرض المجموعة المطابقة
        if plan == 22:
            db = cloud_database()
            size_in = input.v1().strip()
            panel_in = input.v2()
            sensor_in = input.v3()
            matches = [
                x for x in db 
                if str(x.get("size")) == size_in 
                and str(x.get("panel")).lower() == panel_in.lower() 
                and str(x.get("sensor")).lower() == sensor_in.lower()
            ]
            html_list = "".join([f"<li>📱 {m.get('model_name')}</li>" for m in matches])
            return ui.div(
                ui.h4("📌 الهواتف المطابقة لنفس المجموعة والمواصفات:", class_="neon-text"),
                ui.HTML(f"<ul>{html_list}</ul>"),
                class_="glass-card"
            )

        # الحالة 3: فتح خطة الطوارئ الكاملة لاعتماد مجموعة فريدة وجديدة كلياً
        if plan == 3:
            return ui.div(
                ui.h4("🚨 خريطة الطوارئ: تسجيل مجموعة جديدة كلياً", style="color: #ff4500;"),
                ui.p(f"اسم الهاتف الجديد: {query}"),
                ui.p(f"المقاس المستهدف: {input.v1()}"),
                ui.p(f"شكل الشاشة: {input.v2()}"),
                ui.p(f"نوع المستشعر: {input.v3()}"),
                ui.input_action_button("emergency_save", "تأكيد وحفظ تلقائي في السحابة والملف 💾", class_="btn-neon", style="background: #ff4500; color: white;"),
                class_="glass-card"
            )
            
        return ui.div()

# ==========================================================
# تشغيل التطبيق بالهيكلية المحمية
