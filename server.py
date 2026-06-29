import json
from shiny import ui, render, reactive

# استيراد الخدمات الذكية والبنية التحتية
from services.search_service import build_autocomplete_index, find_model_coords
from services.plan_engine import compute_plan_matches, is_empty_result
from services.index_service import build_fast_index, extract_panels_sensors
from services.cache_service import workflow_cache, coords_cache
from core.logger import get_logger

# استيراد الوحدات الأساسية للتطبيق
from database import add_model
from silent_monitor import get_database, refresh, get_status, get_statistics
from logic_engine import run_system_workflows
from ui_components import (
    draw_plan_2_modal,
    draw_plan_3_modal,
    draw_warning_card,
    draw_technical_coords,
    draw_neon_section,
    draw_database_status
)

log = get_logger("server")
MODELS_INDEX_FILE = "models_index.txt"


def load_models_index():
    """تحميل قائمة الموديلات من ملف المؤشر للإكمال التلقائي"""
    try:
        with open(MODELS_INDEX_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except OSError as e:
        log.error(f"Failed to load models index: {e}")
        return []


def convert_database_from_raw(rows):
    """تحويل البيانات الخام إلى هيكلية شجرية منظمة مع تنظيف المفاتيح"""
    db = {}
    if not isinstance(rows, list):
        return db
    for item in rows:
        if not isinstance(item, dict):
            continue
        size = str(item.get("size") or "").strip()
        panel = str(item.get("panel") or "Notch Screen").strip()
        sensor = str(item.get("sensor") or "hardware_top_sensor").strip()
        model = str(item.get("model_name") or "").strip()

        if not size or not model:
            continue

        db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})
        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)
    return db


def server(input, output, session):
    # ===== State Management =====
    db_trigger = reactive.Value(0)
    current_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)  # None | "plan_2" | "plan_3"
    suggestions_list = reactive.Value([])
    plan_results = reactive.Value(None)

    plan_inputs = {
        "size": reactive.Value(""),
        "panel": reactive.Value(""),
        "sensor": reactive.Value(""),
    }
    current_plan_type = reactive.Value(None)

    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])

    # الفهارس السريعة (Trie + DB Index)
    autocomplete_index = reactive.Value(None)
    
    # متغيرات لتحسين الأداء ومنع التحديثات المكررة
    models_index = reactive.Value(load_models_index())
    _db_version = reactive.Value(0)      # لتجنب مشكلة id() المتغيرة في الكاش
    _last_db_size = reactive.Value(-1)   # تهيئة بـ -1 لضمان البناء الأولي
    _last_monitor_status = reactive.Value("") # لتجنب تكرار Logs المراقب

    # ===== Data Layer =====
    @reactive.calc
    def database_data():
        db_trigger()
        try:
            db = get_database()
            if isinstance(db, dict):
                return db
            if isinstance(db, list):
                return convert_database_from_raw(db)
            return {}
        except Exception as e:
            log.error(f"Database error: {e}")
            return {}

    @reactive.calc
    def fast_index_calc():
        return build_fast_index(database_data())

    # ===== Watchers & Optimization =====
    @reactive.effect
    def watcher_refresh():
        """مراقب ذكي: يعيد البناء فقط عند تغير البيانات فعلياً"""
        reactive.invalidate_later(5)
        db_trigger()

        try:
            # التحقق من حجم قاعدة البيانات أولاً لتوفير الموارد
            stats = get_statistics()
            current_size = stats.get("phones", 0) if isinstance(stats, dict) else 0

            # إذا لم يتغير الحجم وكان الفهرس موجوداً، نتخطى إعادة البناء المكلفة
            if _last_db_size() == current_size and autocomplete_index() is not None:
                # فقط نحدث الاقتراحات الحية إذا كانت الستارة مفتوحة
                if show_curtain():
                    query = current_phone()
                    trie = autocomplete_index()
                    if query and trie:
                        matches = trie.search_prefix(query, 10)
                        suggestions_list.set(matches)
                return

            # إذا تغير الحجم، نقوم بالتحديث الكامل
            log.info(f"[WATCHER] Data changed: {current_size} phones. Rebuilding...")
            _last_db_size.set(current_size)  # تحديث الحجم أولاً
            refresh()

            new_index = load_models_index()
            if autocomplete_index() is None or new_index != models_index():
                models_index.set(new_index)
                autocomplete_index.set(build_autocomplete_index(new_index))

                # Invalidate الكاش عند تحديث البيانات باستخدام version counter
                workflow_cache.invalidate()
                coords_cache.invalidate()
                _db_version.set(_db_version() + 1)

                # تحديث قوائم الخيارات
                panels, sensors = extract_panels_sensors(database_data())
                custom_panels.set(panels)
                custom_sensors.set(sensors)

            # تحديث الاقتراحات بعد البناء
            if show_curtain():
                query = current_phone()
                trie = autocomplete_index()
                if query and trie:
                    matches = trie.search_prefix(query, 10)
                    suggestions_list.set(matches)

        except Exception as e:
            log.error(f"Refresh error: {e}")

    @reactive.effect
    def watcher_status():
        """مراقبة حالة المراقب الصامت (تسجيل فقط عند التغير)"""
        reactive.invalidate_later(5)
        try:
            status = get_status()
            current_status = status.get("status", "UNKNOWN") if isinstance(status, dict) else "UNKNOWN"

            # تسجيل فقط عند تغير الحالة لمنع تكرار الـ Logs
            if current_status != _last_monitor_status():
                _last_monitor_status.set(current_status)
                if current_status != "ONLINE":
                    log.warning(f"Silent Monitor Warning: {status}")
                else:
                    log.info("Silent Monitor: ONLINE")
        except Exception as e:
            log.error(f"Status watcher error: {e}")

    # ===== Search & Autocomplete =====
    @reactive.effect
    @reactive.event(input.search_query)
    def handle_search():
        query = input.search_query().strip()
        current_phone.set(query)

        if not query:
            suggestions_list.set([])
            show_curtain.set(False)
            return

        trie = autocomplete_index()
        if not trie:
            return

        matches = trie.search_prefix(query, 10)
        exact_match = trie.contains_exact(query)

        if matches and not exact_match:
            suggestions_list.set(matches)
            show_curtain.set(True)
        else:
            suggestions_list.set([])
            show_curtain.set(False)

    @render.ui
    def suggestions_curtain():
        if not show_curtain():
            return None
        items = suggestions_list()
        if not items:
            return None

        rows = []
        for item in items:
            safe_item = json.dumps(item)
            rows.append(
                ui.div(
                    item,
                    class_="suggestion-row",
                    onclick=(
                        f"Shiny.setInputValue('search_query', {safe_item}, "
                        f"{{priority:'event'}}); "
                        f"Shiny.setInputValue('selected_model_trigger', "
                        f"Math.random(), {{priority:'event'}});"
                    ),
                )
            )
        return ui.div(*rows, class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def confirm_selection():
        show_curtain.set(False)
        # إبطال الكاش لإعادة تقييم Plan 1 فوراً عند الاختيار
        workflow_cache.invalidate()
        coords_cache.invalidate()

    # ===== Plan 2 / Plan 3 Logic =====
    def process_plan(size_val, panel_val, sensor_val, plan_type):
        if not all([size_val, panel_val, sensor_val]):
            plan_results.set(None)
            return

        results = compute_plan_matches(
            size_val, panel_val, sensor_val,
            database_data(),
            fast_index_calc()
        )

        plan_inputs["size"].set(str(size_val))
        plan_inputs["panel"].set(panel_val)
        plan_inputs["sensor"].set(sensor_val)
        current_plan_type.set(plan_type)

        plan_results.set(None if is_empty_result(results) else results)

    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def open_plan_2():
        if current_phone():
            active_modal.set("plan_2")
            current_plan_type.set("plan_2")

    @reactive.effect
    @reactive.event(input.trigger_plan_3)
    def open_plan_3():
        if current_phone():
            active_modal.set("plan_3")
            current_plan_type.set("plan_3")

    @reactive.effect
    @reactive.event(input.p2_search)
    def run_plan_2():
        process_plan(input.p2_size(), input.p2_panel(), input.p2_sensor(), "plan_2")

    @reactive.effect
    @reactive.event(input.p3_search)
    def run_plan_3():
        process_plan(input.p3_size(), input.p3_panel(), input.p3_sensor(), "plan_3")

    # ===== Save & Reset =====
    def reset_ui_after_save():
        ui.update_text(session, "search_query", value="")
        current_phone.set("")
        show_curtain.set(False)
        suggestions_list.set([])
        plan_results.set(None)
        plan_inputs["size"].set("")
        plan_inputs["panel"].set("")
        plan_inputs["sensor"].set("")
        current_plan_type.set(None)
        active_modal.set(None)
        workflow_cache.invalidate()
        coords_cache.invalidate()

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge)
    def learn_p2():
        _save_current_model()

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge_p3)
    def learn_p3():
        _save_current_model()

    @reactive.effect
    @reactive.event(input.btn_foundation)
    def foundation_new_group():
        """تأسيس مجموعة جديدة (Plan 3 foundation)"""
        _save_current_model()

    def _save_current_model():
        phone = current_phone()
        size = plan_inputs["size"]()
        panel = plan_inputs["panel"]()
        sensor = plan_inputs["sensor"]()

        if not all([phone, size, panel, sensor]):
            log.warning("Save attempted with missing data")
            return

        try:
            if add_model(size, panel, sensor, phone):
                # تحديث فوري لقاعدة البيانات والإحصائيات
                refresh()
                workflow_cache.invalidate()
                coords_cache.invalidate()
                db_trigger.set(db_trigger() + 1)
                reset_ui_after_save()
                log.info(f"Model saved: {phone}")
            else:
                log.error(f"Failed to save model: {phone}")
        except Exception as e:
            log.error(f"Save error: {e}")

    # ===== UI Rendering =====
    @reactive.calc
    def cached_coords():
        """تخزين مؤقت لإحداثيات الموديل (يستخدم _db_version بدلاً من id())"""
        phone = current_phone().strip()
        if not phone:
            return None
        version = _db_version()
        return coords_cache.get_or_compute(
            (phone, version),
            lambda: find_model_coords(database_data(), phone)
        )

    @reactive.calc
    def cached_workflow():
        """تخزين مؤقت لنتيجة run_system_workflows"""
        coords = cached_coords()
        if not coords or not coords[3]:
            return None
        phone = current_phone().strip()
        version = _db_version()
        plan_type = current_plan_type()
        return workflow_cache.get_or_compute(
            (phone, version, plan_type),
            lambda: run_system_workflows(phone, database_data(), "")
        )

    @render.ui
    def results_area():
        phone = current_phone().strip()
        if not phone:
            return None

        res = plan_results()
        plan_type = current_plan_type()

        # عرض workflow فقط إذا لم تكن هناك خطة نشطة (Plan 1)
        if plan_type is None:
            workflow_res = cached_workflow()
            if workflow_res:
                return ui.div(ui.HTML(workflow_res))

        btn_id = "btn_learn_and_merge" if plan_type == "plan_2" else "btn_learn_and_merge_p3"
        btn_color = "#2ecc71" if plan_type == "plan_2" else "#e67e22"
        suffix = "(مواصفات يدوية)" if plan_type == "plan_2" else "(خطة بديلة)"

        if isinstance(res, dict):
            return ui.div(
                draw_technical_coords(
                    plan_inputs["size"](),
                    plan_inputs["panel"](),
                    plan_inputs["sensor"](),
                    f"{phone} {suffix}",
                ),
                draw_neon_section("مطابقة تماماً", res.get("exact", []), "#2ecc71", "🟢", "exact"),
                draw_neon_section("أكبر بقليل", res.get("plus", []), "#3498db", "", "plus"),
                draw_neon_section("أصغر قليلاً", res.get("minus", []), "#e67e22", "🟠", "minus"),
                ui.input_action_button(
                    btn_id,
                    "🔄 دمج الهاتف داخل هذه المجموعة",
                    style=(
                        f"width:100%; background:{btn_color}; color:white; "
                        f"padding:14px; border:none; border-radius:12px; "
                        f"font-weight:bold; margin-top:15px; "
                    ),
                ),
            )

        # فشل Plan 3 → عرض زر التأسيس
        if res is None and plan_type == "plan_3":
            return ui.div(
                draw_warning_card("لم يتم العثور على مطابقات. هل تريد تأسيس مجموعة جديدة؟"),
                ui.input_action_button(
                    "btn_foundation",
                    "➕ تأسيس مجموعة جديدة بهذا الهاتف",
                    style=(
                        "width:100%; background:#9b59b6; color:white; "
                        "padding:14px; border:none; border-radius:12px; "
                        "font-weight:bold; margin-top:15px; "
                    ),
                ),
            )

        if res is None and plan_type:
            return ui.div(draw_warning_card("لم يتم العثور على مجموعة مطابقة. "))

        return ui.div(
            draw_warning_card(f"الموديل {phone} غير موجود داخل قاعدة البيانات. "),
            ui.div(
                ui.input_action_button(
                    "trigger_plan_2",
                    "🔵 بدء المطابقة الفنية (Plan 2)",
                    style="width:100%; background:#00bfff; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-bottom:10px; ",
                ),
                ui.input_action_button(
                    "trigger_plan_3",
                    "🟠 بدء الخطة البديلة (Plan 3)",
                    style="width:100%; background:#e67e22; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; ",
                ),
            ),
        )

    @render.ui
    def modal_layer():
        mode = active_modal()
        if mode == "plan_2":
            return draw_plan_2_modal(current_phone(), custom_panels(), custom_sensors())
        if mode == "plan_3":
            return draw_plan_3_modal(current_phone(), custom_panels(), custom_sensors())
        return None

    @render.ui
    def database_status_area():
        """عرض عداد قاعدة البيانات ديناميكياً"""
        try:
            stats = get_statistics()
            count = stats.get("phones", 0) if isinstance(stats, dict) else 0
            return ui.div(draw_database_status(count))
        except Exception as e:
            log.error(f"Stats error: {e}")
            return ui.div(draw_database_status(0))

    # ===== عناصر الإعدادات والمراقبة =====
    # 🔴 الإصلاح الحاسم: استخدام async/await لـ send_custom_message

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer():
        """فتح قائمة الإعدادات الجانبية"""
        await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def close_drawer():
        """إغلاق قائمة الإعدادات الجانبية"""
        await session.send_custom_message("toggle_drawer", "close")

    @render.ui
    def notifications_area():
        """عرض حالة جرس الإشعارات ديناميكياً"""
        try:
            status = get_status()
            source = status.get("source", "غير معروف") if isinstance(status, dict) else "غير متصل"
            return ui.div(f"🔔 المصدر: {source}", class_="metric-box")
        except Exception:
            return ui.div("🔔 جرس الإشعارات: غير متاح", class_="metric-box")

    @render.ui
    def monitor_area():
        """عرض حالة المراقب الصامت ديناميكياً"""
        try:
            status = get_status()
            state = status.get("status", "OFFLINE") if isinstance(status, dict) else "OFFLINE"
            color = "#2ecc71" if state == "ONLINE" else "#e74c3c"
            return ui.div(
                f"🔒 الحالة: {state}",
                style=f"color: {color}; font-weight: bold;",
                class_="metric-box"
            )
        except Exception:
            return ui.div("🔒 المراقب: غير متاح", class_="metric-box")
