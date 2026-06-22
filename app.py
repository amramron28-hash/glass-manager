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

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"تنبيه أمان: فشل تهيئة عميل السحاب: {e}")

# استدعاء الـ workflows والمكونات الأصلية
try:
    from workflows import render_system_workflow as run_system_workflows
except ImportError:
    try:
        from workflows import run_system_workflows
    except ImportError:
        def run_system_workflows(model, data, db):
            return f"<div class='glass-card'><h3 class='neon-text'>{model}</h3><p>Workflow غير متوفر</p></div>"

# مسارات ملفات الفهرس المحلي الفوري
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
# 2) الواجهة الرسومية الأصلية الموحدة (UI)
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
        .search-box { position: relative; max-width: 500px; margin: 30px auto; padding: 0 15px; }
        
        /* تصميم ستارة الاقتراحات التفاعلية الحية أسفل شريط البحث */
        .suggestions-curtain { position: absolute; width: calc(100% - 30px); background: #161b22; border: 1px solid #00bfff; border-radius: 10px; max-height: 220px; overflow-y: auto; z-index: 9999; margin-top: 5px; box-shadow: 0px 8px 16px rgba(0,0,0,0.5); }
        .suggestion-row { padding: 12px; cursor: pointer; text-align: right; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .suggestion-row:hover { background: rgba(0,191,255,0.15); color: #00bfff; }
        .form-group-custom { margin-bottom: 15px; }
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
        # العودة إلى شريط البحث النصي الفردي النقي والأنيق
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف...", width="100%"),
        ui.output_ui("suggestions_curtain_ui"), # الستارة الحية التفاعلية
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
    
    # إدارة الخطط منطقياً (0=البداية الحرة، 1=نجاح الاسم، 2=معالج المواصفات، 3=الطوارئ)
    current_plan = reactive.value(0)
    wizard_step = reactive.value(1) # خطوات الخطة 2 الداخلية

    # خيارات ديناميكية لـ (+)
    screen_options = reactive.value(["Notch", "Punch", "Curved"])
    sensor_options = reactive.value(["hardware", "under_display"])

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

    # التحكم في إغلاق وفتح الستارة عند اختيار اسم
    show_suggestions = reactive.value(True)

    @reactive.effect
    @reactive.event(input.search_query)
    def _():
        show_suggestions.set(True)
        if current_plan() != 0:
            current_plan.set(0)
    # ==========================================================
    # 4) منطق ستارة الاقتراحات التفاعلية الحية (مثل جوجل)
    # ==========================================================
    @render.ui
    def suggestions_curtain_ui():
        if not show_suggestions():
            return ui.div()
            
        q = input.search_query().strip().lower()
        if not q:
            return ui.div()
            
        # القراءة السريعة من الفهرس المحلي
        local_data = load_local_json()
        models = list(local_data.keys()) if local_data else [x.get("model_name") for x in cloud_database() if x.get("model_name")]
        
        # فلترة الأسماء لحظياً لتتقلص مع زيادة الحروف
        matches = [m for m in models if m and q in str(m).lower()][:8]
        
        if not matches:
            return ui.div()
            
        # بناء الستارة ديناميكياً بعناصر بايثون أصلية محميّة
        rows = []
        for m in matches:
            rows.append(
                ui.div(
                    f"📱 {m}", 
                    class_="suggestion-row", 
                    onclick=f"Shiny.setInputValue('selected_suggestion', '{m}', {{priority: 'event'}});"
                )
            )
        return ui.div(*rows, class_="suggestions-curtain")

    # عند النقر على خيار من الستارة، يتم تحديث شريط البحث وإخفاء الستارة فوراً
    @reactive.effect
    @reactive.event(input.selected_suggestion)
    def _():
        choice = input.selected_suggestion()
        ui.update_text("search_query", value=choice)
        show_suggestions.set(False)

    # ==========================================================
    # 5) إدارة الخطط بالتسلسل الصارم (الخطة 1 و 2 و 3)
    # ==========================================================
    @reactive.effect
    @reactive.event(input.btn_search)
    def _():
        show_suggestions.set(False)
        query = input.search_query().strip()
        if not query:
            ui.notification_show("الرجاء كتابة اسم الموديل أولاً!", type="warning")
            return
            
        db = cloud_database()
        # مقارنة مرنة (تحويل الأحرف لصغيرة لتفادي أخطاء حالة الحروف)
        phone = next((x for x in db if str(x.get("model_name")).strip().lower() == query.lower()), None)
        
        if phone:
            # بوابات صارمة: تفعيل الخطة 1 بنجاح وإقفال البقية
            current_plan.set(1)
        else:
            # الخطة 1 فشلت تماماً قف! -> افتح بوابة الخطة 2 بشكل منعزل
            ui.notification_show("الموديل غير مدرج بالاسم. ننتقل لفحص المواصفات (الخطة 2)", type="warning")
            current_plan.set(2)
            wizard_step.set(1)

    # ----------------------------------------------------------
    # نوافذ الزيادة الفرعية الآمنة (Modal Dialogs) لتفعيل أزرار (+)
    # ----------------------------------------------------------
    @reactive.effect
    @reactive.event(input.add_screen_btn)
    def _():
        ui.modal_show(ui.modal(
            ui.input_text("new_screen_name", "أدخل شكل الشاشة الجديد:"),
            ui.input_action_button("save_new_screen", "تأكيد الإضافة ➕", class_="btn-neon"),
            title="إضافة شكل شاشة جديد", easy_close=True
        ))

    @reactive.effect
    @reactive.event(input.save_new_screen)
    def _():
        new_val = input.new_screen_name().strip()
        if new_val and new_val not in screen_options():
            screen_options.set(screen_options() + [new_val])
            ui.notification_show(f"تمت إضافة '{new_val}' مؤقتاً لقائمة الخيارات", type="message")
        ui.modal_remove()

    @reactive.effect
    @reactive.event(input.add_sensor_btn)
    def _():
        ui.modal_show(ui.modal(
            ui.input_text("new_sensor_name", "أدخل نوع المستشعر الجديد:"),
            ui.input_action_button("save_new_sensor", "تأكيد الإضافة ➕", class_="btn-neon"),
            title="إضافة نوع مستشعر جديد", easy_close=True
        ))

    @reactive.effect
    @reactive.event(input.save_new_sensor)
    def _():
        new_val = input.new_sensor_name().strip()
        if new_val and new_val not in sensor_options():
            sensor_options.set(sensor_options() + [new_val])
            ui.notification_show(f"تمت إضافة '{new_val}' مؤقتاً لقائمة الخيارات", type="message")
        ui.modal_remove()

    # ----------------------------------------------------------
    # حركة المعالج المنفصل التابع للخطة 2
    # ----------------------------------------------------------
    @reactive.effect
    @reactive.event(input.next1)
    def _():
        if not input.v1().strip():
            ui.notification_show("يرجى إدخال المقاس يدوياً أولاً!", type="error")
            return
        wizard_step.set(2)

    @reactive.effect
    @reactive.event(input.next2)
    def _():
        wizard_step.set(3)

    # فحص التطابق الثلاثي الصارم (Strict Matching) في نهاية الخطة 2
    @reactive.effect
    @reactive.event(input.check_spec_match)
    def _():
        db = cloud_database()
        size_in = input.v1().strip()
        panel_in = input.v2()
        sensor_in = input.v3()
        
        matches = [
            x for x in db 
            if str(x.get("size")).strip() == size_in 
            and str(x.get("panel")).strip().lower() == panel_in.lower() 
            and str(x.get("sensor")).strip().lower() == sensor_in.lower()
        ]
        
        if matches:
            # الخطة 2 نجحت: عرض الهواتف المطابقة في نفس المجموعة
            current_plan.set(22)
        else:
            # الخطة 2 فشلت تماماً قف! -> افتح بوابة خطة الطوارئ 3 (مجموعة جديدة كلياً)
            ui.notification_show("لا توجد هواتف تطابق هذه المواصفات. خطة الطوارئ 3 تفتح تلقائياً!", type="error")
            current_plan.set(3)

    # ----------------------------------------------------------
    # الخطة 3 (خطة الطوارئ): الحفظ المزدوج والتحديث التلقائي
    # ----------------------------------------------------------
    @reactive.effect
    @reactive.event(input.emergency_save)
    def _():
        query = input.search_query().strip()
        size_in = input.v1().strip()
        panel_in = input.v2()
        sensor_in = input.v3()
        
        try:
            # 1. الحفظ السحابي التلقائي
            supabase.table("phones").insert({
                "model_name": query,
                "size": size_in,
                "panel": panel_in,
                "sensor": sensor_in
            }).execute()
            
            # 2. الحفظ المحلي المزدوج في الـ JSON
            local_data = load_local_json()
            local_data[query] = {
                "1_size": size_in,
                "2_screen_shape": panel_in,
                "3_sensor_type": sensor_in
            }
            save_local_json(local_data)
            
            ui.notification_show("تم حفظ المجموعة الجديدة تلقائياً بالسحاب والملف بنجاح!", type="message")
            refresh_trigger.set(refresh_trigger() + 1)
            current_plan.set(0)
            ui.update_text("search_query", value="")
            
        except Exception as e:
            ui.notification_show(f"فشل الحفظ التلقائي: {e}", type="error")

    # ==========================================================
    # 6) بناء وعرض واجهات الخطط المنفصلة (Render HTML UI)
    # ==========================================================
    @render.ui
    def main_content_ui():
        plan = current_plan()
        query = input.search_query().strip()
        
        if not query or show_suggestions():
            return ui.div()
            
        # الخطة 1: عرض البطاقات الملونة الجمالية
        if plan == 1:
            db = cloud_database()
            phone = next((x for x in db if str(x.get("model_name")).strip().lower() == query.lower()), None)
            # استدعاء دالة الـ Workflow المباشرة لرسم البطاقات الملونة
            try:
                return ui.HTML(run_system_workflows(query, phone, db))
            except:
                return ui.div(ui.h3(f"📱 {query}", class_="neon-text"), ui.p("تم العثور عليه بنجاح!"), class_="glass-card")
            
        # الخطة 2: نوافذ معالج المواصفات المنعزلة (نافذة تلو الأخرى)
        if plan == 2:
            step = wizard_step()
            if step == 1:
                return ui.div(
                    ui.h4("📏 الخطة 2 - نافذة المقاس", class_="neon-text"),
                    ui.input_text("v1", "أدخل مقاس الشاشة يدوياً (مثال: 6.7):", value=""),
                    ui.input_action_button("next1", "التالي (شكل الشاشة) ➡️", class_="btn-neon"),
                    class_="glass-card"
                )
            elif step == 2:
                return ui.div(
                    ui.h4("📺 الخطة 2 - نافذة شكل الشاشة", class_="neon-text"),
                    ui.div(
                        ui.input_select("v2", "اختر الشكل الحركي:", choices=screen_options()),
                        ui.input_action_button("add_screen_btn", "➕", class_="btn-plus"),
                        class_="form-group-custom"
                    ),
                    ui.input_action_button("next2", "التالي (نوع المستشعر) ➡️", class_="btn-neon"),
                    class_="glass-card"
                )
            elif step == 3:
                return ui.div(
                    ui.h4("🔌 الخطة 2 - نافذة مستشعر التقارب", class_="neon-text"),
                    ui.div(
                        ui.input_select("v3", "اختر نوع المستشعر الحالي:", choices=sensor_options()),
                        ui.input_action_button("add_sensor_btn", "➕", class_="btn-plus"),
                        class_="form-group-custom"
                    ),
                    ui.input_action_button("check_spec_match", "فحص وإدراج بالمجموعة 🔍", class_="btn-neon"),
                    class_="glass-card"
                )

        # الخطة 22: نجاح الفحص بالمواصفات وعرض الهواتف المطابقة في نفس المجموعة
        if plan == 22:
            db = cloud_database()
            size_in = input.v1().strip()
            panel_in = input.v2()
            sensor_in = input.v3()
            matches = [
                x for x in db 
            if str(x.get("size")).strip() == size_in 
            and str(x.get("panel")).strip().lower() == panel_in.lower() 
            and str(x.get("sensor")).strip().lower() == sensor_in.lower()
        ]
        
        if matches:
            current_plan.set(22)
        else:
            ui.notification_show("لا توجد هواتف تطابق هذه المواصفات. خطة الطوارئ 3 تفتح تلقائياً!", type="error")
            current_plan.set(3)

    # ----------------------------------------------------------
    # الخطة 3 (خطة الطوارئ): الحفظ المزدوج والتحديث التلقائي
    # ----------------------------------------------------------
    @reactive.effect
    @reactive.event(input.emergency_save)
    def _():
        query = input.search_query().strip()
        size_in = input.v1().strip()
        panel_in = input.v2()
        sensor_in = input.v3()
        
        try:
            supabase.table("phones").insert({
                "model_name": query,
                "size": size_in,
                "panel": panel_in,
                "sensor": sensor_in
            }).execute()
            
            local_data = load_local_json()
            local_data[query] = {
                "1_size": size_in,
                "2_screen_shape": panel_in,
                "3_sensor_type": sensor_in
            }
            save_local_json(local_data)
            
            ui.notification_show("تم حفظ المجموعة الجديدة تلقائياً بالسحاب والملف بنجاح!", type="message")
            refresh_trigger.set(refresh_trigger() + 1)
            current_plan.set(0)
            ui.update_text("search_query", value="")
            
        except Exception as e:
            ui.notification_show(f"فشل الحفظ التلقائي: {e}", type="error")

    # ==========================================================
    # 6) بناء وعرض واجهات الخطط المنفصلة (تابع الـ Render UI)
    # ==========================================================
    @render.ui
    def main_content_ui():
        plan = current_plan()
        query = input.search_query().strip()
        
        if not query or show_suggestions():
            return ui.div()
            
        if plan == 1:
            db = cloud_database()
            phone = next((x for x in db if str(x.get("model_name")).strip().lower() == query.lower()), None)
            try:
                return ui.HTML(run_system_workflows(query, phone, db))
            except:
                return ui.div(ui.h3(f"📱 {query}", class_="neon-text"), ui.p("تم العثور عليه بنجاح!"), class_="glass-card")
            
        if plan == 2:
            step = wizard_step()
            if step == 1:
                return ui.div(
                    ui.h4("📏 الخطة 2 - نافذة المقاس", class_="neon-text"),
                    ui.input_text("v1", "أدخل مقاس الشاشة يدوياً (مثال: 6.7):", value=""),
                    ui.input_action_button("next1", "التالي (شكل الشاشة) ➡️", class_="btn-neon"),
                    class_="glass-card"
                )
            elif step == 2:
                return ui.div(
                    ui.h4("📺 الخطة 2 - نافذة شكل الشاشة", class_="neon-text"),
                    ui.div(
                        ui.input_select("v2", "اختر الشكل الحركي:", choices=screen_options()),
                        ui.input_action_button("add_screen_btn", "➕", class_="btn-plus"),
                        class_="form-group-custom"
                    ),
                    ui.input_action_button("next2", "التالي (نوع المستشعر) ➡️", class_="btn-neon"),
                    class_="glass-card"
                )
            elif step == 3:
                return ui.div(
                    ui.h4("🔌 الخطة 2 - نافذة مستشعر التقارب", class_="neon-text"),
                    ui.div(
                        ui.input_select("v3", "اختر نوع المستشعر الحالي:", choices=sensor_options()),
                        ui.input_action_button("add_sensor_btn", "➕", class_="btn-plus"),
                        class_="form-group-custom"
                    ),
                    ui.input_action_button("check_spec_match", "فحص وإدراج بالمجموعة 🔍", class_="btn-neon"),
                    class_="glass-card"
                )

        if plan == 22:
            db = cloud_database()
            size_in = input.v1().strip()
            panel_in = input.v2()
            sensor_in = input.v3()
            matches = [
                x for x in db 
                if str(x.get("size")).strip() == size_in 
                and str(x.get("panel")).strip().lower() == panel_in.lower() 
                and str(x.get("sensor")).strip().lower() == sensor_in.lower()
            ]
            html_list = "".join([f"<li style='margin: 8px 0;'>📱 {m.get('model_name')}</li>" for m in matches])
            return ui.div(
                ui.h4("📌 الهواتف المندرجة تحت نفس المجموعة والمواصفات:", class_="neon-text"),
                ui.HTML(f"<ul style='list-style-type: none; padding: 0;'>{html_list}</ul>"),
                class_="glass-card"
            )

        if plan == 3:
            return ui.div(
                ui.h4("🚨 خطة الطوارئ: اعتماد مجموعة فريدة جديدة كلياً", style="color: #ff4500;"),
                ui.p(f"اسم الموديل الجديد: {query}"),
                ui.p(f"المقاس: {input.v1()} | الشاشة: {input.v2()} | المستشعر: {input.v3()}"),
                ui.input_action_button("emergency_save", "تأكيد وحفظ تلقائي (سحاب + ملف) 💾", class_="btn-neon", style="background:#ff4500; color:white;"),
                class_="glass-card"
            )
            
        return ui.div()

# ==========================================================
# تشغيل التطبيق بالبنية المصلحة مئة بالمئة
# ==========================================================
app = App(app_ui, server)

