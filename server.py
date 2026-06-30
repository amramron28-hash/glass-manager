hereimport json
import time
from shiny import ui, render, reactive

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
MODELS_INDEX_FILE = "models_index.txt"
STATS_TTL = 3 

def load_models_index():
    try:
        with open(MODELS_INDEX_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except OSError as e:
        log.error(f"Index load error: {e}")
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
    db_trigger = reactive.Value(0)
    current_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)
    suggestions_list = reactive.Value([])
    plan_results = reactive.Value(None)
    plan_inputs = {k: reactive.Value("") for k in ["size", "panel", "sensor"]}
    current_plan_type = reactive.Value(None)
    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])
    autocomplete_index = reactive.Value(None)
    models_index = reactive.Value(load_models_index())
    
    _db_version = reactive.Value(0)
    _last_db_size = reactive.Value(-1)
    _last_monitor_status = reactive.Value("")
    
    # Cache منفصل للإحصائيات والحالة
    _cached_stats = reactive.Value(None)
    _cached_status = reactive.Value(None)
    _stats_time = reactive.Value(0)
    _status_time = reactive.Value(0)

    def invalidate_workflow():
        workflow_cache.invalidate(); coords_cache.invalidate(); _db_version.set(_db_version() + 1)

    def invalidate_stats():
        _cached_stats.set(None); _cached_status.set(None); _stats_time.set(0); _status_time.set(0)

    @reactive.calc
    def database_data():
        db_trigger()
        try:
            db = get_database()
            return db if isinstance(db, dict) else (convert_database_from_raw(db) if isinstance(db, list) else {})
        except Exception as e:
            log.error(f"DB Error: {e}"); return {}

    @reactive.calc
    def fast_index_calc(): return build_fast_index(database_data())

    @reactive.calc
    def get_cached_stats():
        now = time.time()
        if now - _stats_time() < STATS_TTL and _cached_stats() is not None: return _cached_stats()
        try:
            s = get_statistics(); _cached_stats.set(s); _stats_time.set(now); return s
        except: return {}

    @reactive.calc
    def get_cached_status():
        now = time.time()
        if now - _status_time() < STATS_TTL and _cached_status() is not None: return _cached_status()
        try:
            s = get_status(); _cached_status.set(s); _status_time.set(now); return s
        except: return {}

    @reactive.effect
    def watcher_refresh():
        reactive.invalidate_later(5); db_trigger()
        try:
            stats = get_cached_stats()
            size = stats.get("phones", 0) if isinstance(stats, dict) else 0
            
            if size == 0:
                autocomplete_index.set(None); models_index.set([]); custom_panels.set([]); custom_sensors.set([]); _last_db_size.set(0); return
            
            if _last_db_size() == size and autocomplete_index() is not None:
                if show_curtain():
                    q = current_phone(); t = autocomplete_index()
                    if q and t: suggestions_list.set(t.search_prefix(q, 10))
                return

            _last_db_size.set(size); refresh()
            new_idx = load_models_index()
            if autocomplete_index() is None or new_idx != models_index():
                models_index.set(new_idx); autocomplete_index.set(build_autocomplete_index(new_idx))
                invalidate_workflow()
                p, s = extract_panels_sensors(database_data()); custom_panels.set(p); custom_sensors.set(s)
            
            if show_curtain():
                q = current_phone(); t = autocomplete_index()
                if q and t: suggestions_list.set(t.search_prefix(q, 10))
        except Exception as e: log.error(f"Refresh Err: {e}")

    @reactive.effect
    def watcher_status():
        reactive.invalidate_later(10)
        try:
            st = get_cached_status(); cur = st.get("status", "UNKNOWN") if isinstance(st, dict) else "UNKNOWN"
            if cur != _last_monitor_status():
                _last_monitor_status.set(cur)
                log.warning(f"Monitor: {cur}") if cur != "ONLINE" else log.info("Monitor: ONLINE")
        except Exception as e: log.error(f"Status Err: {e}")

    @reactive.effect
    @reactive.event(input.search_query)
    def handle_search():
        q = input.search_query().strip(); current_phone.set(q)
        if not q: suggestions_list.set([]); show_curtain.set(False); return
        t = autocomplete_index()
        if not t: return
        m = t.search_prefix(q, 10); ex = t.contains_exact(q)
        if m and not ex: suggestions_list.set(m); show_curtain.set(True)
        else: suggestions_list.set([]); show_curtain.set(False)

    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list(): return None
        return ui.div(*[ui.div(i, class_="suggestion-row", onclick=f"Shiny.setInputValue('search_query', {json.dumps(i)}, {{priority:'event'}}); Shiny.setInputValue('selected_model_trigger', Math.random(), {{priority:'event'}});") for i in suggestions_list()], class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def confirm_selection():
        show_curtain.set(False); current_phone.set(input.search_query().strip()); invalidate_workflow()

    def process_plan(sz, pn, sn, pt):
        if not all([sz, pn, sn]): plan_results.set(None); return
        r = compute_plan_matches(str(sz), pn, sn, database_data(), fast_index_calc())
        for k, v in zip(["size","panel","sensor"], [str(sz), pn, sn]): plan_inputs[k].set(v)
        current_plan_type.set(pt); plan_results.set(None if is_empty_result(r) else r)

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
    def run_plan_2(): process_plan(input.p2_size(), input.p2_panel(), input.p2_sensor(), "plan_2")

    @reactive.effect
    @reactive.event(input.p3_search)
    def run_plan_3(): process_plan(input.p3_size(), input.p3_panel(), input.p3_sensor(), "plan_3")

    def reset_ui():
        ui.update_text(session, "search_query", value="")
        current_phone.set(""); show_curtain.set(False); suggestions_list.set([])
        plan_results.set(None); current_plan_type.set(None); active_modal.set(None)
        for k in plan_inputs: plan_inputs[k].set("")
        invalidate_workflow()

    def save_model(action):
        ph = current_phone(); sz = plan_inputs["size"](); pn = plan_inputs["panel"](); sn = plan_inputs["sensor"]()
        if not all([ph, sz, pn, sn]): log.warning(f"{action} missing data"); return
        try:
            if add_model(sz, pn, sn, ph):
                refresh(); invalidate_stats(); db_trigger.set(db_trigger() + 1); reset_ui()
                log.info(f"{action}: {ph}")
            else: log.error(f"{action} failed: {ph}")
        except Exception as e: log.error(f"{action} err: {e}")

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge)
    def learn_p2(): save_model("Merge P2")

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge_p3)
    def learn_p3(): save_model("Merge P3")

    @reactive.effect
    @reactive.event(input.btn_foundation)
    def foundation(): save_model("Foundation")

    @reactive.calc
    def cached_coords():
        ph = current_phone().strip()
        if not ph: return None
        return coords_cache.get_or_compute((ph, _db_version()), lambda: find_model_coords(database_data(), ph))

    @reactive.calc
    def cached_workflow():
        c = cached_coords()
        if not c or not c[3]: return None
        return workflow_cache.get_or_compute((current_phone().strip(), _db_version(), current_plan_type()), lambda: run_system_workflows(current_phone().strip(), database_data(), ""))

    @render.ui
    def results_area():
        ph = current_phone().strip()
        if not ph: return None
        if current_plan_type() is None:
            wf = cached_workflow()
            if wf: return ui.div(ui.HTML(wf))
        
        res = plan_results(); pt = current_plan_type()
        if isinstance(res, dict):
            btn = "btn_learn_and_merge" if pt == "plan_2" else "btn_learn_and_merge_p3"
            col = "#2ecc71" if pt == "plan_2" else "#e67e22"
            suf = "(مواصفات يدوية)" if pt == "plan_2" else "(خطة بديلة)"
            return ui.div(
                draw_technical_coords(plan_inputs["size"](), plan_inputs["panel"](), plan_inputs["sensor"](), f"{ph} {suf}"),
                draw_neon_section("مطابقة تماماً", res.get("exact", []), "#2ecc71", "🟢", "exact"),
                draw_neon_section("أكبر بقليل", res.get("plus", []), "#3498db", "", "plus"),
                draw_neon_section("أصغر قليلاً", res.get("minus", []), "#e67e22", "🟠", "minus"),
                ui.input_action_button(btn, "🔄 دمج الهاتف", style=f"width:100%; background:{col}; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-top:15px;")
            )
        
        if res is None and pt == "plan_3":
            return ui.div(draw_warning_card("لا توجد مطابقات. تأسيس مجموعة جديدة؟"), ui.input_action_button("btn_foundation", "➕ تأسيس مجموعة", style="width:100%; background:#9b59b6; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-top:15px;"))
        
        if res is None and pt: return ui.div(draw_warning_card("لم يتم العثور على مجموعة."))
        
        return ui.div(draw_warning_card(f"الموديل {ph} غير موجود."), ui.div(
            ui.input_action_button("trigger_plan_2", "🔵 Plan 2", style="width:100%; background:#00bfff; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-bottom:10px;"),
            ui.input_action_button("trigger_plan_3", "🟠 Plan 3", style="width:100%; background:#e67e22; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold;")
        ))

    @render.ui
    def modal_layer():
        m = active_modal()
        if m == "plan_2": return draw_plan_2_modal(current_phone(), custom_panels(), custom_sensors())
        if m == "plan_3": return draw_plan_3_modal(current_phone(), custom_panels(), custom_sensors())
        return None

    # ✅ التصحيح الحاسم: حساب العداد مباشرة من database_data()
    @render.ui
    def database_status_area():
        """✅ حساب العداد مباشرة من قاعدة البيانات (وليس من statistics)"""
        try:
            db = database_data()
            total = 0
            for panels in db.values():
                if isinstance(panels, dict):
                    for sensors in panels.values():
                        if isinstance(sensors, dict):
                            for data in sensors.values():
                                if isinstance(data, dict):
                                    total += len(data.get("models", []))
            return draw_database_status(total)
        except Exception as e:
            log.error(f"Stats error: {e}")
            return draw_database_status(0)

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer(): await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def close_drawer(): await session.send_custom_message("toggle_drawer", "close")

    @render.ui
    def notifications_area():
        try:
            s = get_cached_status(); src = s.get("source", "غير معروف") if isinstance(s, dict) else "غير متصل"
            return ui.div(f"🔔 المصدر: {src}", class_="metric-box")
        except: return ui.div("🔔 غير متاح", class_="metric-box")

    @render.ui
    def monitor_area():
        try:
            s = get_cached_status(); st = s.get("status", "OFFLINE") if isinstance(s, dict) else "OFFLINE"
            col = "#2ecc71" if st == "ONLINE" else "#e74c3c"
            return ui.div(f"🔒 الحالة: {st}", style=f"color: {col}; font-weight: bold;", class_="metric-box")
        except: return ui.div("🔒 غير متاح", class_="metric-box")
