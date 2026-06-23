import os
from shiny import App, ui, render, reactive
from supabase import create_client

from workflows import run_system_workflows, get_compatibles_strict
from ui_components import (
    inject_pwa_and_styles, 
    draw_plan_2_modal, 
    draw_plan_3_modal,
    draw_technical_coords,
    draw_neon_section
)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def convert_database(rows):
    db = {}
    for item in rows:
        size = str(item.get("size", "")).strip()
        panel = str(item.get("panel", "")).strip()
        sensor = str(item.get("sensor", "")).strip()
        model = str(item.get("model_name", "")).strip()

        if not size or not model:
            continue

        db.setdefault(size, {})
        db[size].setdefault(panel, {})
        db[size][panel].setdefault(sensor, {"models": []})

        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)
    return db

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),

    ui.HTML("""
<script>
function openDrawer(){
    let d = document.getElementById('settings_drawer');
    if(d) d.classList.add('open');
}
function closeDrawer(){
    let d = document.getElementById('settings_drawer');
    if(d) d.classList.remove('open');
}
</script>
"""),

    # نافذة الإعدادات الجانبية (Drawer)
    ui.div(
        ui.h3("⚙️ الإعدادات", style="color:#00bfff; text-align:right;"),
        ui.div("🔔 الإشعارات نشطة", class_="metric-box"),
        ui.div("🛡️ المراقب الصامت يعمل", class_="metric-box"),
        ui.input_action_button("close_drawer", "إغلاق", class_="btn-neon", style="width:100%;"),
        id="settings_drawer",
        class_="drawer"
    ),

    # الهيدر العلوي والتطبيق
    ui.div(
        ui.div(
            ui.h2("ZEGAAR AMMAR", style="color:#00bfff; margin:0; font-weight:900;"),
            ui.h3("GLASS MANAGER", style="color:white; margin:0; letter-spacing:2px;"),
        ),
        ui.input_action_button("btn_settings", "⚙️", class_="btn-neon", style="font-size:20px; padding:10px 15px;"),
        class_="header-bar"
    ),

    # صندوق البحث والستارة الذكية
    ui.div(
        ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."),
        ui.output_ui("suggestions_curtain"),
        class_="search-box"
    ),

    # مناطق العرض الديناميكية للنظام والخطط التفاعلية
    ui.output_ui("results_area"),
    ui.output_ui("modal_layer")
)

def server(input, output, session):
    
    # حوافظ وقيم تفاعلية لإدارة تدفق العمليات
    db_trigger = reactive.Value(0)
    current_search_phone = reactive.Value("")
    show_curtain = reactive.Value(True)
    active_modal = reactive.Value(None)  # يمكن أن يكون 'plan_2' أو 'plan_3' أو None
    
    # القوائم الديناميكية المحدثة للأشكال والحساسات المضافة عبر زر +
    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])

    @reactive.calc
    def cloud_rows():
        db_trigger()  # تفعيل إعادة الجلب تلقائياً عند تحديث قاعدة البيانات
        try:
            response = supabase.table("phones").select("*").execute()
            return response.data or []
        except Exception as e:
            print("Supabase Error:", e)
            return []

    @reactive.calc
    def database():
        return convert_database(cloud_rows())

    # استخراج كافة أنواع الشاشات الفريدة في قاعدة البيانات للمنسدلة
    @reactive.calc
    def unique_panels():
        panels = set(str(row.get("panel", "")).strip() for row in cloud_rows())
        panels.update(custom_panels())
        return sorted(list(panels))

    # استخراج كافة المستشعرات الصارمة الفريدة لقاعدة بيانات شاومي وغيرها
    @reactive.calc
    def unique_sensors():
        sensors = set(str(row.get("sensor", "")).strip() for row in cloud_rows())
        sensors.update(custom_sensors())
        return sorted(list(sensors))

    # أحداث الـ Drawer الجانبي
    @reactive.effect
    @reactive.event(input.btn_settings)
    def open_drawer():
        ui.insert_ui(ui.HTML("<script>openDrawer();</script>"), selector="body")

    @reactive.effect
    @reactive.event(input.close_drawer)
    def close_drawer():
        ui.insert_ui(ui.HTML("<script>closeDrawer();</script>"), selector="body")

    # رصد نص البحث وإعادة فتح الستارة عند طباعة حرف جديد
    @reactive.effect
    @reactive.event(input.search_query)
    def track_search():
        show_curtain.set(True)

    # ستارة الاقتراحات الذكية والتحكم بظهورها واختفائها التلقائي
    @render.ui
    def suggestions_curtain():
        if not show_curtain():
            return None
            
        q = input.search_query().strip().lower()
        if not q:
            return None

        matches = []
        for row in cloud_rows():
            name = str(row.get("model_name", ""))
            if q in name.lower():
                matches.append(name)

        matches = list(dict.fromkeys(matches))[:8]
        if not matches:
            return None

        return ui.div(
            *[
                ui.div(
                    name,
                    class_="suggestion-row",
                    onclick=f"Shiny.setInputValue('selected_model', '{name}', {{priority: 'event'}});"
                )
                for name in matches
            ],
            class_="suggestions-curtain"
        )

    # عند الضغط على موديل من الاقتراحات: نملأ حقل البحث ونغلق الستارة فوراً
    @reactive.effect
    @reactive.event(input.selected_model)
    def fill_search():
        model_selected = input.selected_model()
        ui.update_text("search_query", value=model_selected)
        show_curtain.set(False)

    # إغلاق الستارة تلقائياً في الواجهة عند العثور على نتيجة من دالة workflows
    @reactive.effect
    @reactive.event(input.hide_curtain_signal)
    def hide_curtain_on_signal():
        show_curtain.set(False)

    # رصد إطلاق وتشغيل الخطة 2 من واجهة التحذير
    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def launch_plan_2():
        current_search_phone.set(input.trigger_plan_2())
        active_modal.set("plan_2")

    # إدارة وحقن الطبقات المنبثقة للخطط (Modals)
    @render.ui
    def modal_layer():
        mode = active_modal()
        if mode == "plan_2":
            return draw_plan_2_modal(current_search_phone(), unique_panels(), unique_sensors())
        elif mode == "plan_3":
            return draw_plan_3_modal(
                current_search_phone(),
                input.p2_size(),
                input.p2_panel(),
                input.p2_sensor()
            )
        return None

    # زر إغلاق وتراجع الخطة 2
    @reactive.effect
    @reactive.event(input.p2_cancel)
    def cancel_p2():
        active_modal.set(None)

    # زر إضافة شكل شاشة جديد حياً للمتصفح ➕
    @reactive.effect
    @reactive.event(input.btn_add_panel)
    def add_custom_panel():
        ui.modal_show(ui.modal(
            ui.input_text("new_panel_name", "أدخل اسم المسمى الجديد للشاشة:"),
            ui.modal_button("تراجع"),
            ui.input_action_button("save_new_panel", "إضافة لحصيلة الجلسة", class_="btn-neon"),
            title="✨ إضافة مواصفة شاشة جديدة", easy_close=True
        ))

    @reactive.effect
    @reactive.event(input.save_new_panel)
    def save_panel_to_state():
        val = input.new_panel_name().strip()
        if val:
            custom_panels.set(custom_panels() + [val])
        ui.modal_remove()

    # زر إضافة مستشعر حركي صارم جديد حياً للمتصفح ➕
    @reactive.effect
    @reactive.event(input.btn_add_sensor)
    def add_custom_sensor():
        ui.modal_show(ui.modal(
            ui.input_text("new_sensor_name", "أدخل المسمى الفني للمستشعر الجديد:"),
            ui.modal_button("تراجع"),
            ui.input_action_button("save_new_sensor", "إضافة لحصيلة الجلسة", class_="btn-neon"),
            title="✨ إضافة مستشعر حركي صارم", easy_close=True
        ))

    @reactive.effect
    @reactive.event(input.save_new_sensor)
    def save_sensor_to_state():
        val = input.new_sensor_name().strip()
        if val:
            custom_sensors.set(custom_sensors() + [val])
        ui.modal_remove()

    # تنفيذ البحث الفني للخطة 2 ومطابقة المجموعات
    @reactive.effect
    @reactive.event(input.p2_search)
    def process_plan_2_matching():
        req_size = str(input.p2_size() or "").strip()
        req_panel = str(input.p2_panel()).strip()
        req_sensor = str(input.p2_sensor()).strip()

        # استدعاء دالة المقارنة الصارمة للتحقق من المجموعات
        compat = get_compatibles_strict(database(), req_size, req_panel, req_sensor, current_search_phone())
        
        # تحقق هندسي: إذا تم العثور على مجموعة مطابقة (تماماً أو متسامحة بقيمة ±0.03)
        if compat["exact"] or compat["plus"] or compat["minus"]:
            active_modal.set(None)  # إغلاق النافذة
            
            # عرض زر الدمج التلقائي في المجموعة لحفظ الخلية ومخرجات المقارنة
            ui.modal_show(ui.modal(
                ui.div(
                    ui.h3("🎉 تم العثور على مجموعات متوافقة فنياً!", style="color:#2ecc71; text-align:center;"),
                    ui.p(f"الهاتف ({current_search_phone()}) يملك نفس الهيكل الفني للمجموعات المكتشفة."),
                    ui.p("هل تريد إدراجه ودمجه مع هذه المجموعة في السحاب لتلقينه تلقائياً مستقبلاً؟", style="text-align:right;"),
                    style="direction:rtl;"
                ),
                footer=ui.div(
                    ui.input_action_button("btn_merge_confirm", "🔗 نعم، ادمج الهاتف فوراً", class_="btn-neon", style="background:#2ecc71; color:white;"),
                    ui.modal_button("إلغاء وتجاهل")
                ),
                size="m", easy_close=False
            ))
        else:
            # لم يجد الكود أي مواصفات أو اسم مطابق -> تفعيل خطة الطوارئ 3 كلياً
            active_modal.set("plan_3")
    # تنفيذ دمج الهاتف في المجموعة المكتشفة بـ Supabase
    @reactive.effect
    @reactive.event(input.btn_merge_confirm)
    def confirm_merge_supabase():
        try:
            supabase.table("phones").insert({
                "model_name": current_search_phone(),
                "size": str(input.p2_size()),
                "panel": input.p2_panel(),
                "sensor": input.p2_sensor()
            }).execute()
            
            db_trigger.set(db_trigger() + 1)  # إنعاش وتحديث النظام حياً
            ui.modal_remove()
            ui.notification_show(f"✔️ تم دمج الموديل {current_search_phone()} بالمجموعة بنجاح!", type="message", duration=4)
        except Exception as e:
            ui.notification_show(f"❌ فشل الدمج بالسيرفر: {str(e)}", type="error")

    # زر إلغاء وتراجع خطة الطوارئ 3
    @reactive.effect
    @reactive.event(input.p3_cancel)
    def cancel_p3():
        active_modal.set("plan_2")  # العودة للخلفية اليدوية

    # تنفيذ خطة الطوارئ 3: إنشاء وحفظ خلية/مجموعة مرجعية جديدة كلياً في قاعدة البيانات
    @reactive.effect
    @reactive.event(input.p3_submit)
    def submit_plan_3_supabase():
        try:
            supabase.table("phones").insert({
                "model_name": current_search_phone(),
                "size": str(input.p2_size()),
                "panel": input.p2_panel(),
                "sensor": input.p2_sensor()
            }).execute()
            
            db_trigger.set(db_trigger() + 1)  # إنعاش البيانات حياً
            active_modal.set(None)
            ui.notification_show(f"🚨 خطة 3: تم تأسيس المجموعة المرجعية بنجاح للـ {current_search_phone()}!", type="warning", duration=5)
        except Exception as e:
            ui.notification_show(f"❌ فشل التأسيس: {str(e)}", type="error")

    # نافذة المخرجات الرئيسية والتحديث المباشر للمقاس والتطابات
    @render.ui
    def results_area():
        phone = input.search_query().strip()
        if not phone:
            return None

        # تمرير الـ database التفاعلية المباشرة المربوطة بـ Supabase
        result = run_system_workflows(phone, database(), None)
        if not result:
            return None

        return ui.HTML(result)

app = App(app_ui, server)
