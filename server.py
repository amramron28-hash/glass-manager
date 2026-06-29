import json
from shiny import ui, render, reactive
from hashlib import md5

# استيراد الثوابت والخدمات
from core.constants import COLORS, IDS, MAX_SUGGESTIONS, REFRESH_INTERVAL_SEC
from services.save_service import perform_save
from services.search_service import build_autocomplete_index, find_model_coords
from services.plan_engine import compute_plan_matches, is_empty_result
from services.index_service import build_fast_index, extract_panels_sensors
from services.cache_service import workflow_cache, coords_cache
from core.logger import get_logger

from database import add_model
from silent_monitor import get_database, refresh, get_status, get_statistics
from logic_engine import run_system_workflows
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, draw_warning_card,
    draw_technical_coords, draw_neon_section, draw_database_status
)

log = get_logger("server")


def load_models_index():
    try:
        with open(IDS.get("models_index_file", "models_index.txt"), "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except OSError as e:
        log.error(f"Failed to load models index: {e}")
        return []


def convert_database_from_raw(rows):
    db = {}
    if not isinstance(rows, list): return db
    for item in rows:
        if not isinstance(item, dict): continue
        size = str(item.get("size") or "").strip()
        panel = str(item.get("panel") or "Notch Screen").strip()
        sensor = str(item.get("sensor") or "hardware_top_sensor").strip()
        model = str(item.get("model_name") or "").strip()
        if not size or not model: continue
        db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})
        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)
    return db


def server(input, output, session):
    # ===== State Management =====
    db_trigger = reactive.Value(0)
    current_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)
    suggestions_list = reactive.Value([])
    plan_results = reactive.Value(None)
    plan_failed = reactive.Value(False)

    plan_inputs = {k: reactive.Value("") for k in ["size", "panel", "sensor"]}
    current_plan_type = reactive.Value(None)
    
    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])
    autocomplete_index = reactive.Value(None)
    models_index = reactive.Value(load_models_index())
    
    _db_version = reactive.Value(0)
    _last_db_hash = reactive.Value("")
    _last_monitor_status = reactive.Value("")

    # ===== Data Layer & Cached Calcs =====
    @reactive.calc
    def database_data():
        db_trigger()
        try:
            db = get_database()
            if isinstance(db, dict): return db
            if isinstance(db, list): return convert_database_from_raw(db)
            return {}
        except Exception as e:
            log.error(f"Database error: {e}")
            return {}

    @reactive.calc
    def fast_index_calc():
        return build_fast_index(database_data())

    @reactive.calc
    def system_stats():
        """حساب الإحصائيات مرة واحدة وإعادة استخدامها"""
        try:
            stats = get_statistics()
            return stats.get("phones", 0) if isinstance(stats, dict) else 0
        except: return 0

    @reactive.calc
    def system_status():
        """جلب حالة النظام مرة واحدة"""
        try:
            return get_status() or {}
        except: return {}

    # ===== Watchers (Optimized) =====
    @reactive.effect
    def watcher_refresh():
        reactive.invalidate_later(REFRESH_INTERVAL_SEC)
        db_trigger()
        
        try:
            raw_db = get_database()
            # استخدام Hash بدلاً من Count لاكتشاف التغييرات الدقيقة
            current_hash = md5(json.dumps(raw_db, sort_keys=True, default=str).encode()).hexdigest()
            
            if _last_db_hash() == current_hash and autocomplete_index() is not None:
                if show_curtain():
                    query = current_phone()
                    trie = autocomplete_index()
                    if query and trie:
                        suggestions_list.set(trie.search_prefix(query, MAX_SUGGESTIONS))
                return

            log.info("[WATCHER] Data changed detected via Hash.")
            _last_db_hash.set(current_hash)
            refresh()
            
            new_index = load_models_index()
            if autocomplete_index() is None or new_index != models_index():
                models_index.set(new_index)
                autocomplete_index.set(build_autocomplete_index(new_index))
                
                panels, sensors = extract_panels_sensors(database_data())
                custom_panels.set(panels)
                custom_sensors.set(sensors)
                
                workflow_cache.invalidate()
                coords_cache.invalidate()
                _db_version.set(_db_version() + 1)

            if show_curtain():
                query = current_phone()
                trie = autocomplete_index()
                if query and trie:
                    suggestions_list.set(trie.search_prefix(query, MAX_SUGGESTIONS))
        except Exception as e:
            log.error(f"Refresh error: {e}")

    @reactive.effect
    def watcher_status():
        reactive.invalidate_later(REFRESH_INTERVAL_SEC)
        try:
            status = system_status()
            current_st = status.get("status", "UNKNOWN")
            if current_st != _last_monitor_status():
                _last_monitor_status.set(current_st)
                log.warning(f"Silent Monitor: {current_st}") if current_st != "ONLINE" else log.info("Silent Monitor: ONLINE")
        except Exception as e:
            log.error(f"Status watcher error: {e}")

    # ===== Search Handlers =====
    @reactive.effect
    @reactive.event(input.search_query)
    def handle_search():
        query = input.search_query().strip()
        current_phone.set(query)
        if not query:
            suggestions_list.set([]); show_curtain.set(False); return
        
        trie = autocomplete_index()
        if not trie: return
        
        matches = trie.search_prefix(query, MAX_SUGGESTIONS)
        exact = trie.contains_exact(query)
        
        if matches and not exact:
            suggestions_list.set(matches); show_curtain.set(True)
        else:
            suggestions_list.set([]); show_curtain.set(False)

    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list(): return None
        rows = []
        for item in suggestions_list():
            safe = json.dumps(item)
            rows.append(ui.div(item, class_="suggestion-row", 
                onclick=f"Shiny.setInputValue('{IDS['search_query']}', {safe}, {{priority:'event'}}); Shiny.setInputValue('{IDS['selected_trigger']}', Math.random(), {{priority:'event'}});"))
        return ui.div(*rows, class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def confirm_selection():
        show_curtain.set(False)
        current_phone.set(input.search_query().strip())
        workflow_cache.invalidate(); coords_cache.invalidate()

    # ===== Plan Logic =====
    @reactive.effect
    def handle_plan_failure():
        if plan_results() is None and current_plan_type() == "plan_2" and not plan_failed():
            plan_failed.set(True)
            active_modal.set("plan_3")
            current_plan_type.set("plan_3")

    def execute_plan(size, panel, sensor, p_type):
        for k, v in zip(["size", "panel", "sensor"], [str(size), panel, sensor]):
            plan_inputs[k].set(v)
        current_plan_type.set(p_type); plan_failed.set(False)
        
        if not all([size, panel, sensor]):
            plan_results.set(None); return
            
        results = compute_plan_matches(str(size), panel, sensor, database_data(), fast_index_calc())
        plan_results.set(None if is_empty_result(results) else results)

    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def open_plan_2():
        if current_phone(): active_modal.set("plan_2"); current_plan_type.set("plan_2")

    @reactive.effect
    @reactive.event(input.trigger_plan_3)
    def open_plan_3():
        if current_phone(): active_modal.set("plan_3"); current_plan_type.set("plan_3")

    @reactive.effect
    @reactive.event(input.p2_search)
    def run_plan_2(): execute_plan(input.p2_size(), input.p2_panel(), input.p2_sensor(), "plan_2")

    @reactive.effect
    @reactive.event(input.p3_search)
    def run_plan_3(): execute_plan(input.p3_size(), input.p3_panel(), input.p3_sensor(), "plan_3")

    # ===== Save Handlers =====
    def reset_state(full=False):
        if full:
            ui.update_text(session, IDS["search_query"], value="")
            current_phone.set(""); show_curtain.set(False); suggestions_list.set([])
        plan_results.set(None); current_plan_type.set(None); active_modal.set(None)
        plan_failed.set(False)
        for k in plan_inputs: plan_inputs[k].set("")
        workflow_cache.invalidate(); coords_cache.invalidate()

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge)
    def learn_p2():
        if perform_save(current_phone(), *[plan_inputs[k]() for k in ["size","panel","sensor"]], "Merge P2"):
            db_trigger.set(db_trigger() + 1); reset_state(full=True)

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge_p3)
    def learn_p3():
        if perform_save(current_phone(), *[plan_inputs[k]() for k in ["size","panel","sensor"]], "Merge P3"):
            db_trigger.set(db_trigger() + 1); reset_state(full=True)

    @reactive.effect
    @reactive.event(input.btn_foundation)
    def foundation_new_group():
        if perform_save(current_phone(), *[plan_inputs[k]() for k in ["size","panel","sensor"]], "Foundation"):
            db_trigger.set(db_trigger() + 1); reset_state(full=True)

    # ===== UI Rendering (Optimized) =====
    @reactive.calc
    def cached_coords():
        phone = current_phone().strip()
        if not phone: return None
        return coords_cache.get_or_compute((phone, _db_version()), lambda: find_model_coords(database_data(), phone))

    @reactive.calc
    def cached_workflow():
        coords = cached_coords()
        if not coords or not coords[3]: return None
        return workflow_cache.get_or_compute(
            (current_phone().strip(), _db_version(), current_plan_type()),
            lambda: run_system_workflows(current_phone().strip(), database_data(), "")
        )

    def render_plan_results(phone, res, p_type):
        btn_id = IDS["merge_p2"] if p_type == "plan_2" else IDS["merge_p3"]
        color = COLORS["exact"] if p_type == "plan_2" else COLORS["minus"]
        suffix = "(مواصفات يدوية)" if p_type == "plan_2" else "(خطة بديلة)"
        inputs = {k: plan_inputs[k]() for k in ["size", "panel", "sensor"]}
        
        sections = [("مطابقة تماماً", res.get("exact", []), COLORS["exact"], "🟢", "exact"),
                    ("أكبر بقليل", res.get("plus", []), COLORS["plus"], "", "plus"),
                    ("أصغر قليلاً", res.get("minus", []), COLORS["minus"], "🟠", "minus")]
        
        cards = [draw_technical_coords(inputs["size"], inputs["panel"], inputs["sensor"], f"{phone} {suffix}")]
        cards.extend([draw_neon_section(t, l, c, i, pt) for t, l, c, i, pt in sections])
        cards.append(ui.input_action_button(btn_id, "🔄 دمج الهاتف", 
            style=f"width:100%; background:{color}; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-top:15px;"))
        return ui.div(*cards)

    @render.ui
    def results_area():
        phone = current_phone().strip()
        if not phone: return None
        
        if current_plan_type() is None:
            wf = cached_workflow()
            if wf: return ui.div(ui.HTML(wf))
            
        res = plan_results(); p_type = current_plan_type()
        
        if isinstance(res, dict): return render_plan_results(phone, res, p_type)
        if res is None and p_type == "plan_2" and plan_failed():
            return ui.div(draw_warning_card("جاري الانتقال لـ Plan 3..."))
        if res is None and p_type == "plan_3":
            return ui.div(draw_warning_card("لا توجد مطابقات. تأسيس مجموعة جديدة؟"),
                ui.input_action_button(IDS["foundation"], "➕ تأسيس مجموعة",
                    style=f"width:100%; background:{COLORS['foundation']}; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-top:15px;"))
                    
        return ui.div(draw_warning_card(f"الموديل {phone} غير موجود."),
            ui.div(
                ui.input_action_button(IDS["trigger_p2"], "🔵 Plan 2", style=f"width:100%; background:{COLORS['plan2_btn']}; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-bottom:10px;"),
                ui.input_action_button(IDS["trigger_p3"], "🟠 Plan 3", style=f"width:100%; background:{COLORS['plan3_btn']}; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold;")))

    @render.ui
    def modal_layer():
        mode = active_modal()
        if mode == "plan_2": return draw_plan_2_modal(current_phone(), custom_panels(), custom_sensors())
        if mode == "plan_3": return draw_plan_3_modal(current_phone(), custom_panels(), custom_sensors())
        return None

    @render.ui
    def database_status_area():
        return ui.div(draw_database_status(system_stats()))

    @render.ui
    def notifications_area():
        st = system_status()
        src = st.get("source", "غير معروف") if isinstance(st, dict) else "غير متصل"
        return ui.div(f"🔔 المصدر: {src}", class_="metric-box")

    @render.ui
    def monitor_area():
        st = system_status()
        state = st.get("status", "OFFLINE") if isinstance(st, dict) else "OFFLINE"
        color = COLORS["exact"] if state == "ONLINE" else COLORS["warning"] if "warning" in COLORS else "#e74c3c"
        return ui.div(f"🔒 الحالة: {state}", style=f"color: {color}; font-weight: bold;", class_="metric-box")

    # ===== Settings Controls (Async Fixed) =====
    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer():
        await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def close_drawer():
        await session.send_custom_message("toggle_drawer", "close")
