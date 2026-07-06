# server.py
from shiny import reactive, render, ui, Session
from services import *
from silent_monitor import get_database, refresh as monitor_refresh, get_status
from logic_engine import run_system_workflows
from workflows import run_system_workflows as workflow_renderer
from core.logger import get_logger
from config import IDS, COLORS

log = get_logger("server")


def server(input, output, session):
    # =========================
    # 1. إدارة الحالة (State Management)
    # =========================
    database_data = reactive.value({})
    models_index = reactive.value([])
    autocomplete_index = reactive.value(None)
    custom_panels = reactive.value([])
    custom_sensors = reactive.value([])

    current_phone = reactive.value("")
    suggestions_list = reactive.value([])
    show_curtain = reactive.value(False)

    plan_results = reactive.value(None)
    last_monitor_status = reactive.value("OFFLINE")
    workflow_cache_val = reactive.value(None)

    # =========================
    # 2. مزامنة قاعدة البيانات (حل مشكلة Offline/Online)
    # =========================
    @reactive.effect
    def _sync_database():
        try:
            # تحميل البيانات من SilentMonitor (الذي يتعامل مع Supabase والملف المحلي)
            db = get_database()
            status_info = get_status()

            if db and isinstance(db, dict):
                database_data.set(db)
                last_monitor_status.set(status_info.get("status", "UNKNOWN"))

                # بناء الفهارس فقط إذا تغيرت البيانات
                current_models = models_index()
                new_flat_list = []
                for panels in db.values():
                    for sensors in panels.values():
                        for s_data in sensors.values():
                            new_flat_list.extend(s_data.get("models", []))

                if len(new_flat_list) != len(current_models):
                    unique_models = sorted(list(set(new_flat_list)))
                    models_index.set(unique_models)
                    autocomplete_index.set(build_autocomplete_index(unique_models))

                    # استخراج القوائم الفريدة للألواح والمستشعرات
                    p_set, s_set = set(), set()
                    for panels in db.values():
                        for p, sensors in panels.items():
                            p_set.add(p)
                            for s in sensors.keys():
                                s_set.add(s)
                    custom_panels.set(sorted(list(p_set)))
                    custom_sensors.set(sorted(list(s_set)))

                    log.info(f"Database synced: {len(models_index())} models loaded.")
            else:
                last_monitor_status.set("OFFLINE")

        except Exception as e:
            log.error(f"Sync Error: {e}")

    # =========================
    # 3. البحث والاقتراحات (Auto-complete)
    # =========================
    @reactive.effect
    def _handle_search():
        query = input.search_query().strip()
        current_phone.set(query)

        trie = autocomplete_index()
        if not query or not trie:
            suggestions_list.set([])
            show_curtain.set(False)
            return

        matches = trie.search_prefix(query, 10)
        if matches:
            suggestions_list.set(matches)
            show_curtain.set(True)
        else:
            suggestions_list.set([])
            show_curtain.set(False)

    @output
    @render.ui
    def suggestions_curtain():
        if not show_curtain():
            return None
        items = suggestions_list()
        if not items:
            return None

        return ui.div(
            *[
                ui.div(m, class_="suggestion-row", onclick=f"Shiny.setInputValue('search_query', '{m}');")
                for m in items
            ],
            class_="suggestions-curtain",
        )

    # =========================
    # 4. عرض النتائج والصورة (حل مشكلة اختفاء الصورة والبطاقات)
    # =========================
    @reactive.effect
    def _on_model_selected():
        phone = current_phone()
        if not phone:
            plan_results.set(None)
            return

        db = database_data()
        if not db:
            return

        # استخدام دالة العرض من workflows.py للحصول على البطاقات الملونة النيون
        result_ui = workflow_renderer(phone, db)

        # التحقق هل نحتاج لفتح خطة 2؟
        needs_plan2 = "trigger_plan_2" in str(result_ui) or "ابدأ إدخال المواصفات" in str(result_ui)

        plan_results.set(
            {
                "ui": result_ui,
                "type": "plan_2_pending" if needs_plan2 else "result",
                "phone": phone,
            }
        )

    @output
    @render.ui
    def results_workflow_view():
        res = plan_results()
        if not res:
            return None

        children = []

        # ✅ إصلاح الصورة: استخدام AMMAR.jpg الموجود فعلياً في مجلد www
        children.append(
            ui.tags.img(
                src="/AMMAR.jpg",
                style="width: 200px; height: auto; display: block; margin: 20px auto; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.5);",
            )
        )

        # إضافة مخرجات Workflow (البطاقات الملونة النيون)
        if res.get("ui"):
            children.append(res["ui"])

        # إذا كنا بحاجة لخطة 2، أضف حقول الإدخال المتسلسلة
        if res.get("type") == "plan_2_pending":
            children.append(
                ui.div(
                    ui.h3("📋 خطة 2: إدخال يدوي", style="text-align:center; color: var(--primary-color);"),
                    ui.input_text("p2_size", "المقاس:", placeholder="6.67"),
                    ui.input_selectize("p2_panel", "نوع الشاشة:", choices=custom_panels()),
                    ui.input_selectize("p2_sensor", "المستشعر:", choices=custom_sensors()),
                    ui.tags.button(
                        "بحث في المجموعات",
                        class_="btn-neon",
                        style="width:100%; background: var(--primary-color); margin-top:10px;",
                        onclick="Shiny.setInputValue('exec_plan2', true, {priority:'event'});",
                    ),
                    class_="glass-card",
                )
            )

        return ui.div(*children, class_="fade-in")

    # زر تنفيذ خطة 2
    @reactive.effect
    def _exec_plan2():
        if input.exec_plan2():
            size = input.p2_size()
            panel = input.p2_panel()
            sensor = input.p2_sensor()
            if all([size, panel, sensor]):
                res = process_plan(size, panel, sensor, database_data(), build_fast_index(database_data()))
                if res:
                    plan_results.set(
                        {
                            "ui": ui.div(
                                ui.h3(f"✅ تطابق: {res['size']} | {res['panel']}"), class_="glass-card"
                            ),
                            "type": "match",
                        }
                    )
                else:
                    plan_results.set(
                        {
                            "ui": ui.div(ui.h3("️ لا يوجد تطابق، انتقل لخطة 3"), class_="glass-card"),
                            "type": "no_match",
                        }
                    )

    # =========================
    # 5. نافذة الإعدادات (Drawer Logic - متوافق مع CSS .drawer.open)
    # =========================
    @reactive.effect
    def _toggle_drawer():
        if input.btn_settings():
            session.send_custom_message("toggle_drawer", {"action": "open"})
        if input.btn_close_drawer_trigger():
            session.send_custom_message("toggle_drawer", {"action": "close"})

    @output
    @render.ui
    def drawer_js_handler():
        return ui.tags.script("""
            Shiny.addCustomMessageHandler('toggle_drawer', function(msg) {
                const d = document.getElementById('settings-drawer');
                if(d) msg.action === 'open' ? d.classList.add('open') : d.classList.remove('open');
            });
        """)

    # =========================
    # 6. مكونات حالة النظام (داخل الـ Drawer - متوافقة مع CSS .metric-box)
    # =========================
    @output
    @render.ui
    def database_status_area():
        total = len(models_index())
        return ui.div(
            ui.div("📊 عدد الموديلات", style="font-size: 12px; opacity: 0.7; margin-bottom: 4px;"),
            ui.div(str(total), style="font-size: 18px; font-weight: bold; color: var(--primary-color);"),
            class_="metric-box",
        )

    @output
    @render.ui
    def monitor_area():
        st = last_monitor_status()
        col = "#2ecc71" if st == "ONLINE" else ("#e67e22" if st == "FALLBACK" else "#ff5252")
        return ui.div(
            ui.div("🛰️ حالة المراقب", style="font-size: 12px; opacity: 0.7; margin-bottom: 4px;"),
            ui.div(st, style=f"font-size: 18px; font-weight: bold; color: {col};"),
            class_="metric-box",
        )

    @output
    @render.ui
    def notifications_area():
        src = get_status().get("source", "N/A")
        return ui.div(
            ui.div(" مصدر البيانات", style="font-size: 12px; opacity: 0.7; margin-bottom: 4px;"),
            ui.div(src, style="font-size: 18px; font-weight: bold; color: var(--foundation-color);"),
            class_="metric-box",
                            )
