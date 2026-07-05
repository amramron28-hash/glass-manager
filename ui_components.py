from shiny import reactive, render, ui, Session
from services import *
from silent_monitor import get_database, refresh as monitor_refresh, get_status
from logic_engine import run_system_workflows
from workflows import run_system_workflows as workflow_renderer
from core.logger import get_logger
from config import IDS, COLORS, REFRESH_INTERVAL_SEC

log = get_logger("server")


def server(input, output, session):
    # =========================
    # 1. إدارة الحالة (State Management)
    # =========================
    
    # بيانات النظام الأساسية
    database_data = reactive.value({})
    models_index = reactive.value([])
    autocomplete_index = reactive.value(None)
    custom_panels = reactive.value([])
    custom_sensors = reactive.value([])
    
    # حالة البحث والواجهة
    current_phone = reactive.value("")
    suggestions_list = reactive.value([])
    show_curtain = reactive.value(False)
    
    # نتائج العمل والخطط
    plan_results = reactive.value(None)      # النتيجة النهائية المعروضة
    current_plan_type = reactive.value(None) # نوع الخطة الحالية
    active_modal = reactive.value(None)      # النافذة المنبثقة النشطة
    
    # مدخلات الخطط اليدوية (للخطة 2)
    plan_inputs = {
        "size": reactive.value(""),
        "panel": reactive.value(""),
        "sensor": reactive.value("")
    }
    
    last_monitor_status = reactive.value("OFFLINE")
    workflow_cache_val = reactive.value(None)

    # =========================
    # 2. منطق التحديث التلقائي (Auto Refresh Logic)
    # =========================
    @reactive.effect
    def _sync_database():
        """مزامنة قاعدة البيانات والفهارس تلقائياً"""
        try:
            execute_refresh_logic(
                cached_stats=lambda: get_cache_stats(),
                database_data=database_data,
                autocomplete_index=autocomplete_index,
                models_index=models_index,
                custom_panels=custom_panels,
                custom_sensors=custom_sensors,
                last_db_size=len(models_index),
                show_curtain=show_curtain,
                current_phone=current_phone,
                suggestions_list=suggestions_list,
                refresh_fn=monitor_refresh,
                invalidate_workflow_fn=lambda: workflow_cache_val.set(None)
            )
            
            # تحديث حالة المراقب
            db = get_database()
            if db:
                database_data.set(db)
                status = get_status()
                last_monitor_status.set(status.get("status", "OFFLINE"))
                
        except Exception as e:
            log.error(f"Database sync error: {e}")

    # =========================
    # 3. البحث والإكمال التلقائي (Search & Autocomplete)
    # =========================
    @reactive.effect
    def _handle_search():
        """معالجة البحث عند تغيير نص البحث"""
        process_search_query(
            search_query_value=input.search_query(),
            current_phone_attr=current_phone,
            suggestions_list_attr=suggestions_list,
            show_curtain_attr=show_curtain,
            autocomplete_index_attr=autocomplete_index,
        )

    @output
    @render.ui
    def suggestions_curtain():
        """عرض قائمة الاقتراحات"""
        if not show_curtain():
            return None
        
        suggestions = suggestions_list()
        if not suggestions:
            return None
        
        return ui.div(
            *[
                ui.div(
                    suggestion,
                    class_="suggestion-row",
                    onclick=f"Shiny.setInputValue('{IDS['search_query']}', '{suggestion}');"
                )
                for suggestion in suggestions
            ],
            class_="suggestions-curtain"
        )

    # =========================
    # 4. معالجة اختيار الموديل وعرض النتائج (Core Workflow)
    # =========================
    @reactive.effect
    def _on_model_selected():
        """عند اختيار موديل أو الضغط على زر البحث"""
        phone = current_phone()
        if not phone:
            plan_results.set(None)
            return
        
        # تنفيذ Workflow الرئيسي باستخدام دالة العرض من workflows.py
        db = database_data()
        if not db:
            return
        
        result_ui = workflow_renderer(phone, db)
        
        # التحقق مما إذا كانت النتيجة تحتوي على زر تفعيل الخطة 2
        # هذا يعني أن الموديل غير موجود مباشرة ويجب الانتقال للمسار التفاعلي
        has_plan2_trigger = False
        if isinstance(result_ui, ui.TagList) or hasattr(result_ui, 'children'):
            # بحث بسيط عن وجود النص الخاص بالخطة 2 في المخرجات
            content_str = str(result_ui)
            if IDS['trigger_p2'] in content_str or "ابدأ إدخال المواصفات" in content_str:
                has_plan2_trigger = True
        
        plan_results.set({
            "ui": result_ui,
            "type": "plan_2_pending" if has_plan2_trigger else "plan_1_result",
            "phone": phone
        })

    @output
    @render.ui
    def results_workflow_view():
        """عرض نتائج Workflow والصورة"""
        results = plan_results()
        if not results:
            return None
        
        result_type = results.get("type")
        phone = results.get("phone", "")
        
        # حاوية النتائج الرئيسية
        container_children = []
        
        # ✅ إصلاح مشكلة اختفاء الصورة: وضعها كعنصر بارز فوق النتائج
        container_children.append(
            ui.tags.img(
                src="/phone_image.webp",
                style="width: 180px; height: auto; display: block; margin: 0 auto 20px auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.5); opacity: 0.9;"
            )
        )
        
        # إضافة مخرجات الدالة workflow_renderer
        result_ui = results.get("ui")
        if result_ui:
            container_children.append(result_ui)
        
        # ✅ إصلاح تسلسل الخطط: إذا كنا في انتظار الخطة 2، نضيف حقول الإدخال المتسلسلة
        if result_type == "plan_2_pending":
            container_children.append(_build_plan2_interactive_inputs())
            
        return ui.div(*container_children, class_="glass-card fade-in")

    def _build_plan2_interactive_inputs():
        """بناء واجهة الإدخال المتسلسلة للخطة 2 (مقاس -> شاشة -> مستشعر)"""
        return ui.div(
            ui.h3(" خطة 2: إدخال المواصفات يدوياً", style="color: var(--primary-color); text-align: center; margin-bottom: 15px;"),
            
            # حقل المقاس
            ui.div(
                ui.input_text("p2_size", "المقاس:", placeholder="مثال: 6.67"),
                class_="input-with-add"
            ),
            
            # حقل الشاشة مع زر الإضافة
            ui.div(
                ui.input_selectize("p2_panel", "نوع الشاشة:", choices=custom_panels()),
                ui.tags.button("+", class_="btn-add-option", 
                              onclick="Shiny.setInputValue('show_add_panel', true, {priority: 'event'});"),
                class_="input-with-add"
            ),
            
            # حقل المستشعر مع زر الإضافة
            ui.div(
                ui.input_selectize("p2_sensor", "نوع المستشعر:", choices=custom_sensors()),
                ui.tags.button("+", class_="btn-add-option",
                              onclick="Shiny.setInputValue('show_add_sensor', true, {priority: 'event'});"),
                class_="input-with-add"
            ),
            
            # زر البحث في المجموعات
            ui.tags.button(
                " بحث في المجموعات",
                class_="btn-neon",
                style=f"width:100%; padding:12px; background:{COLORS['plan2_btn']}; border:none; border-radius:8px; color:white; font-weight:bold; cursor:pointer; margin-top:10px;",
                onclick="Shiny.setInputValue('execute_plan2_search', true, {priority: 'event'});"
            ),
            style="margin-top: 20px;"
        )

    # =========================
    # 5. تنفيذ البحث في الخطة 2 (Plan 2 Execution)
    # =========================
    @reactive.effect
    def _execute_plan2_search():
        """تنفيذ البحث بناءً على مدخلات الخطة 2"""
        if input.execute_plan2_search():
            size = input.p2_size()
            panel = input.p2_panel()
            sensor = input.p2_sensor()
            
            if not all([size, panel, sensor]):
                log.warning("Plan 2: Missing inputs")
                return
            
            db = database_data()
            fast_idx = build_fast_index(db)
            
            result = process_plan(size, panel, sensor, db, fast_idx)
            
            if result:
                # إذا وُجد تطابق، نعرض نافذة تأكيد الإدراج
                plan_results.set({
                    "ui": ui.div(
                        ui.h3("✅ تم العثور على تطابق!", style="color: var(--success-color); text-align: center;"),
                        ui.div(f"المقاس: {result['size']} | الشاشة: {result['panel']} | المستشعر: {result['sensor']}", 
                              style="text-align: center; margin: 10px 0;"),
                        ui.tags.button(
                            "إدراج الموديل الحالي في هذه المجموعة",
                            class_="btn-neon",
                            style=f"width:100%; padding:12px; background:{COLORS['exact']}; border:none; border-radius:8px; color:white; font-weight:bold; cursor:pointer;",
                            onclick=f"Shiny.setInputValue('confirm_merge_to_group', '{current_phone()}', {{priority: 'event'}});"
                        ),
                        class_="glass-card"
                    ),
                    "type": "plan_2_match_found",
                    "data": result
                })
            else:
                # لم يُوجد تطابق → الانتقال لخطة الطوارئ 3
                plan_results.set({
                    "ui": ui.div(
                        ui.h3("⚠️ لم يُوجد تطابق في المجموعات", style="color: var(--warning-color); text-align: center;"),
                        ui.p("يرجى إنشاء مجموعة جديدة بالكامل عبر خطة الطوارئ", style="text-align: center;"),
                        ui.tags.button(
                            " فتح خطة الطوارئ 3",
                            class_="btn-neon",
                            style=f"width:100%; padding:12px; background:{COLORS['plan3_btn']}; border:none; border-radius:8px; color:white; font-weight:bold; cursor:pointer; margin-top:10px;",
                            onclick="Shiny.setInputValue('open_plan3_emergency', true, {priority: 'event'});"
                        ),
                        class_="glass-card"
                    ),
                    "type": "plan_3_required"
                })

    # =========================
    # 6. نافذة الإعدادات (Settings Drawer) - الإصلاح الكامل
    # =========================
    @reactive.effect
    def _toggle_settings_drawer():
        """التحكم في إظهار/إخفاء الـ Drawer باستخدام JavaScript"""
        if input.btn_settings():
            session.send_custom_message("toggle_drawer", {"action": "open"})
        
        if input.close_drawer_trigger():
            session.send_custom_message("toggle_drawer", {"action": "close"})

    # JavaScript للتحكم في الـ Drawer (متوافق مع CSS .drawer.open)
    @output
    @render.ui
    def drawer_js_handler():
        return ui.tags.script("""
            Shiny.addCustomMessageHandler('toggle_drawer', function(message) {
                const drawer = document.getElementById('settings-drawer');
                if (!drawer) return;
                
                if (message.action === 'open') {
                    drawer.classList.add('open');
                } else {
                    drawer.classList.remove('open');
                }
            });
        """)

    # =========================
    # 7. مكونات حالة النظام (System Status Components)
    # =========================
    @output
    @render.ui
    def database_status_area():
        """عرض عداد الهواتف"""
        total = len(models_index())
        return ui.div(
            ui.div("📊 قاعدة البيانات", style="font-size: 12px; opacity: 0.7;"),
            ui.div(str(total), style="font-size: 20px; font-weight: bold; color: var(--primary-color);"),
            class_="metric-box"
        )

    @output
    @render.ui
    def monitor_area():
        """عرض حالة المراقب الصامت"""
        status = last_monitor_status()
        color = "#2ecc71" if status == "ONLINE" else ("#e67e22" if status == "FALLBACK" else "#ff5252")
        return ui.div(
            ui.div(" المراقب", style="font-size: 12px; opacity: 0.7;"),
            ui.div(status, style=f"font-size: 16px; font-weight: bold; color: {color};"),
            class_="metric-box"
        )

    @output
    @render.ui
    def notifications_area():
        """عرض الإشعارات"""
        status = get_status()
        source = status.get("source", "N/A") if isinstance(status, dict) else "N/A"
        return ui.div(
            ui.div("🔔 المصدر", style="font-size: 12px; opacity: 0.7;"),
            ui.div(source, style="font-size: 14px; font-weight: bold; color: var(--secondary-color);"),
            class_="metric-box"
        )

    # =========================
    # 8. إضافة لوحة/مستشعر جديد (Add Panel/Sensor)
    # =========================
    @reactive.effect
    def _handle_show_add_panel():
        if input.show_add_panel():
            handle_show_add_panel(show_curtain, suggestions_list)

    @reactive.effect
    def _handle_show_add_sensor():
        if input.show_add_sensor():
            handle_show_add_sensor(show_curtain, suggestions_list)

    @reactive.effect
    def _handle_confirm_add_panel():
        if input.btn_confirm_add_panel():
            confirm_add_panel(input, custom_panels, lambda: workflow_cache_val.set(None))

    @reactive.effect
    def _handle_confirm_add_sensor():
        if input.btn_confirm_add_sensor():
            confirm_add_sensor(input, custom_sensors, lambda: workflow_cache_val.set(None))

    @reactive.effect
    def _handle_cancel_add():
        if input.btn_cancel_add():
            cancel_add()

    # =========================
    # 9. إعادة التعيين (Reset)
    # =========================
    @reactive.effect
    def _handle_reset_on_empty_search():
        """إعادة تعيين الواجهة عند مسح حقل البحث"""
        if input.search_query() == "":
            reset_ui(
                session,
                current_phone,
                show_curtain,
                suggestions_list,
                plan_results,
                current_plan_type,
                active_modal,
                plan_inputs,
                lambda: workflow_cache_val.set(None)
            )
