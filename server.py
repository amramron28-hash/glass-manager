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
    fast_index = reactive.Value(None)
    
    models_index = reactive.Value(load_models_index())

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

    @reactive.effect
    def watcher_refresh():
        db_trigger()
        try:
            refresh()
            new_index = load_models_index()
            models_index.set(new_index)
            
            # إعادة بناء Trie
            autocomplete_index.set(build_autocomplete_index(new_index))
            
            # إعادة بناء الفهرس السريع (يُحسب lazily عبر reactive.calc)
            _ = fast_index_calc()
            
            # Invalidate الكاش عند تحديث البيانات
            workflow_cache.invalidate()
            coords_cache.invalidate()
            
            # تحديث قوائم الخيارات
            panels, sensors = extract_panels_sensors(database_data())
            custom_panels.set(panels)
            custom_sensors.set(sensors)
            
            # تحديث الاقتراحات إذا كانت الستارة مفتوحة
            if show_curtain():
                query = current_phone()
                if query and autocomplete_index():
                    matches = autocomplete_index().search_prefix(query, 10)
                    suggestions_list.set(matches)
        except Exception as e:
            log.error(f"Refresh error: {e}")

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
        active_modal.set(None)  # إغلاق Modal عبر Reactive State فقط
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
        """تخزين مؤقت لإحداثيات الموديل"""
        phone = current_phone().strip()
        if not phone:
            return None
        return coords_cache.get_or_compute(
            (phone, id(database_data())),
            lambda: find_model_coords(database_data(), phone)
        )

    @reactive.calc
    def cached_workflow():
        """تخزين مؤقت لنتيجة run_system_workflows"""
        coords = cached_coords()
        if not coords or not coords[3]:
            return None
        phone = current_phone().strip()
        return workflow_cache.get_or_compute(
            (phone, id(database_data())),
            lambda: run_system_workflows(phone, database_data(), "")
        )

    @render.ui
    def results_area():
        phone = current_phone().strip()
        if not phone:
            return None
        
        # استخدام النتيجة المخزنة
        workflow_res = cached_workflow()
        if workflow_res:
            return ui.div(ui.HTML(workflow_res))
        
        res = plan_results()
        plan_type = current_plan_type()
        
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
                        f"font-weight:bold; margin-top:15px;"
                    ),
                ),
            )
        
        if res is None and plan_type:
            return ui.div(draw_warning_card("لم يتم العثور على مجموعة مطابقة."))
        
        return ui.div(
            draw_warning_card(f"الموديل {phone} غير موجود داخل قاعدة البيانات."),
            ui.div(
                ui.input_action_button(
                    "trigger_plan_2",
                    "🔵 بدء المطابقة الفنية (Plan 2)",
                    style="width:100%; background:#00bfff; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-bottom:10px;",
                ),
                ui.input_action_button(
                    "trigger_plan_3",
                    "🟠 بدء الخطة البديلة (Plan 3)",
                    style="width:100%; background:#e67e22; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold;",
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
        try:
            stats = get_statistics()
            count = stats.get("phones", 0) if isinstance(stats, dict) else 0
            return ui.div(draw_database_status(count))
        except Exception as e:
            log.error(f"Stats error: {e}")
            return ui.div(draw_database_status(0))

    @reactive.effect
    def watcher_status():
        try:
            status = get_status()
            if isinstance(status, dict) and status.get("status") != "ONLINE":
                log.warning(f"Silent Monitor: {status}")
        except Exception as e:
            log.error(f"Status watcher error: {e}")
