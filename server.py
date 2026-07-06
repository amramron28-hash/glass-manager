"""
ZEGAAR GLASS MANAGER
Production Ready v5.0
Fully Optimized for Shiny 1.6.x
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time

from collections import OrderedDict
from enum import Enum
from typing import Any, Dict, Optional

from shiny import reactive, render, ui

from services import (
    build_autocomplete_index,
    build_fast_index,
    process_plan,
)

from silent_monitor import (
    get_database,
    get_status,
)

from logic_engine import (
    find_model_coords,
    get_compatibles_strict,
)

from ui_components import (
    draw_neon_section,
    draw_technical_coords,
    draw_welcome_section,
)

from core.logger import get_logger

log = get_logger("server")


# ==========================================================
# Result Status
# ==========================================================

class ResultStatus(str, Enum):

    SUCCESS = "success"

    PLAN_2_PENDING = "plan_2_pending"

    PLAN_2_MATCH = "plan_2_match"

    PLAN_3_REQUIRED = "plan_3_required"

    ERROR = "error"

    EMPTY = "empty"


# ==========================================================
# LRU Cache
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

    def __len__(self):

        return len(self.cache)


# ==========================================================
# Server
# ==========================================================

def server(input, output, session):

    # ---------------------------
    # Reactive State
    # ---------------------------

    database_data = reactive.value({})

    models_index = reactive.value([])

    autocomplete_index = reactive.value(None)

    fast_index_cache = reactive.value(None)

    custom_panels = reactive.value([])

    custom_sensors = reactive.value([])

    current_phone = reactive.value("")

    last_processed_phone = reactive.value("")

    suggestions_list = reactive.value([])

    show_curtain = reactive.value(False)

    plan_results = reactive.value(None)

    last_monitor_status = reactive.value("OFFLINE")

    last_sync_timestamp = reactive.value("")

    last_sync_time = reactive.value(0.0)

    last_db_hash = reactive.value("")

    workflow_cache = LRUCache(150)

    SEARCH_DELAY = 0.30

    SYNC_INTERVAL = 5.0
    # ==========================================================
    # Helpers
    # ==========================================================

    def normalize_text(text: str) -> str:
        """Normalize phone name for search/cache."""
        if not text:
            return ""

        text = str(text).casefold()

        text = re.sub(
            r"[^\w\s\u0621-\u064a+\-.]",
            "",
            text,
        )

        return re.sub(r"\s+", " ", text).strip()


    def safe_float(value) -> Optional[float]:
        """Convert user input to float safely."""

        try:
            return float(
                str(value)
                .replace(",", ".")
                .strip()
            )
        except Exception:
            return None


    def compute_db_hash(db: dict) -> str:
        """
        Compute a stable hash.
        Uses monitor timestamp when available.
        """

        try:

            status = get_status() or {}

            last_sync = status.get("last_sync")

            if last_sync:
                return hashlib.sha256(
                    str(last_sync).encode()
                ).hexdigest()

            models = []

            for panels in db.values():

                if not isinstance(panels, dict):
                    continue

                for sensors in panels.values():

                    if not isinstance(sensors, dict):
                        continue

                    for group in sensors.values():

                        if isinstance(group, dict):

                            models.extend(
                                group.get("models", [])
                            )

            models.sort()

            return hashlib.sha256(
                json.dumps(
                    models,
                    ensure_ascii=False
                ).encode()
            ).hexdigest()

        except Exception as e:

            log.error(f"Hash Error: {e}")

            return ""


    # ==========================================================
    # Async Messages
    # ==========================================================

    def _send_message(name: str, data: dict):

        try:

            loop = asyncio.get_running_loop()

            loop.create_task(
                session.send_custom_message(
                    name,
                    data,
                )
            )

        except RuntimeError:
            return

        except Exception as e:

            log.debug(
                f"send_custom_message: {e}"
            )


    def toggle_loading(show: bool):

        _send_message(
            "toggle_loading",
            {
                "show": bool(show)
            },
        )


    def open_drawer():

        _send_message(
            "toggle_drawer",
            {
                "action": "open"
            },
        )


    def close_drawer():

        _send_message(
            "toggle_drawer",
            {
                "action": "close"
            },
    )
    # ==========================================================
    # Workflow
    # ==========================================================

    def run_workflow_structured(
        phone: str,
        db: dict,
    ) -> Dict[str, Any]:

        start = time.time()

        try:

            phone = normalize_text(phone)

            cache_key = (
                f"{phone}:{last_db_hash()[:12]}"
            )

            cached = workflow_cache.get(cache_key)

            if cached is not None:

                log.debug(f"Cache hit: {phone}")

                return cached

            size, panel, sensor, real_name = (
                find_model_coords(
                    db,
                    phone,
                )
            )

            if real_name:

                compatibles = (
                    get_compatibles_strict(
                        db,
                        size,
                        panel,
                        sensor,
                        real_name,
                    )
                    or {}
                )

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

                    "phone": phone,

                    "message": (
                        f"الموديل ({phone}) غير موجود."
                    ),

                }

            workflow_cache.put(
                cache_key,
                result,
            )

            elapsed = (
                time.time() - start
            )

            log.info(
                f"Workflow {elapsed:.3f}s : {phone}"
            )

            return result

        except Exception as e:

            log.exception(e)

            return {

                "status": ResultStatus.ERROR,

                "message": str(e),

            }


    # ==========================================================
    # Database Sync
    # ==========================================================

    @reactive.effect
    def _sync_database():

        reactive.invalidate_later(
            SYNC_INTERVAL
        )

        now = time.time()

        if (
            now - last_sync_time()
            < SYNC_INTERVAL - 0.25
        ):
            return

        try:

            db = get_database()

            if (
                not db
                or
                not isinstance(db, dict)
            ):

                last_monitor_status.set(
                    "OFFLINE"
                )

                return

            status = (
                get_status()
                or {}
            )

            database_data.set(db)

            last_monitor_status.set(
                status.get(
                    "status",
                    "ONLINE",
                )
            )

            last_sync_timestamp.set(
                time.strftime(
                    "%H:%M:%S"
                )
            )

            db_hash = compute_db_hash(db)

            # لا تعيد بناء الفهارس إذا لم تتغير البيانات
            if db_hash == last_db_hash():

                log.debug(
                    "Database unchanged"
                )

                return

            last_db_hash.set(db_hash)

            build_start = time.time()

            flat_models = []

            panel_set = set()

            sensor_set = set()

            for panels in db.values():

                if not isinstance(
                    panels,
                    dict,
                ):
                    continue

                for panel_name, sensors in panels.items():

                    panel_set.add(
                        str(panel_name)
                    )

                    if not isinstance(
                        sensors,
                        dict,
                    ):
                        continue

                    for sensor_name, group in sensors.items():

                        sensor_set.add(
                            str(sensor_name)
                        )

                        if (
                            isinstance(group, dict)
                        ):

                            flat_models.extend(
                                group.get(
                                    "models",
                                    [],
                                )
                            )

            flat_models = sorted(
                set(flat_models)
            )

            models_index.set(
                flat_models
            )

            autocomplete_index.set(
                build_autocomplete_index(
                    flat_models
                )
            )

            fast_index_cache.set(
                build_fast_index(db)
            )

            custom_panels.set(
                sorted(panel_set)
            )

            custom_sensors.set(
                sorted(sensor_set)
            )

            workflow_cache.clear()

            log.info(

                f"Database synced "

                f"{len(flat_models)} models "

                f"in "

                f"{time.time()-build_start:.3f}s"

            )

        except Exception as e:

            log.exception(e)

        finally:

            last_sync_time.set(
                time.time()
        )
    # ==========================================================
    # Search + Autocomplete
    # ==========================================================

    @reactive.effect
    @reactive.event(input.search_query)
    def _handle_search():

        # Debounce
        reactive.invalidate_later(SEARCH_DELAY)

        query = normalize_text(input.search_query())

        current_phone.set(query)

        if not query:

            suggestions_list.set([])

            show_curtain.set(False)

            return

        trie = autocomplete_index()

        if trie is None:

            suggestions_list.set([])

            show_curtain.set(False)

            return

        try:

            matches = trie.search_prefix(query, 10)

        except Exception as e:

            log.error(f"Autocomplete error: {e}")

            matches = []

        if matches:

            suggestions_list.set(matches)

            show_curtain.set(True)

        else:

            suggestions_list.set([])

            show_curtain.set(False)


    # ==========================================================
    # Suggestions Curtain
    # ==========================================================

    @output
    @render.ui
    def suggestions_curtain():

        if not show_curtain():

            return None

        items = suggestions_list()

        if not items:

            return None

        rows = []

        for item in items:

            safe = json.dumps(
                item,
                ensure_ascii=False,
            ).replace("</", "<\\/")

            rows.append(

                ui.div(

                    item,

                    class_="suggestion-row",

                    onclick=f"""
Shiny.setInputValue(
'search_query',
{safe},
{{priority:'event'}}
);

Shiny.setInputValue(
'_hide_curtain_trigger',
Date.now(),
{{priority:'event'}}
);
""",

                )

            )

        return ui.div(

            *rows,

            class_="suggestions-curtain",

        )


    # ==========================================================
    # Hide Curtain
    # ==========================================================

    @reactive.effect
    @reactive.event(input._hide_curtain_trigger)
    def _hide_curtain():

        show_curtain.set(False)


    # ==========================================================
    # Execute Search
    # ==========================================================

    @reactive.effect
    @reactive.event(input.search_query)
    def _execute_search():

        phone = normalize_text(
            current_phone()
        )

        if not phone:

            plan_results.set(None)

            last_processed_phone.set("")

            toggle_loading(False)

            return

        # منع تنفيذ نفس البحث مرتين
        if phone == last_processed_phone():

            return

        last_processed_phone.set(phone)

        db = database_data()

        if not db:

            plan_results.set({

                "status": ResultStatus.ERROR,

                "message": "تعذر تحميل قاعدة البيانات.",

            })

            return

        toggle_loading(True)

        try:

            result = run_workflow_structured(

                phone,

                db,

            )

            plan_results.set(result)

        except Exception as e:

            log.exception(e)

            plan_results.set({

                "status": ResultStatus.ERROR,

                "message": str(e),

            })

        finally:

            toggle_loading(False)
    # ==========================================================
    # Results View
    # ==========================================================

    @output
    @render.ui
    def results_workflow_view():

        res = plan_results()

        if not res:
            return None

        status = res.get("status")

        children = []

        # ======================================================
        # SUCCESS
        # ======================================================

        if status == ResultStatus.SUCCESS:

            coords = res.get("coords", {})

            compatibles = res.get("compatibles", {})

            children.append(

                draw_technical_coords(

                    coords.get("size"),

                    coords.get("panel"),

                    coords.get("sensor"),

                    coords.get("real_name"),

                )

            )

            sections = [

                (

                    "مطابقة تماماً",

                    compatibles.get("exact") or [],

                    "#2ecc71",

                    "exact",

                ),

                (

                    "أكبر بقليل ±0.03",

                    compatibles.get("plus") or [],

                    "#3498db",

                    "plus",

                ),

                (

                    "أصغر قليلاً ±0.03",

                    compatibles.get("minus") or [],

                    "#e67e22",

                    "minus",

                ),

            ]

            for title, data, color, key in sections:

                section = draw_neon_section(

                    title,

                    data,

                    color,

                    "",

                    key,

                )

                if section:

                    children.append(section)

        # ======================================================
        # PLAN 2
        # ======================================================

        elif status == ResultStatus.PLAN_2_PENDING:

            children.append(

                ui.div(

                    ui.h3(

                        "📋 إدخال المواصفات يدوياً",

                        style="""
text-align:center;
color:var(--primary-color);
margin-bottom:15px;
""",

                    ),

                    ui.p(

                        res.get("message", ""),

                        style="""
text-align:center;
opacity:.85;
margin-bottom:18px;
""",

                    ),

                    ui.input_text(

                        "p2_size",

                        "المقاس",

                        placeholder="مثال: 6.67",

                    ),

                    ui.input_selectize(

                        "p2_panel",

                        "نوع الشاشة",

                        choices=custom_panels(),

                    ),

                    ui.input_selectize(

                        "p2_sensor",

                        "المستشعر",

                        choices=custom_sensors(),

                    ),

                    ui.tags.button(

                        "🔍 بحث",

                        class_="btn-neon",

                        style="""
width:100%;
margin-top:15px;
""",

                        onclick="""
Shiny.setInputValue(
'exec_plan2',
Date.now(),
{priority:'event'}
)
""",

                    ),

                    class_="glass-card fade-in",

                )

            )

        # ======================================================
        # PLAN2 MATCH
        # ======================================================

        elif status == ResultStatus.PLAN_2_MATCH:

            info = res.get("data", {})

            models = info.get("models", [])

            children.append(

                ui.div(

                    ui.h3(

                        "✅ تم العثور على مجموعة",

                        style="""
color:#2ecc71;
text-align:center;
""",

                    ),

                    ui.p(

                        res.get("message", ""),

                        style="text-align:center;",

                    ),

                    ui.hr(),

                    ui.h5(

                        "الموديلات الموجودة",

                        style="""
text-align:center;
margin-bottom:10px;
""",

                    ),

                    ui.div(

                        *[

                            ui.div(

                                m,

                                class_="compat-item",

                            )

                            for m in models

                        ]

                        if models

                        else [

                            ui.div(

                                "لا توجد موديلات.",

                            )

                        ],

                    ),

                    class_="glass-card fade-in",

                )

            )

        # ======================================================
        # PLAN3
        # ======================================================

        elif status == ResultStatus.PLAN_3_REQUIRED:

            children.append(

                ui.div(

                    ui.h3(

                        "🚨 لم يتم العثور على مجموعة",

                        style="""
text-align:center;
color:#ff5252;
""",

                    ),

                    ui.p(

                        "ينصح بإنشاء مجموعة جديدة.",

                        style="text-align:center;",

                    ),

                    class_="glass-card fade-in",

                )

            )

        # ======================================================
        # ERROR
        # ======================================================

        elif status == ResultStatus.ERROR:

            children.append(

                ui.div(

                    ui.h3(

                        "⚠️ حدث خطأ",

                        style="""
text-align:center;
color:#ff5252;
""",

                    ),

                    ui.p(

                        res.get("message", ""),

                        style="text-align:center;",

                    ),

                    class_="glass-card fade-in",

                )

            )

        return ui.div(

            *children,

            class_="fade-in",

            )
    # ==========================================================
    # Plan 2 Execution
    # ==========================================================

    @reactive.effect
    @reactive.event(input.exec_plan2)
    def _exec_plan2():

        toggle_loading(True)

        try:

            size = safe_float(input.p2_size())

            panel = (input.p2_panel() or "").strip()

            sensor = (input.p2_sensor() or "").strip()

            # -----------------------------------
            # Validation
            # -----------------------------------

            if size is None:

                plan_results.set({

                    "status": ResultStatus.ERROR,

                    "message": "يرجى إدخال المقاس بصورة صحيحة.",

                })

                return

            if not panel:

                plan_results.set({

                    "status": ResultStatus.ERROR,

                    "message": "يرجى اختيار نوع الشاشة.",

                })

                return

            if not sensor:

                plan_results.set({

                    "status": ResultStatus.ERROR,

                    "message": "يرجى اختيار نوع المستشعر.",

                })

                return

            # -----------------------------------
            # Fast Index
            # -----------------------------------

            idx = fast_index_cache()

            if idx is None:

                idx = build_fast_index(database_data())

                fast_index_cache.set(idx)

            # -----------------------------------
            # Search
            # -----------------------------------

            result = process_plan(

                size,

                panel,

                sensor,

                database_data(),

                idx,

            )

            if result:

                models = result.get("models", [])

                plan_results.set({

                    "status": ResultStatus.PLAN_2_MATCH,

                    "message":

                        f"المقاس : {result.get('size')}"

                        f" | الشاشة : {result.get('panel')}"

                        f" | المستشعر : {result.get('sensor')}",

                    "data": {

                        **result,

                        "models": models,

                    },

                })

                log.info(

                    f"Plan2 Match "

                    f"{len(models)} models"

                )

            else:

                plan_results.set({

                    "status": ResultStatus.PLAN_3_REQUIRED,

                    "message":

                        "لم يتم العثور على مجموعة مطابقة.",

                })

                log.info(

                    "Plan2 -> Plan3"

                )

        except Exception as e:

            log.exception(e)

            plan_results.set({

                "status": ResultStatus.ERROR,

                "message": str(e),

            })

        finally:

            toggle_loading(False)
    # ==========================================================
    # Settings Drawer
    # ==========================================================

    @reactive.effect
    @reactive.event(input.btn_settings)
    def _open_drawer():

        open_drawer()


    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    def _close_drawer():

        close_drawer()


    # ==========================================================
    # Dashboard Cards
    # ==========================================================

    @output
    @render.ui
    def database_status_area():

        return ui.div(

            ui.div(

                "📊 عدد الموديلات",

                class_="metric-title",

            ),

            ui.div(

                str(len(models_index())),

                class_="metric-value",

                style="color:var(--primary-color);",

            ),

            ui.div(

                f"آخر تحديث : {last_sync_timestamp()}",

                style="""
font-size:11px;
opacity:.65;
margin-top:6px;
""",

            ),

            class_="metric-box",

        )


    @output
    @render.ui
    def monitor_area():

        state = last_monitor_status()

        colors = {

            "ONLINE": "#2ecc71",

            "FALLBACK": "#f39c12",

            "OFFLINE": "#ff5252",

        }

        color = colors.get(

            state,

            "#999",

        )

        return ui.div(

            ui.div(

                "🛰️ حالة المراقب",

                class_="metric-title",

            ),

            ui.div(

                state,

                class_="metric-value",

                style=f"color:{color};",

            ),

            class_="metric-box",

        )


    @output
    @render.ui
    def notifications_area():

        status = get_status() or {}

        return ui.div(

            ui.div(

                "🔔 مصدر البيانات",

                class_="metric-title",

            ),

            ui.div(

                status.get(

                    "source",

                    "Unknown",

                ),

                class_="metric-value",

                style="color:var(--foundation-color);",

            ),

            class_="metric-box",

        )


    # ==========================================================
    # Welcome Area
    # ==========================================================

    @output
    @render.ui
    def welcome_area():

        if plan_results() is not None:

            return None

        return draw_welcome_section()


    # ==========================================================
    # Session Information
    # ==========================================================

    @output
    @render.text
    def session_info():

        return (

            f"Models: {len(models_index())} | "

            f"Cache: {len(workflow_cache)} | "

            f"Status: {last_monitor_status()}"

        )
    # =========================
    # 10. تنظيف الموارد
    # =========================
    def _cleanup():
        """تنظيف الموارد عند انتهاء الجلسة"""

        try:
            workflow_cache.clear()
        except Exception:
            pass

        try:
            suggestions_list.set([])
            show_curtain.set(False)
            plan_results.set(None)
        except Exception:
            pass

        log.info("Session ended. Resources cleaned successfully.")

    session.on_ended(_cleanup)

    # =========================
    # 11. Startup Log
    # =========================
    log.info("ZEGAAR GLASS MANAGER Server v4.2 started successfully")
