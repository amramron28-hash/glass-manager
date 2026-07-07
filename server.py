from __future__ import annotations
from shiny import reactive, render, ui
import logging
import asyncio
import json
from enum import Enum
import services as svs
from logic_engine import run_system_workflows, run_intelligent_inspector
from silent_monitor import get_database, refresh as monitor_refresh, get_db_hash
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, draw_technical_coords, 
    draw_neon_section, draw_welcome_section, draw_database_status,
    draw_monitor_component, draw_notifications, draw_silent_inspector,
    draw_system_info, draw_drawer_js_handler
)
from collections import OrderedDict

def local_normalize(text: str) -> str:
    return str(text or "").lower().strip()

class Status(str, Enum):
    SUCCESS = "success"
    PLAN_2 = "plan_2"
    PLAN_3 = "plan_3"
    ERROR = "error"

class LRUCache:
    def __init__(self, size=150): 
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
        if len(self.cache) > self.size: self.cache.popitem(last=False)
    def clear(self): self.cache.clear()

logger = logging.getLogger("ui_debug")

def server(input, output, session):
    modal_state = reactive.value(None)
    suggestions_state = reactive.value(False)
    workflow_state = reactive.value(None)
    autocomplete_index = reactive.value(None)
    search_cache = LRUCache()
    db_total_models = reactive.value(0)

    @session.on_ended
    def _cleanup():
        search_cache.clear()

    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _close_modal(): modal_state.set(None)

    @reactive.effect
    async def _run_inspector():
        if not input.btn_run_inspector(): return
        try:
            def run_sync(): return run_intelligent_inspector()
            await asyncio.to_thread(run_sync)
            search_cache.clear()
        except Exception as e: logger.exception("Inspector Error")

    @reactive.effect
    def _init():
        try:
            autocomplete_index.set(svs.build_autocomplete_index(svs.load_models_index()))
            db = get_database() or {}
            total = sum(len(s.get("models", [])) for p in db.values() for s in p.values() for s2 in (s.values() if isinstance(s, dict) else []))
            db_total_models.set(total)
        except Exception as e: logger.error(f"Init error: {e}")

    @reactive.effect
    @reactive.event(input.search_query)
    async def _run_search():
        modal_state.set(None) 
        q = local_normalize(input.search_query())
        if len(q) < 2:
            suggestions_state.set(False)
            return
        suggestions_state.set(True)
        await asyncio.sleep(0.3)
        if q != local_normalize(input.search_query()): return
        try: 
            db = get_database() or {}
            res = run_system_workflows(q, db)
            workflow_state.set(res)
            if res.get("status") == Status.PLAN_2.value: modal_state.set("plan2")
            elif res.get("status") == Status.PLAN_3.value: modal_state.set("plan3")
            suggestions_state.set(False)
        except Exception as e: logger.exception("Search Error")

    # المخرجات (ملاحظة: نستخدم @render.ui فقط بدون @output)
    @render.ui
    def system_info_area(): return draw_system_info()

    @render.ui
    def database_status_area(): return draw_database_status(db_total_models())

    @render.ui
    def monitor_area(): return draw_monitor_component({"status": "ONLINE" if get_database() else "OFFLINE"})

    @render.ui
    def notifications_area(): return draw_notifications({"source": "Supabase"})

    @render.ui
    def silent_inspector_area(): return draw_silent_inspector()

    @render.ui
    def drawer_js_handler(): return draw_drawer_js_handler()

    @render.ui
    def results_workflow_view():
        res = workflow_state()
        if not res or res.get("status") != Status.SUCCESS.value: return None
        c, comp = res.get("coords", {}), res.get("compatibles", {})
        return ui.TagList(
            draw_technical_coords(c.get("size"), c.get("panel"), c.get("sensor"), c.get("real_name")),
            draw_neon_section("مطابقة تماماً", comp.get("exact"), "#2ecc71", "✅", "exact"),
            draw_neon_section("إضافات", comp.get("plus"), "#3498db", "➕", "plus"),
            draw_neon_section("نواقص", comp.get("minus"), "#e67e22", "➖", "minus")
        )

    @render.ui
    def dynamic_modal_container():
        m, res = modal_state(), workflow_state()
        if not m or not res: return None
        if m == "plan2": return draw_plan_2_modal(res.get("phone", ""), res.get("panels"), res.get("sensors"))
        if m == "plan3": return draw_plan_3_modal(res.get("phone", ""))
        return None

    @render.ui
    def suggestions_curtain():
        idx, q = autocomplete_index(), local_normalize(input.search_query())
        if not suggestions_state() or not idx or len(q) < 2: return None
        results = idx.search_prefix(q, 5)
        return ui.div(*[ui.div(r, class_="suggestion-row", onclick=f"Shiny.setInputValue('search_query', {json.dumps(r)}, {{priority:'event'}});") for r in results], class_="suggestions-curtain")

    @render.ui
    def welcome_area():
        return draw_welcome_section() if workflow_state() is None else None
