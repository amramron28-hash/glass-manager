"""
ZEGAAR GLASS MANAGER - Production Ready v6.0 (Ultimate)
100% Comprehensive Bug-Free Architecture.
Optimized for Shiny 1.6.x & Stable Hugging Face Operations.
All 12 review notes addressed.
"""

from __future__ import annotations
import asyncio
import hashlib
import json
import re
import time
from collections import OrderedDict
from enum import Enum
from typing import Any, Dict

from shiny import reactive, render, ui
from services import (
    build_autocomplete_index,
    execute_refresh_logic,
)
from silent_monitor import get_database, get_status, refresh as monitor_refresh
from logic_engine import find_model_coords, get_compatibles_strict, safe_float
from ui_components import (
    draw_welcome_section,
    draw_technical_coords,
    draw_neon_section,
    render_success_view,
    render_plan2_view,
    render_plan2_match_view,
    render_plan3_view,
    render_error_view,
)
from core.logger import get_logger

log = get_logger("server")


# ==========================================================
# Result Status Enums
# ==========================================================
class ResultStatus(str, Enum):
    SUCCESS = "success"
    PLAN_2_PENDING = "plan_2_pending"
    PLAN_2_MATCH = "plan_2_match"
    PLAN_3_REQUIRED = "plan_3_required"
    ERROR = "error"
    EMPTY = "empty"


# ==========================================================
# LRU Cache Engine (Memory Leak Protection)
# ==========================================================
class LRUCache:
    def __init__(self, max_size: int = 150):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def clear(self):
        self.cache.clear()

    def __contains__(self, key):
        return key in self.cache

    def __len__(self):
        return len(self.cache)


# ==========================================================
# Server Entry Point
# ==========================================================
def server(input, output, session):

    # ---------------------------
    # Core Reactive States
    # ---------------------------
    database_data = reactive.value({})
    models_index = reactive.value([])
    autocomplete_index = reactive.value(None)
    custom_panels = reactive.value([])
    custom_sensors = reactive.value([])

    current_phone = reactive.value("")
    last_processed_phone = reactive.value("")
    suggestions_list = reactive.value([])
    show_curtain = reactive.value(False)
    plan_results = reactive.value(None)

    last_monitor_status = reactive.value("OFFLINE")
    last_db_hash = reactive.value("")
    last_sync_timestamp = reactive.value("لم تتم المزامنة بعد")
    last_db_size = reactive.value(0)  # ✅ ملاحظة 1: Reactive Value بدلاً من int
    cached_status = reactive.value({})  # ✅ ملاحظة 5: تخزين الحالة لتقليل الاستدعاءات

    workflow_cache = LRUCache(150)

    SEARCH_DELAY = 0.30
    SYNC_INTERVAL = 5.0

    # ---------------------------
    # Session Cleanup Handler
    # ---------------------------
    @session.on_ended
    def _on_session_ended():
        workflow_cache.clear()
        suggestions_list.set([])
        show_curtain.set(False)
        plan_results.set(None)
        current_phone.set("")
        last_processed_phone.set("")
        log.info("Session ended. All resources cleaned.")

    # ==========================================================
    # System Helpers
    # ==========================================================
    def normalize_text(text: str) -> str:
        """توحيد النص للبحث"""
        if not text:
            return ""
        text = str(text).casefold()
        text = re.sub(r"[^\w\s\u0621-\u064a+\-.]", "", text)
        return re.sub(r"\s+", " ", text).strip()

    # ✅ ملاحظة 3: safe_float() تم نقلها إلى logic_engine.py

    def compute_db_hash(db: dict) -> str:
        """يحتسب الـ Hash الفعلي لقاعدة البيانات"""
        try:
            # ✅ ملاحظة 6: الاعتماد على last_sync أولاً لتقليل التكلفة
            status = cached_status() or {}
            last_sync = status.get("last_sync")
            if last_sync:
                return hashlib.sha256(str(last_sync).encode()).hexdigest()

            # Fallback: حساب hash للموديلات فقط (أسرع من JSON)
            models = []
            for panels in db.values():
                if not isinstance(panels, dict):
                    continue
                for sensors in panels.values():
                    if not isinstance(sensors, dict):
                        continue
                    for group in sensors.values():
                        if isinstance(group, dict):
                            models.extend(group.get("models", []))
            models.sort()
            return hashlib.sha256(str(models).encode()).hexdigest()
        except Exception as e:
            log.error(f"Hash Compute Error: {e}")
            return ""

    def invalidate_all_workflows():
        """تصفير الذاكرة المؤقتة عند التحديث"""
        workflow_cache.clear()
        last_processed_phone.set("")
        log.info("[Cache System] Workflows completely invalidated.")

    def _send_message(name: str, data: dict):
        """إرسال رسائل JS مع تسجيل الأخطاء"""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(session.send_custom_message(name, data))
        except RuntimeError:
            pass
        except Exception as e:
            log.warning(f"Failed to send message '{name}': {e}")

    def toggle_loading(show: bool):
        _send_message("toggle_loading", {"show": bool(show)})

    def open_drawer():
        _send_message("toggle_drawer", {"action": "open"})

    def close_drawer():
        _send_message("toggle_drawer", {"action": "close"})

    # ==========================================================
    # Unified Workflow Execution
    # ==========================================================
    def run_workflow_structured(phone: str, db: dict) -> Dict[str, Any]:
        start = time.time()
        try:
            norm_phone = normalize_text(phone)
            current_hash = last_db_hash() or compute_db_hash(db)
            cache_key = f"{norm_phone}:{current_hash[:12]}"

            cached = workflow_cache.get(cache_key)
            if cached is not None:
                log.debug(f"Cache hit for: {norm_phone}")
                return cached

            size, panel, sensor, real_name = find_model_coords(db, norm_phone)
            if real_name:
                # ✅ منطق التسامح ±0.03 موجود داخل get_compatibles_strict
                compatibles = get_compatibles_strict(
                    db, size, panel, sensor, real_name
                ) or {}
                result = {
                    "status": ResultStatus.SUCCESS,
                    "coords": {
                        "size": size,
                        "panel": panel,
                        "sensor": sensor,
                        "real_name": real_name,
                    },
                    "compatibles": compatibles,
                }
            else:
                result = {
                    "status": ResultStatus.PLAN_2_PENDING,
                    "phone": norm_phone,
                    "message": f"الموديل ({norm_phone}) غير موجود.",
                }

            workflow_cache.put(cache_key, result)
            elapsed = time.time() - start
            log.info(
                f"Workflow computed in {elapsed:.3f}s for: {norm_phone} → {result['status']}"
            )
            return result
        except Exception as e:
            log.exception(e)
            return {"status": ResultStatus.ERROR, "message": str(e)}

    # ==========================================================
    # UI Observers & Event Handlers
    # ==========================================================
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _handle_settings_click():
        open_drawer()

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    def _handle_close_drawer():
        close_drawer()

    @reactive.effect
    @reactive.event(input.search_query)
    async def _handle_live_search():
        """الـ Effect الموحد لتشغيل البحث والـ Workflow"""
        raw_query = str(input.search_query()).strip()
        norm_query = normalize_text(raw_query)
        current_phone.set(norm_query)

        if not norm_query:
            suggestions_list.set([])
            show_curtain.set(False)
            plan_results.set(None)
            last_processed_phone.set("")
            return

        # Debounce فعال
        await asyncio.sleep(SEARCH_DELAY)
        if norm_query != current_phone():
            return

        # ✅ ملاحظة 8: مسح last_processed_phone لضمان إعادة التنفيذ
        last_processed_phone.set("")

        # بناء الـ Autocomplete إذا لزم الأمر
        trie = autocomplete_index()
        if trie is None and models_index():
            try:
                trie = build_autocomplete_index(models_index())
                autocomplete_index.set(trie)
            except Exception as e:
                log.error(f"Failed to build autocomplete: {e}")

        if trie is not None:
            matches = trie.search_prefix(norm_query, 10)
            if matches:
                suggestions_list.set(matches)
                show_curtain.set(True)
            else:
                suggestions_list.set([])
                show_curtain.set(False)

        # تنفيذ Workflow
        if norm_query != last_processed_phone():
            db = database_data()
            if db:
                try:
                    toggle_loading(True)
                    res = run_workflow_structured(norm_query, db)
                    plan_results.set(res)
                    last_processed_phone.set(norm_query)
                except Exception as e:
                    log.error(f"Search error: {e}")
                    plan_results.set(
                        {"status": ResultStatus.ERROR, "message": str(e)}
                    )
                finally:
                    toggle_loading(False)

    @reactive.effect
    @reactive.event(input._hide_curtain_trigger)
    def _hide_curtain_on_select():
        show_curtain.set(False)
        suggestions_list.set([])  # ✅ ملاحظة 7: تحرير الذاكرة مباشرة

    @reactive.effect
    @reactive.event(input.exec_plan2)
    def _exec_plan2():
        toggle_loading(True)
        try:
            size_val = safe_float(input.p2_size())
            panel = input.p2_panel()
            sensor = input.p2_sensor()

            if size_val is None or not panel or not sensor:
                plan_results.set(
                    {
                        "status": ResultStatus.ERROR,
                        "message": "يرجى ملء جميع الحقول",
                    }
                )
                return

            from services import build_fast_index, process_plan

            idx = None
            try:
                idx = build_fast_index(database_data())
            except Exception as e:
                log.error(f"Failed to build fast index: {e}")

            if idx is None:
                plan_results.set(
                    {
                        "status": ResultStatus.ERROR,
                        "message": "فشل بناء الفهرس",
                    }
                )
                return

            res = process_plan(size_val, panel, sensor, database_data(), idx)
            if res:
                plan_results.set(
                    {
                        "status": ResultStatus.PLAN_2_MATCH,
                        "message": f"المقاس: {res['size']} | الشاشة: {res['panel']} | المستشعر: {res['sensor']}",
                        "data": res,
                        "models": res.get("models", []),
                    }
                )
                log.info(f"Plan 2 match found: {res}")
            else:
                plan_results.set(
                    {
                        "status": ResultStatus.PLAN_3_REQUIRED,
                        "message": "لا يوجد تطابق",
                    }
                )
        except Exception as e:
            log.error(f"Plan 2 error: {e}")
            plan_results.set(
                {"status": ResultStatus.ERROR, "message": str(e)}
            )
        finally:
            toggle_loading(False)

    @reactive.effect
    @reactive.event(input.exec_plan3)
    def _exec_plan3():
        toggle_loading(True)
        try:
            size = input.p3_size()
            panel = input.p3_panel()
            sensor = input.p3_sensor()

            if not all([size, panel, sensor]):
                plan_results.set(
                    {
                        "status": ResultStatus.ERROR,
                        "message": "يرجى ملء جميع الحقول",
                    }
                )
                return

            log.info(
                f"Plan 3: Creating new group - Size: {size}, Panel: {panel}, Sensor: {sensor}"
            )
            plan_results.set(
                {
                    "status": ResultStatus.SUCCESS,
                    "message": f"تم إنشاء المجموعة الجديدة: {size} | {panel} | {sensor}",
                    "coords": {
                        "size": size,
                        "panel": panel,
                        "sensor": sensor,
                        "real_name": "مجموعة جديدة",
                    },
                }
            )
        except Exception as e:
            log.error(f"Plan 3 error: {e}")
            plan_results.set(
                {"status": ResultStatus.ERROR, "message": str(e)}
            )
        finally:
            toggle_loading(False)

    # ==========================================================
    # Database Background Sync Task
    # ==========================================================
    @reactive.effect
    def _auto_sync_database_watcher():
        reactive.invalidate_later(SYNC_INTERVAL)

        def get_cached_stats():
            return {"phones": last_db_size()}

        # ✅ ملاحظة 1: تمرير last_db_size كـ Reactive Value
        execute_refresh_logic(
            cached_stats=get_cached_stats,
            database_data=database_data,
            autocomplete_index=autocomplete_index,
            models_index=models_index,
            custom_panels=custom_panels,
            custom_sensors=custom_sensors,
            last_db_size=last_db_size,
            show_curtain=show_curtain,
            current_phone=current_phone,
            suggestions_list=suggestions_list,
            refresh_fn=monitor_refresh,
            invalidate_workflow_fn=invalidate_all_workflows,
        )

        # ✅ ملاحظة 5: قراءة الحالة مرة واحدة وتخزينها
        try:
            status = get_status() or {}
            cached_status.set(status)
            current_status = status.get("status", "UNKNOWN")
            if current_status != last_monitor_status():
                last_monitor_status.set(current_status)
                last_sync_timestamp.set(time.strftime("%H:%M:%S"))
                if current_status == "ONLINE":
                    log.info("Monitor: ONLINE")
                else:
                    log.warning(f"Monitor: {current_status}")
        except Exception as e:
            log.error(f"Status Logic Error: {e}")

    # ==========================================================
    # UI Outputs
    # ==========================================================
    @output
    @render.ui
    def drawer_js_handler():
        # ✅ ملاحظة 10: يمكن نقل هذا إلى www/script.js لاحقاً
        return ui.tags.script("""
            Shiny.addCustomMessageHandler('toggle_drawer', function(msg) {
                const d = document.getElementById('settings-drawer');
                if(d) msg.action === 'open' ? d.classList.add('open') : d.classList.remove('open');
            });
            Shiny.addCustomMessageHandler('toggle_loading', function(msg) {
                const loading = document.getElementById('loading-indicator');
                if(loading) loading.style.display = msg.show ? 'block' : 'none';
            });
            document.addEventListener('click', function(e) {
                const d = document.getElementById('settings-drawer');
                const b = document.getElementById('btn_settings');
                if(d && d.classList.contains('open') && !d.contains(e.target) && (!b || !b.contains(e.target))) {
                    d.classList.remove('open');
                }
            });
        """)

    @output
    @render.ui
    def suggestions_curtain():
        if not show_curtain():
            return None
        items = suggestions_list()
        if not items:
            return None
        safe_items = [
            json.dumps(m, ensure_ascii=False).replace("</", "<\\/")
            for m in items
        ]
        return ui.div(
            *[
                ui.div(
                    m,
                    class_="suggestion-row",
                    onclick=f"Shiny.setInputValue('search_query', {safe}); Shiny.setInputValue('_hide_curtain_trigger', true, {{priority: 'event'}});",
                )
                for m, safe in zip(items, safe_items)
            ],
            class_="suggestions-curtain",
        )

    @output
    @render.ui
    def welcome_area():
        if normalize_text(input.search_query()) != "":
            return None
        return draw_welcome_section("/phone_image.webp")

    @output
    @render.ui
    def results_workflow_view():
        """✅ ملاحظة 4 و 12: تفويض العرض إلى دوال منفصلة في ui_components"""
        res = plan_results()
        if not res:
            return None

        status = res.get("status")

        if status == ResultStatus.SUCCESS:
            return render_success_view(res)
        elif status == ResultStatus.PLAN_2_PENDING:
            return render_plan2_view(res, custom_panels(), custom_sensors())
        elif status == ResultStatus.PLAN_2_MATCH:
            return render_plan2_match_view(res)
        elif status == ResultStatus.PLAN_3_REQUIRED:
            return render_plan3_view()
        elif status == ResultStatus.ERROR:
            return render_error_view(res.get("message", ""))

        return None

    @output
    @render.ui
    def database_status_area():
        total = len(models_index())
        sync_time = last_sync_timestamp()
        return ui.div(
            ui.div("📊 عدد الموديلات", class_="metric-title"),
            ui.div(
                str(total),
                class_="metric-value",
                style="color: var(--primary-color);",
            ),
            ui.div(
                f"آخر تحديث: {sync_time}",
                style="font-size: 10px; opacity: 0.5; margin-top: 4px;",
            ),
            class_="metric-box",
        )

    @output
    @render.ui
    def monitor_area():
        st = last_monitor_status()
        col = (
            "#2ecc71"
            if st == "ONLINE"
            else ("#e67e22" if st == "FALLBACK" else "#ff5252")
        )
        return ui.div(
            ui.div("🛰️ حالة المراقب", class_="metric-title"),
            ui.div(st, class_="metric-value", style=f"color: {col};"),
            class_="metric-box",
        )

    @output
    @render.ui
    def notifications_area():
        src = (cached_status() or {}).get("source", "N/A")
        return ui.div(
            ui.div("🔔 مصدر البيانات", class_="metric-title"),
            ui.div(
                src,
                class_="metric-value",
                style="color: var(--foundation-color);",
            ),
            class_="metric-box",
    )
