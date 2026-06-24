import os
from shiny import App, ui, render, reactive
from supabase import create_client
from workflows import run_system_workflows, get_compatibles_strict
from ui_components import inject_pwa_and_styles, draw_plan_2_modal, draw_plan_3_modal

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
        if not size or not model: continue
        db.setdefault(size, {})
        db[size].setdefault(panel, {})
        db[size][panel].setdefault(sensor, {"models": []})
        if model not in db[size][panel][sensor]["models"]: db[size][panel][sensor]["models"].append(model)
    return db

# ربط شاشة الإعدادات بمخرجات ديناميكية لعرض العداد الحقيقي وحالة الحارس فورياً
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.HTML("<script>Shiny.addCustomMessageHandler('toggle_drawer', function(msg) { let d=document.getElementById('settings_drawer'); if(d) { if(msg==='open') d.classList.add('open'); else d.classList.remove('open'); } });</script>"),
    
    ui.div(
        ui.h3("⚙️ الإعدادات", style="color:#00bfff; text-align:right; margin-bottom:25px;"), 
        ui.div(ui.input_switch("switch_notif", "🔔 تفعيل جرس الإشعارات", value=True), class_="metric-box"), 
        ui.div(ui.input_switch("switch_monitor", "🛡️ تشغيل المراقب الصامت", value=True), class_="metric-box"),
        
        # صندوق مخرجات ذكي يعرض العداد الحي للهواتف وحالة الأمان
        ui.output_ui("drawer_status_area"),
        
        ui.p("", style="margin-bottom:20px;"),
        ui.input_action_button("close_drawer", "إغلاق الترس", class_="btn-neon", style="width:100%;"), 
        id="settings_drawer", 
        class_="drawer"
    ),
    
    ui.div(
        ui.div(
            class_="brand-neon-title", 
            children=[
                ui.div("ZEGAAR AMMAR", class_="brand-neon-main"), 
                ui.div("GLASS MANAGER", class_="brand-neon-sub")
            ]
        ), 
        ui.input_action_button("btn_settings", "⚙️", class_="btn-neon", style="font-size:20px; padding:10px 15px;"), 
        class_="header-bar"
    ),
    
    ui.div(ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."), ui.output_ui("suggestions_curtain"), class_="search-box"),
    ui.output_ui("results_area"), 
    ui.output_ui("modal_layer")
)
def server(input, output, session):
    db_trigger = reactive.Value(0)
    current_search_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)
    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])
    is_programmatic_update = reactive.Value(False)

    @reactive.calc
    def cloud_rows():
        db_trigger()
        try:
            res = supabase.table("phones").select("*").execute()
            return res.data or []
        except: return []

    @reactive.calc
    def database(): return convert_database(cloud_rows())
    @reactive.calc
    def unique_panels():
        p = set(str(r.get("panel", "")).strip() for r in cloud_rows()); p.update(custom_panels())
        return sorted(list(p))
    @reactive.calc
    def unique_sensors():
        s = set(str(r.get("sensor", "")).strip() for r in cloud_rows()); s.update(custom_sensors())
        return sorted(list(s))

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer(): await session.send_custom_message("toggle_drawer", "open")
    @reactive.effect
    @reactive.event(input.close_drawer)
    async def close_drawer(): await session.send_custom_message("toggle_drawer", "close")

    # إحياء عداد الهواتف الحية ديناميكياً ليقرأ من طول المصفوفة الفعلي ويعرض حالة حارس التطبيق
    @render.ui
    def drawer_status_area():
        total_phones = len(cloud_rows())
        notif_txt = "🟢 جرس الإشعارات: نشط" if input.switch_notif() else "🔴 جرس الإشعارات: متوقف"
        monitor_txt = "🟢 المراقب الصامت: يحرس البيانات" if input.switch_monitor() else "🔴 المراقب الصامت: متوقف"
        return ui.div(
            ui.div(f"📊 إجمالي الهواتف بالسحاب: {total_phones}", class_="metric-box", style="font-weight:bold; color:#00bfff;"),
            ui.div(notif_txt, style="font-size:13px; color:#bbb; text-align:right; margin-bottom:5px; margin-top:10px;"),
            ui.div(monitor_txt, style="font-size:13px; color:#bbb; text-align:right;")
        )

    @reactive.effect
    @reactive.event(input.search_query)
    def track_search():
        if is_programmatic_update():
            is_programmatic_update.set(False)
        else:
            show_curtain.set(True)

    @render.ui
    def suggestions_curtain():
        if not show_curtain(): return None
        q = input.search_query().strip().lower()
        if not q: return None
        matches = list(dict.fromkeys(str(r.get("model_name", "")) for r in cloud_rows() if q in str(r.get("model_name", "")).lower()))[:8]
        if not matches: return None
        return ui.div(*[ui.div(n, class_="suggestion-row", onclick=f"Shiny.setInputValue('selected_model', '{n}', {{priority: 'event'}});") for n in matches], class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model)
    def fill_search():
        is_programmatic_update.set(True)
        ui.update_text("search_query", value=input.selected_model())
        show_curtain.set(False)

    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def launch_plan_2():
        current_search_phone.set(input.trigger_plan_2())
        active_modal.set("plan_2")

    @render.ui
    def modal_layer():
        m = active_modal()
        if m == "plan_2": return draw_plan_2_modal(current_search_phone(), unique_panels(), unique_sensors())
        if m == "plan_3": return draw_plan_3_modal(current_search_phone(), input.p2_size(), input.p2_panel(), input.p2_sensor())
        return None

    @reactive.effect
    @reactive.event(input.p2_cancel)
    def cancel_p2(): active_modal.set(None)
    @reactive.effect
    @reactive.event(input.btn_add_panel)
    def add_panel(): ui.modal_show(ui.modal(ui.input_text("new_p", "اسم الشاشة الجديدة:"), ui.modal_button("تراجع"), ui.input_action_button("save_p", "إضافة", class_="btn-neon"), title="✨ إضافة شاشة"))
    @reactive.effect
    @reactive.event(input.save_p)
    def save_p():
        if input.new_p().strip(): custom_panels.set(custom_panels() + [input.new_p().strip()])
        ui.modal_remove()
    @reactive.effect
    @reactive.event(input.btn_add_sensor)
    def add_sensor(): ui.modal_show(ui.modal(ui.input_text("new_s", "اسم المستشعر الجديد:"), ui.modal_button("تراجع"), ui.input_action_button("save_s", "إضافة", class_="btn-neon"), title="✨ إضافة مستشعر"))
    @reactive.effect
    @reactive.event(input.save_s)
    def save_s():
        if input.new_s().strip(): custom_sensors.set(custom_sensors() + [input.new_s().strip()])
        ui.modal_remove()

    @reactive.effect
    @reactive.event(input.p2_search)
    def process_p2():
        compat = get_compatibles_strict(database(), str(input.p2_size() or ""), input.p2_panel(), input.p2_sensor(), current_search_phone())
        if compat["exact"] or compat["plus"] or compat["minus"]:
            active_modal.set(None)
            ui.modal_show(ui.modal(ui.div(ui.h3("🎉 تم العثور على مجموعات متوافقة!", style="color:#2ecc71; text-align:center;"), ui.p("هل تريد الدمج تلقائياً مع هذه المجموعة في السحاب؟")), footer=ui.div(ui.input_action_button("btn_merge", "🔗 ادمج الهاتف فوراً", class_="btn-neon", style="background:#2ecc71; color:white;"), ui.modal_button("إلغاء")), size="m"))
        else: active_modal.set("plan_3")

    # تفعيل المراقب الصامت كحارس أمني لمنع تكرار دمج الموديلات المسجلة سابقاً
    @reactive.effect
    @reactive.event(input.btn_merge)
    def do_merge():
        if input.switch_monitor():
            existing_names = [str(r.get("model_name", "")).strip().lower() for r in cloud_rows()]
            if str(current_search_phone()).strip().lower() in existing_names:
                if input.switch_notif():
                    ui.notification_show("🚨 المراقب الصامت: هذا الموديل مسجل بالفعل في المجموعات! تم إلغاء التكرار.", type="error", duration=5)
                ui.modal_remove()
                return
        try:
            supabase.table("phones").insert({"model_name": current_search_phone(), "size": str(input.p2_size()), "panel": input.p2_panel(), "sensor": input.p2_sensor()}).execute()
            db_trigger.set(db_trigger() + 1); ui.modal_remove()
            if input.switch_notif():
                ui.notification_show("✔️ جرس الإشعارات: تم دمج الموديل بنجاح بالسحاب!", type="message")
        except: pass

    @reactive.effect
    @reactive.event(input.p3_cancel)
    def cancel_p3(): active_modal.set("plan_2")

    # تفعيل المراقب الصامت في خطة الطوارئ 3 لمنع تكرار تأسيس نفس الهاتف
    @reactive.effect
    @reactive.event(input.p3_submit)
    def do_p3():
        if input.switch_monitor():
            existing_names = [str(r.get("model_name", "")).strip().lower() for r in cloud_rows()]
            if str(current_search_phone()).strip().lower() in existing_names:
                if input.switch_notif():
                    ui.notification_show("🚨 المراقب الصامت: تم إحباط تأسيس مجموعة مكررة للهاتف!", type="error", duration=5)
                active_modal.set(None)
                return
        try:
            supabase.table("phones").insert({"model_name": current_search_phone(), "size": str(input.p2_size()), "panel": input.p2_panel(), "sensor": input.p2_sensor()}).execute()
            db_trigger.set(db_trigger() + 1); active_modal.set(None)
            if input.switch_notif():
                ui.notification_show("🚨 جرس الإشعارات: تم تأسيس مرجع فني جديد ومجموعة مستقلة!", type="warning")
        except: pass

    @render.ui
    def results_area():
        p = input.search_query().strip()
        return ui.HTML(run_system_workflows(p, database(), None)) if p else None

app = App(app_ui, server)
