from __future__ import annotations

import asyncio
import json
import logging
from collections import OrderedDict
from enum import Enum

from shiny import reactive, render, ui

import services as svs

from logic_engine import (
    run_system_workflows,
    run_intelligent_inspector,
)

from silent_monitor import (
    get_database,
    refresh as monitor_refresh,
    get_db_hash,
)

from ui_components import (
    draw_plan_2_modal,
    draw_plan_3_modal,
    draw_technical_coords,
    draw_neon_section,
    draw_welcome_section,
    draw_database_status,
    draw_monitor_component,
    draw_notifications,
    draw_silent_inspector,
    draw_system_info,
)

logger = logging.getLogger("glass_manager")


# ==========================================================
# Utilities
# ==========================================================

def local_normalize(text: str) -> str:
    return str(text or "").strip().lower()


class Status(str, Enum):
    SUCCESS = "success"
    PLAN_2 = "plan_2"
    PLAN2_SUCCESS = "plan2_success"
    PLAN_3 = "plan_3"
    ERROR = "error"


class LRUCache:

    def __init__(self, size: int = 150):
        self.cache = OrderedDict()
        self.size = size

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)

        while len(self.cache) > self.size:
            self.cache.popitem(last=False)

    def clear(self):
        self.cache.clear()


# ==========================================================
# Server
# ==========================================================

def server(input, output, session):

    workflow_state = reactive.value(None)

    modal_state = reactive.value(None)

    suggestions_state = reactive.value(False)

    autocomplete_index = reactive.value(None)

    db_hash = reactive.value("")

    db_total_models = reactive.value(0)

    inspector_status = reactive.value(
        {
            "status": "READY",
            "message": ""
        }
    )

    search_cache = LRUCache()

    # ------------------------------------------------------
    # تنظيف الجلسة
    # ------------------------------------------------------

    @session.on_ended
    def _cleanup():

        search_cache.clear()

        workflow_state.set(None)

        modal_state.set(None)

        suggestions_state.set(False)

    # ------------------------------------------------------
    # تحميل البيانات لأول مرة
    # ------------------------------------------------------

    @reactive.effect
    def _initialize():

        try:

            db = get_database() or {}

            autocomplete_index.set(
                svs.build_autocomplete_index(
                    svs.load_models_index()
                )
            )

            db_hash.set(get_db_hash())

            total = 0

            for panels in db.values():

                if not isinstance(panels, dict):
                    continue

                for sensors in panels.values():

                    if not isinstance(sensors, dict):
                        continue

                    for sensor_data in sensors.values():

                        if isinstance(sensor_data, dict):
                            total += len(sensor_data.get("models", []))

            db_total_models.set(total)

        except Exception:
            logger.exception("Initialization Error")
    # ------------------------------------------------------
    # تحديث قاعدة البيانات كل دقيقة
    # ------------------------------------------------------

    @reactive.effect
    def _auto_refresh():

        reactive.invalidate_later(60)

        try:

            new_hash = get_db_hash()

            if new_hash != db_hash():

                monitor_refresh()

                autocomplete_index.set(
                    svs.build_autocomplete_index(
                        svs.load_models_index()
                    )
                )

                db_hash.set(new_hash)

                search_cache.clear()

        except Exception:
            logger.exception("Auto Refresh Error")

    # ------------------------------------------------------
    # تشغيل المراقب الصامت
    # ------------------------------------------------------

    @reactive.effect
    @reactive.event(input.btn_run_inspector)
    async def _run_inspector():

        inspector_status.set(
            {
                "status": "RUNNING",
                "message": "Cleaning..."
            }
        )

        try:

            result = await asyncio.to_thread(
                run_intelligent_inspector
            )

            if isinstance(result, tuple):

                cleaned_db, changed = result

            else:

                cleaned_db = result
                changed = False

            if changed:

                search_cache.clear()

                inspector_status.set(
                    {
                        "status": "SUCCESS",
                        "message": "Database cleaned"
                    }
                )

            else:

                inspector_status.set(
                    {
                        "status": "READY",
                        "message": "Database already clean"
                    }
                )

        except Exception:

            logger.exception("Inspector Error")

            inspector_status.set(
                {
                    "status": "ERROR",
                    "message": "Inspector failed"
                }
            )

    # ------------------------------------------------------
    # البحث الذكي
    # ------------------------------------------------------

    @reactive.effect
    @reactive.event(input.search_query)
    async def _run_search():

        modal_state.set(None)

        query = local_normalize(input.search_query())

        if len(query) < 2:

            workflow_state.set(None)

            suggestions_state.set(False)

            return

        suggestions_state.set(True)

        await asyncio.sleep(0.30)

        if query != local_normalize(input.search_query()):
            return

        cache_key = f"{query}_{db_hash()}"

        cached = search_cache.get(cache_key)

        if cached is not None:

            workflow_state.set(cached)

            suggestions_state.set(False)

            return

        try:

            db = get_database() or {}

            result = run_system_workflows(query, db)

            workflow_state.set(result)

            search_cache.put(cache_key, result)

            status = result.get("status")

            if status == Status.PLAN_2.value:

                modal_state.set("plan2")

            elif status == Status.PLAN_3.value:

                modal_state.set("plan3")

            else:

                modal_state.set(None)

        except Exception:

            logger.exception("Search Error")

        finally:

            suggestions_state.set(False)

    # ------------------------------------------------------
    # إغلاق المودال
    # ------------------------------------------------------

    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _close_modal():

        modal_state.set(None)
    # ======================================================
    # Outputs
    # ======================================================

    @output
    @render.ui
    def system_info_area():
        return draw_system_info()

    @output
    @render.ui
    def database_status_area():
        return draw_database_status(db_total_models())

    @output
    @render.ui
    def monitor_area():
        return draw_monitor_component(inspector_status())

    @output
    @render.ui
    def notifications_area():
        return draw_notifications(
            {
                "status": "ONLINE"
            }
        )

    @output
    @render.ui
    def silent_inspector_area():
        return draw_silent_inspector()

    # ======================================================
    # شاشة الترحيب
    # ======================================================

    @output
    @render.ui
    def welcome_area():

        if workflow_state() is None:

            return draw_welcome_section()

        return None

    # ======================================================
    # نتائج البحث
    # ======================================================

    @output
    @render.ui
    def results_workflow_view():

        result = workflow_state()

        if result is None:
            return None

        if result.get("status") != Status.SUCCESS.value:
            return None

        coords = result.get("coords", {})
        compatibles = result.get("compatibles", {})

        return ui.TagList(

            draw_technical_coords(
                coords.get("size"),
                coords.get("panel"),
                coords.get("sensor"),
                coords.get("real_name")
            ),

            draw_neon_section(
                "مطابقة تماماً",
                compatibles.get("exact", []),
                "#2ecc71",
                "✅",
                "exact"
            ),

            draw_neon_section(
                "أكبر بقليل",
                compatibles.get("plus", []),
                "#3498db",
                "➕",
                "plus"
            ),

            draw_neon_section(
                "أصغر بقليل",
                compatibles.get("minus", []),
                "#e67e22",
                "➖",
                "minus"
            ),

            draw_neon_section(
                "تحذيرات",
                compatibles.get("warn", []),
                "#f39c12",
                "⚠️",
                "warn"
            ) if compatibles.get("warn") else None

        )

    # ======================================================
    # Modals
    # =================================================   
