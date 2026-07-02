import json
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


def _fuzzy_find(key, available_keys):
    """✅ بحث مرن متعدد المستويات مع تنظيف الرموز"""
    if not key or not available_keys:
        return None
    if key in available_keys:
        return key
    key_lower = key.lower().strip().replace("_", " ").replace("-", " ").replace("/", " ")
    for k in available_keys:
        k_lower = k.lower().strip().replace("_", " ").replace("-", " ").replace("/", " ")
        if key_lower == k_lower:
            return k
        if key_lower in k_lower or k_lower in key_lower:
            return k
        key_words = set(key_lower.split())
        k_words = set(k_lower.split())
        common = key_words & k_words
        if len(common) >= max(1, min(len(key_words), len(k_words)) * 0.5):
            return k
    return None


def server(input, output, session):
    # ===== State Management =====
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

    _cached_stats = reactive.Value(None)
    _cached_status = reactive.Value(None)
    _stats_time = reactive.Value(0)
    _status_time = reactive.Value(0)

    def invalidate_workflow():
        workflow_cache.invalidate()
        coords_cache.invalidate()
        _db_version.set(_db_version() + 1)

    def invalidate_stats():
        _cached_stats.set(None)
        _cached_status.set(None)
        _stats_time.set(0)
        _status_time.set(0)

    # ===== Data Layer =====
    @reactive.calc
    def database_data():
        db_trigger()
        try:
            db = get_database()
            return db if isinstance(db, dict) else (convert_database_from_raw(db) if isinstance(db, list) else {})
        except Exception as e:
            log.error(f"DB Error: {e}")
            return {}

    @reactive.calc
    def fast_index_calc():
        return build_fast_index(database_data())

    @reactive.calc
    def get_cached_stats():
        now = time.time()
        if now - _stats_time() < STATS_TTL and _cached_stats() is not None:
            return _cached_stats()
        try:
            s = get_statistics()
            _cached_stats.set(s)
            _stats_time.set(now)
            return s
        except Exception:
            return {}

    @reactive.calc
    def get_cached_status():
        now = time.time()
        if now - _status_time() < STATS_TTL and _cached_status() is not None:
            return _cached_status()
        try:
            s = get_status()
            _cached_status.set(s)
            _status_time.set(now)
            return s
        except Exception:
            return {}

    # ===== Watchers =====
    @reactive.effect
    def watcher_refresh():
        reactive.invalidate_later(5)
        db_trigger()
        try:
            stats = get_cached_stats()
            size = stats.get("phones", 0) if isinstance(stats, dict) else 0
            if size == 0:
                autocomplete_index.set(None)
                models_index.set([])
                custom_panels.set([])
                custom_sensors.set([])
                _last_db_size.set(0)
                return
            if _last_db_size() == size and autocomplete_index() is not None:
                if show_curtain():
                    q = current_phone()
                    t = autocomplete_index()
                    if q and t:
                        suggestions_list.set(t.search_prefix(q, 10))
                return
            _last_db_size.set(size)
            refresh()
            new_idx = load_models_index()
            if autocomplete_index() is None or new_idx != models_index():
                models_index.set(new_idx)
                autocomplete_index.set(build_autocomplete_index(new_idx))
                invalidate_workflow()
                p, s = extract_panels_sensors(database_data())
                custom_panels.set(p)
                custom_sensors.set(s)
            if show_curtain():
                q = current_phone()
                t = autocomplete_index()
                if q and t:
                    suggestions_list.set(t.search_prefix(q, 10))
        except Exception as e:
            log.error(f"Refresh Err: {e}")

    @reactive.effect
    def watcher_status():
        reactive.invalidate_later(10)
        try:
            st = get_cached_status()
            cur = st.get("status", "UNKNOWN") if isinstance(st, dict) else "UNKNOWN"
            if cur != _last_monitor_status():
                _last_monitor_status.set(cur)
                log.warning(f"Monitor: {cur}") if cur != "ONLINE" else log.info("Monitor: ONLINE")
        except Exception as e:
            log.error(f"Status Err: {e}")

    # ===== Search & Autocomplete =====
    @reactive.effect
    @reactive.event(input.search_query)
    def handle_search():
        q = input.search_query().strip()
        current_phone.set(q)
        if not q:
            suggestions_list.set([])
            show_curtain.set(False)
            return
        t = autocomplete_index()
        if not t:
            return
        m = t.search_prefix(q, 10)
        ex = t.contains_exact(q)
        if m and not ex:
            suggestions_list.set(m)
            show_curtain.set(True)
        else:
            suggestions_list.set([])
            show_curtain.set(False)

    @render.ui
    def suggestions_curtain():
        if not show_curtain() or not suggestions_list():
            return None
        return ui.div(
            *[ui.div(
                i, class_="suggestion-row",
                onclick=f"Shiny.setInputValue('search_query', {json.dumps(i)}, {{priority:'event'}}); Shiny.setInputValue('selected_model_trigger', Math.random(), {{priority:'event'}});"
            ) for i in suggestions_list()],
            class_="suggestions-curtain"
        )

    @reactive.effect
    @reactive.event(input.selected_model_trigger)
    def confirm_selection():
        show_curtain.set(False)
        current_phone.set(input.search_query().strip())
        invalidate_workflow()

    # ===== Plan Logic =====
    def process_plan(sz, pn, sn, pt):
        try:
            log.info(f"Processing {pt}: size={sz}, panel={pn}, sensor={sn}")
            if not all([sz, pn, sn]):
                log.warning(f"Process plan {pt}: Missing required fields")
                plan_results.set(None)
                return

            db = database_data()
            idx = fast_index_calc()
            sz_str = str(sz).strip()

            matched_size = _fuzzy_find(sz_str, list(db.keys()))
            if not matched_size:
                log.warning(f"[FUZZY] Size '{sz_str}' not matched. Available: {list(db.keys())[:20]}")
                plan_results.set(None)
                current_plan_type.set(pt)
                for k, v in zip(["size", "panel", "sensor"], [sz_str, pn, sn]):
                    plan_inputs[k].set(v)
                return
            log.info(f"[FUZZY] Size '{sz_str}' → matched to '{matched_size}'")

            available_panels = list(db[matched_size].keys())
            matched_panel = _fuzzy_find(pn, available_panels)
            if not matched_panel:
                log.warning(f"[FUZZY] Panel '{pn}' not matched. Available: {available_panels}")
                plan_results.set(None)
                current_plan_type.set(pt)
                for k, v in zip(["size", "panel", "sensor"], [sz_str, pn, sn]):
                    plan_inputs[k].set(v)
                return
            log.info(f"[FUZZY] Panel '{pn}' → matched to '{matched_panel}'")

            available_sensors = list(db[matched_size][matched_panel].keys())
            matched_sensor = _fuzzy_find(sn, available_sensors)
            if not matched_sensor:
                log.warning(f"[FUZZY] Sensor '{sn}' not matched. Available: {available_sensors}. Using fallback.")
                if available_sensors:
                    matched_sensor = available_sensors[0]
                    log.info(f"[FUZZY] Fallback: using '{matched_sensor}' instead of '{sn}'")
                else:
                    log.error(f"[FUZZY] No sensors available for size='{matched_size}', panel='{matched_panel}'")
                    plan_results.set(None)
                    current_plan_type.set(pt)
                    for k, v in zip(["size", "panel", "sensor"], [sz_str, pn, sn]):
                        plan_inputs[k].set(v)
                    return
            else:
                log.info(f"[FUZZY] Sensor '{sn}' → matched to '{matched_sensor}'")

            start_time = time.time()
            r = compute_plan_matches(matched_size, matched_panel, matched_sensor, db, idx)
            elapsed = time.time() - start_time

            log.info(f"[DIAG] Plan {pt} completed in {elapsed:.2f}s | size='{matched_size}' panel='{matched_panel}' sensor='{matched_sensor}'")
            if isinstance(r, dict):
                log.info(f"[DIAG] Results: exact={len(r.get('exact', []))}, plus={len(r.get('plus', []))}, minus={len(r.get('minus', []))}")
            else:
                log.info(f"[DIAG] Results type={type(r)}, value={r}")

            for k, v in zip(["size", "panel", "sensor"], [sz_str, pn, sn]):
                plan_inputs[k].set(v)
            current_plan_type.set(pt)
            plan_results.set(None if is_empty_result(r) else r)
        except Exception as e:
            log.error(f"Process plan error: {e}", exc_info=True)
            plan_results.set(None)

    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def open_plan_2():
        log.info("Opening Plan 2 modal")
        active_modal.set("plan_2")
        current_plan_type.set("plan_2")
        plan_results.set(None)

    @reactive.effect
    @reactive.event(input.trigger_plan_3)
    def open_plan_3():
        log.info("Opening Plan 3 modal")
        active_modal.set("plan_3")
        current_plan_type.set("plan_3")
        plan_results.set(None)
        if not plan_inputs["size"]():
            plan_inputs["size"].set(6.5)
        if not plan_inputs["panel"]():
            plan_inputs["panel"].set(custom_panels()[0] if custom_panels() else "OLED")
        if not plan_inputs["sensor"]():
            plan_inputs["sensor"].set(custom_sensors()[0] if custom_sensors() else "Virtual")

    @reactive.effect
    @reactive.event(input.p2_search)
    def run_plan_2():
        try:
            log.info("Running Plan 2 search")
            active_modal.set(None)
            sz = input.p2_size()
            pn = input.p2_panel()
            sn = input.p2_sensor()
            log.info(f"Plan 2 inputs: size={sz}, panel={pn}, sensor={sn}")
            if sz is None or pn in (None, "", "__empty__") or sn in (None, "", "__empty__"):
                log.warning("Plan 2: Missing or empty required fields")
                return
            process_plan(sz, pn, sn, "plan_2")
        except Exception as e:
            log.error(f"Run Plan 2 error: {e}", exc_info=True)

    @reactive.effect
    @reactive.event(input.p3_search)
    def run_plan_3():
        try:
            log.info("Running Plan 3 search")
            active_modal.set(None)
            sz = input.p3_size()
            pn = input.p3_panel()
            sn = input.p3_sensor()
            log.info(f"Plan 3 inputs: size={sz}, panel={pn}, sensor={sn}")
            if sz is None or pn in (None, "", "__empty__") or sn in (None, "", "__empty__"):
                log.warning("Plan 3: Missing or empty required fields")
                return
            process_plan(sz, pn, sn, "plan_3")
        except Exception as e:
            log.error(f"Run Plan 3 error: {e}", exc_info=True)

    # ===== Save & Reset =====
    def reset_ui():
        ui.update_text(session, "search_query", value="")
        current_phone.set("")
        show_curtain.set(False)
        suggestions_list.set([])
        plan_results.set(None)
        current_plan_type.set(None)
        active_modal.set(None)
        for k in plan_inputs:
            plan_inputs[k].set("")
        invalidate_workflow()

    def save_model(action):
        ph = current_phone()
        sz = plan_inputs["size"]()
        pn = plan_inputs["panel"]()
        sn = plan_inputs["sensor"]()
        if not all([ph, sz, pn, sn]):
            log.warning(f"{action} missing data")
            return
        try:
            if add_model(sz, pn, sn, ph):
                refresh()
                invalidate_stats()
                db_trigger.set(db_trigger() + 1)
                reset_ui()
                log.info(f"{action}: {ph}")
            else:
                log.error(f"{action} failed: {ph}")
        except Exception as e:
            log.error(f"{action} err: {e}")

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge)
    def learn_p2():
        save_model("Merge P2")

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge_p3)
    def learn_p3():
        save_model("Merge P3")

    @reactive.effect
    @reactive.event(input.btn_foundation)
    def foundation():
        save_model("Foundation")

    # ===== زر (+) لإضافة خيارات جديدة =====
    @reactive.effect
    @reactive.event(input.show_add_panel)
    def handle_show_add_panel():
        show_curtain.set(False)
        suggestions_list.set([])
        m = ui.modal(
            ui.input_text("new_panel_name", "اسم نوع الشاشة الجديد:", placeholder="مثال: IPS LCD"),
            ui.div(
                ui.input_action_button("btn_confirm_add_panel", "✅ إضافة", style="background:#2ecc71; color:white; padding:10px 20px; border:none; border-radius:8px; margin-left:10px;"),
                ui.input_action_button("btn_cancel_add", "❌ إلغاء", style="background:#e74c3c; color:white; padding:10px 20px; border:none; border-radius:8px;"),
                style="text-align:center; margin-top:20px;"
            ),
            title="➕ إضافة نوع شاشة جديد",
            easy_close=True
        )
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.show_add_sensor)
    def handle_show_add_sensor():
        show_curtain.set(False)
        suggestions_list.set([])
        m = ui.modal(
            ui.input_text("new_sensor_name", "اسم المستشعر الجديد:", placeholder="مثال: Proximity Sensor"),
            ui.div(
                ui.input_action_button("btn_confirm_add_sensor", "✅ إضافة", style="background:#2ecc71; color:white; padding:10px 20px; border:none; border-radius:8px; margin-left:10px;"),
                ui.input_action_button("btn_cancel_add", "❌ إلغاء", style="background:#e74c3c; color:white; padding:10px 20px; border:none; border-radius:8px;"),
                style="text-align:center; margin-top:20px;"
            ),
            title="➕ إضافة مستشعر جديد",
            easy_close=True
        )
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.btn_confirm_add_panel)
    def confirm_add_panel():
        try:
            new_value = input.new_panel_name().strip()
            if new_value:
                current = custom_panels()
                if new_value not in current:
                    custom_panels.set(current + [new_value])
                    invalidate_workflow()
                    log.info(f"Added new panel: {new_value}")
            ui.modal_remove()
        except Exception as e:
            log.error(f"Add panel error: {e}")

    @reactive.effect
    @reactive.event(input.btn_confirm_add_sensor)
    def confirm_add_sensor():
        try:
            new_value = input.new_sensor_name().strip()
            if new_value:
                current = custom_sensors()
                if new_value not in current:
                    custom_sensors.set(current + [new_value])
                    invalidate_workflow()
                    log.info(f"Added new sensor: {new_value}")
            ui.modal_remove()
        except Exception as e:
            log.error(f"Add sensor error: {e}")

    @reactive.effect
    @reactive.event(input.btn_cancel_add)
    def cancel_add():
        ui.modal_remove()

    # ===== UI Rendering =====
    @reactive.calc
    def cached_coords():
        ph = current_phone().strip()
        if not ph:
            return None
        return coords_cache.get_or_compute(
            (ph, _db_version()),
            lambda: find_model_coords(database_data(), ph)
        )

    @reactive.calc
    def cached_workflow():
        c = cached_coords()
        if not c or not c[3]:
            return None
        return workflow_cache.get_or_compute(
            (current_phone().strip(), _db_version(), current_plan_type()),
            lambda: run_system_workflows(current_phone().strip(), database_data(), "")
        )

    @render.ui
    def results_area():
        """✅ منطق تسلسل الخطط المعزول + استعادة البطاقات الحمراء في الخطة 1"""
        ph = current_phone().strip()
        if not ph:
            return None

        res = plan_results()
        pt = current_plan_type()

        log.info(f"results_area: phone='{ph}', plan_type='{pt}', has_results={isinstance(res, dict)}")

        # 🔵 الخطة 1: التطابق التلقائي المباشر
        if pt is None:
            wf = cached_workflow()
            if wf:
                return ui.div(ui.HTML(wf))

            # ✅ استعادة البطاقات الحمراء: بحث عن موديلات مشابهة بمستشعر مختلف
            db = database_data()
            warning_cards = []
            ph_lower = ph.lower().strip()

            for size_key, panels in db.items():
                if not isinstance(panels, dict):
                    continue
                for panel_key, sensors in panels.items():
                    if not isinstance(sensors, dict):
                        continue
                    for sensor_key, data in sensors.items():
                        if not isinstance(data, dict):
                            continue
                        for model in data.get("models", []):
                            if ph_lower in model.lower():
                                # وجدنا موديل مشابه - اعرض تحذيرات المستشعر المختلف
                                for other_sensor, other_data in sensors.items():
                                    if other_sensor != sensor_key and isinstance(other_data, dict):
                                        for m in other_data.get("models", [])[:3]:
                                            warning_cards.append(
                                                ui.HTML(f'<div class="flat-warning-card" style="margin-bottom:8px;">⚠️ {escape(str(m))} - نفس المقاس والشاشة لكن المستشعر مختلف: {escape(str(other_sensor))}</div>')
                                            )
                                break
                        if warning_cards:
                            break
                    if warning_cards:
                        break
                if warning_cards:
                    break

            result_elements = [draw_warning_card(f"الموديل {ph} غير موجود في قاعدة البيانات.")]

            if warning_cards:
                result_elements.append(ui.h4("⚠️ تنبيه: موديلات مشابهة بمستشعر مختلف:", style="color:#ff5252; text-align:right; direction:rtl; margin-top:15px;"))
                result_elements.extend(warning_cards)

            result_elements.append(
                ui.input_action_button(
                    "trigger_plan_2",
                    "🔵 بدء المطابقة الفنية (Plan 2)",
                    style="""
                        width:100%;
                        background:#00bfff;
                        color:white;
                        padding:14px;
                        border:none;
                        border-radius:12px;
                        font-weight:bold;
                        margin-top:15px;
                    """
                )
            )

            return ui.div(*result_elements)

        # 🟢 الخطة 2: التكامل اليدوي والمجموعات
        elif pt == "plan_2":
            log.info("Rendering Plan 2 results")
            if isinstance(res, dict) and not is_empty_result(res):
                return ui.div(
                    draw_technical_coords(
                        plan_inputs["size"](),
                        plan_inputs["panel"](),
                        plan_inputs["sensor"](),
                        f"{ph} (مواصفات يدوية)"
                    ),
                    draw_neon_section("مطابقة تماماً", res.get("exact", []), "#2ecc71", "🟢", "exact"),
                    draw_neon_section("أكبر بقليل", res.get("plus", []), "#3498db", "", "plus"),
                    draw_neon_section("أصغر قليلاً", res.get("minus", []), "#e67e22", "🟠", "minus"),
                    ui.input_action_button(
                        "btn_learn_and_merge",
                        "🔄 دمج الهاتف داخل هذه المجموعة",
                        style="width:100%; background:#2ecc71; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-top:15px;"
                    )
                )
            else:
                return ui.div(
                    draw_warning_card(
                        "لم يتم العثور على أي تطابق في المجموعات الحالية بالمواصفات المُدخلة."
                    ),
                    ui.input_action_button(
                        "trigger_plan_3",
                        "🟠 انتقل لخطة الطوارئ (Plan 3)",
                        style="""
                            width:100%;
                            background:#e67e22;
                            color:white;
                            padding:14px;
                            border:none;
                            border-radius:12px;
                            font-weight:bold;
                            margin-top:10px;
                        """
                    )
                )

        # 🟠 الخطة 3: التأسيس والإنشاء (خطة الطوارئ)
        elif pt == "plan_3":
            log.info("Rendering Plan 3 results")
            if isinstance(res, dict) and not is_empty_result(res):
                return ui.div(
                    draw_technical_coords(
                        plan_inputs["size"](),
                        plan_inputs["panel"](),
                        plan_inputs["sensor"](),
                        f"{ph} (خطة طوارئ)"
                    ),
                    draw_neon_section("مطابقة تماماً", res.get("exact", []), "#2ecc71", "🟢", "exact"),
                    draw_neon_section("أكبر بقليل", res.get("plus", []), "#3498db", "", "plus"),
                    draw_neon_section("أصغر قليلاً", res.get("minus", []), "#e67e22", "🟠", "minus"),
                    ui.input_action_button(
                        "btn_learn_and_merge_p3",
                        "🔄 دمج الهاتف داخل هذه المجموعة",
                        style="width:100%; background:#e67e22; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-top:15px;"
                    )
                )
            else:
                return ui.div(
                    draw_warning_card("لا توجد أي مجموعة مشابهة. هل تريد تأسيس مجموعة جديدة بهذا الهاتف؟"),
                    ui.input_action_button(
                        "btn_foundation",
                        "➕ تأسيس مجموعة جديدة",
                        style="width:100%; background:#9b59b6; color:white; padding:14px; border:none; border-radius:12px; font-weight:bold; margin-top:15px;"
                    )
                )

        else:
            log.warning(f"Unexpected plan type: {pt}")
            return ui.div(draw_warning_card("حدث خطأ في نظام الخطط. يرجى إعادة التحميل."))

    @render.ui
    def modal_layer():
        m = active_modal()
        if m == "plan_2":
            return draw_plan_2_modal(current_phone(), custom_panels(), custom_sensors())
        elif m == "plan_3":
            return draw_plan_3_modal(current_phone(), custom_panels(), custom_sensors())
        elif m == "add_panel":
            return ui.modal(
                ui.input_text("new_panel_name", "اسم نوع الشاشة الجديد:", placeholder="مثال: IPS LCD"),
                ui.div(
                    ui.input_action_button("btn_confirm_add_panel", "✅ إضافة", style="background:#2ecc71; color:white; padding:10px 20px; border:none; border-radius:8px; margin-left:10px;"),
                    ui.input_action_button("btn_cancel_add", "❌ إلغاء", style="background:#e74c3c; color:white; padding:10px 20px; border:none; border-radius:8px;"),
                    style="text-align:center; margin-top:20px;"
                ),
                title="➕ إضافة نوع شاشة جديد",
                easy_close=True
            )
        elif m == "add_sensor":
            return ui.modal(
                ui.input_text("new_sensor_name", "اسم المستشعر الجديد:", placeholder="مثال: Proximity Sensor"),
                ui.div(
                    ui.input_action_button("btn_confirm_add_sensor", "✅ إضافة", style="background:#2ecc71; color:white; padding:10px 20px; border:none; border-radius:8px; margin-left:10px;"),
                    ui.input_action_button("btn_cancel_add", "❌ إلغاء", style="background:#e74c3c; color:white; padding:10px 20px; border:none; border-radius:8px;"),
                    style="text-align:center; margin-top:20px;"
                ),
                title="➕ إضافة مستشعر جديد",
                easy_close=True
            )
        else:
            return None

    # ===== الإعدادات الديناميكية =====
    @render.ui
    def database_status_area():
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
    async def open_drawer():
        await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def close_drawer():
        await session.send_custom_message("toggle_drawer", "close")

    @render.ui
    def notifications_area():
        try:
            s = get_cached_status()
            src = s.get("source", "غير معروف") if isinstance(s, dict) else "غير متصل"
            return ui.div(f"🔔 المصدر: {src}", class_="metric-box")
        except Exception:
            return ui.div("🔔 غير متاح", class_="metric-box")

    @render.ui
    def monitor_area():
        try:
            s = get_cached_status()
            st = s.get("status", "OFFLINE") if isinstance(s, dict) else "OFFLINE"
            col = "#2ecc71" if st == "ONLINE" else "#e74c3c"
            return ui.div(
                f"🔒 الحالة: {st}",
                style=f"color: {col}; font-weight: bold;",
                class_="metric-box"
            )
        except Exception:
            return ui.div("🔒 غير متاح", class_="metric-box")
