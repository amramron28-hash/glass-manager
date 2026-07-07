from __future__ import annotations
from shiny import reactive, render, ui
import logging
import asyncio
import json
from enum import Enum
import services as svs
from logic_engine import run_system_workflows
from silent_monitor import get_database, refresh as monitor_refresh, get_db_hash
from ui_components import (
    draw_plan_2_modal, draw_plan_3_modal, 
    draw_settings_modal, draw_technical_coords, draw_neon_section, draw_welcome_section
)
from collections import OrderedDict

# دالة محلية لتنظيف النصوص (تجاوز أي نقص في services.py)
def local_normalize(text: str) -> str:
    return str(text or "").lower().strip()

class Status(str, Enum):
    SUCCESS = "success"
    PLAN_2 = "plan_2"
    PLAN_3 = "plan_3"
    ERROR = "error"

class LRUCache:
    def __init__(self, size=150): self.cache = OrderedDict(); self.size = size
    def get(self, key):
        if key in self.cache: self.cache.move_to_end(key); return self.cache[key]
        return None
    def put(self, key, value):
        self.cache[key] = value; self.cache.move_to_end(key)
        if len(self.cache) > self.size: self.cache.popitem(last=False)
    def clear(self): self.cache.clear()

logger = logging.getLogger("ui_debug")

def server(input, output, session):
    modal_state = reactive.value(None)
    suggestions_state = reactive.value(False)
    workflow_state = reactive.value(None)
    autocomplete_index = reactive.value(None)
    search_cache = LRUCache()

    @session.on_ended
    def _cleanup():
        search_cache.clear()
        workflow_state.set(None)
        modal_state.set(None)

    # --- معالجات التفاعل ---
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _open_settings(): modal_state.set("settings")

    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _close_modal(): modal_state.set(None)

    @reactive.effect
    @reactive.event(input._hide_curtain_trigger)
    def _hide(): suggestions_state.set(False)

    # --- التحديث التلقائي ---
    @reactive.effect
    def _auto_refresh():
        reactive.invalidate_later(60)
        try:
            monitor_refresh()
            autocomplete_index.set(svs.build_autocomplete_index(svs.load_models_index()))
        except Exception: pass

    @reactive.effect
    def _init():
        autocomplete_index.set(svs.build_autocomplete_index(svs.load_models_index()))

    # --- منطق البحث الرئيسي ---
    @reactive.effect
    @reactive.event(input.search_query)
    async def _run_search():
        modal_state.set(None) 
        q = local_normalize(input.search_query())
        
        if len(q) >= 2:
            suggestions_state.set(True)
        else:
            suggestions_state.set(False); return
        
        await asyncio.sleep(0.3)
        if q != local_normalize(input.search_query()): return

        try: cache_key = f"{q}_{get_db_hash()}"
        except: cache_key = f"{q}_default"
        
        cached = search_cache.get(cache_key)
        if cached: workflow_state.set(cached); return

        session.send_custom_message("toggle_loading", {"show": True})
        try:
            db = get_database() or {}
            if not db: workflow_state.set({"status": Status.ERROR.value, "message": "DB Error"}); return
            
            res = run_system_workflows(q, db)
            workflow_state.set(res)
            search_cache.put(cache_key, res)
            
            st = res.get("status")
            if st == Status.PLAN_2.value: modal_state.set("plan2")
            elif st == Status.PLAN_3.value: modal_state.set("plan3")
            
            suggestions_state.set(False)
        except Exception as e:
            logger.exception("Search Error")
        finally:
            session.send_custom_message("toggle_loading", {"show": False})

    # --- المخرجات الديناميكية للواجهة ---
    @output
    @render.ui
    def results_workflow_view():
        res = workflow_state()
        if not res or res.get("status") != Status.SUCCESS.value: return None
        c = res.get("coords", {})
        comp = res.get("compatibles", {})
        return ui.TagList(
            draw_technical_coords(c.get("size"), c.get("panel"), c.get("sensor"), c.get("real_name")),
            draw_neon_section("مطابقة تماماً", comp.get("exact"), "#2ecc71", "✅", "exact"),
            draw_neon_section("إضافات", comp.get("plus"), "#3498db", "➕", "plus"),
            draw_neon_section("نواقص", comp.get("minus"), "#e67e22", "➖", "minus")
        )

    @output
    @render.ui
    def dynamic_modal_container():
        m = modal_state()
        res = workflow_state()
        if not m: return None
        if m == "settings": return draw_settings_modal()
        if res:
            if m == "plan2": return draw_plan_2_modal(res.get("phone"), res.get("panels"), res.get("sensors"))
            if m == "plan3": return draw_plan_3_modal(res.get("phone"))
        return None

    @output
    @render.ui
    def suggestions_curtain():
        idx = autocomplete_index()
        q = local_normalize(input.search_query())
        if not suggestions_state() or not idx or len(q) < 2: return None
        results = idx.search_prefix(q, 5)
        if not results: return None
        return ui.div(
            *[ui.div(r, class_="suggestion-row", onclick=f"Shiny.setInputValue('search_query', {json.dumps(r)}, {{priority:'event'}}); Shiny.setInputValue('_hide_curtain_trigger', true, {{priority:'event'}});") 
              for r in results],
            class_="suggestions-curtain"
        )
    
    @output
    @render.ui
    def welcome_area():
        if workflow_state() is None: return draw_welcome_section()
        return None
