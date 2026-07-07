from __future__ import annotations
from shiny import reactive, render, ui
import logging
import asyncio
import json
from enum import Enum
import services as svs
from logic_engine import run_system_workflows, run_intelligent_inspector, fetch_db_structure
from silent_monitor import get_database, refresh as monitor_refresh, get_db_hash
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
    draw_system_info
)
from collections import OrderedDict

# دالة محلية لتنظيف النصوص
def local_normalize(text: str) -> str:
    return str(text or "").lower().strip()

class Status(str, Enum):
    SUCCESS = "success"
    PLAN_2 = "plan_2"
    PLAN2_SUCCESS = "plan2_success"
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
        if len(self.cache) > self.size: 
            self.cache.popitem(last=False)
    
    def clear(self): 
        self.cache.clear()

logger = logging.getLogger("ui_debug")

def server(input, output, session):
    modal_state = reactive.value(None)
    suggestions_state = reactive.value(False)
    workflow_state = reactive.value(None)
    autocomplete_index = reactive.value(None)
    search_cache = LRUCache()
    
    # ✅ جديد: حالة المراقب الصامت
    inspector_status = reactive.value({"status": "جاهز", "message": ""})
    db_total_models = reactive.value(0)

    @session.on_ended
    def _cleanup():
        search_cache.clear()
        workflow_state.set(None)
        modal_state.set(None)

    # ============================================
    # معالجات التفاعل (Event Handlers)
    # ============================================
    
    @reactive.effect
    @reactive.event(input.btn_close_modal)
    def _close_modal(): 
        modal_state.set(None)

    @reactive.effect
    @reactive.event(input._hide_curtain_trigger)
    def _hide(): 
        suggestions_state.set(False)

    # ✅ جديد: معالج زر المراقب الصامت
    @reactive.effect
    @reactive.event(input.btn_run_inspector)
    async def _run_inspector():
        try:
            inspector_status.set({"status": "جاري التشغيل...", "message": ""})
            
            # تشغيل المراقب الصامت في thread منفصل لتجنب حجب الواجهة
            def run_sync():
                return run_intelligent_inspector()
            
            cleaned_data, changes_made = await asyncio.to_thread(run_sync)
            
            if changes_made:
                inspector_status.set({
                    "status": "✅ تم التنظيف", 
                    "message": "تم إزالة التكرارات بنجاح"
                })
                # تحديث عداد الموديلات بعد التنظيف
                total = sum(
                    len(s.get("models", []))
                    for p in cleaned_data.values()
                    for s in p.values()
                    for s2 in (s.values() if isinstance(s, dict) else [])
                )
                db_total_models.set(total)
                
                # مسح الكاش لأن البيانات تغيرت
                search_cache.clear()
            else:
                inspector_status.set({
                    "status": "✨ نظيف", 
                    "message": "قاعدة البيانات مرتبة بالفعل"
                })
                
        except Exception as e:
            logger.exception("Inspector Error")
            inspector_status.set({"status": "❌ خطأ", "message": str(e)})

    # ============================================
    # التحديث التلقائي
    # ============================================
    
    @reactive.effect
    def _auto_refresh():
        reactive.invalidate_later(60)
        try:
            monitor_refresh()
            autocomplete_index.set(svs.build_autocomplete_index(svs.load_models_index()))
        except Exception: 
            pass

    @reactive.effect
    def _init():
        try:
            autocomplete_index.set(svs.build_autocomplete_index(svs.load_models_index()))
            # حساب العدد الإجمالي للموديلات عند بدء التشغيل
            db = get_database() or {}
            total = sum(
                len(sensor_data.get("models", []))
                for panels in db.values()
                for sensors in panels.values()
                for sensor_data in (sensors.values() if isinstance(sensors, dict) else [])
            )
            db_total_models.set(total)
        except Exception as e:
            logger.error(f"Init error: {e}")

    # ============================================
    # منطق البحث الرئيسي
    # ============================================
    
    @reactive.effect
    @reactive.event(input.search_query)
    async def _run_search():
        modal_state.set(None) 
        q = local_normalize(input.search_query())
        
        if len(q) >= 2:
            suggestions_state.set(True)
        else:
            suggestions_state.set(False)
            return
        
        await asyncio.sleep(0.3)
        if q != local_normalize(input.search_query()): 
            return

        try: 
            cache_key = f"{q}_{get_db_hash()}"
        except: 
            cache_key = f"{q}_default"
        
        cached = search_cache.get(cache_key)
        if cached: 
            workflow_state.set(cached)
            return

        session.send_custom_message("toggle_loading", {"show": True})
        try:
            db = get_database() or {}
            if not db: 
                workflow_state.set({"status": Status.ERROR.value, "message": "DB Error"})
                return
            
            # ✅ ملاحظة: run_system_workflows في النسخة الجديدة لا تحتاج db كمعامل
            # لكنها تقبله للتوافق مع الإصدارات القديمة
            res = run_system_workflows(q, db)
            workflow_state.set(res)
            search_cache.put(cache_key, res)
            
            st = res.get("status")
            if st == Status.PLAN_2.value: 
                modal_state.set("plan2")
            elif st == Status.PLAN_3.value: 
                modal_state.set("plan3")
            
            suggestions_state.set(False)
        except Exception as e:
            logger.exception("Search Error")
        finally:
            session.send_custom_message("toggle_loading", {"show": False})

    # ============================================
    # ✅ Outputs جديدة للـ Drawer (الإعدادات)
    # ============================================
    
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
        try:
            status = {"status": "ONLINE" if get_database() else "OFFLINE"}
        except:
            status = {"status": "UNKNOWN"}
        return draw_monitor_component(status)

    @output
    @render.ui
    def notifications_area():
        return draw_notifications({"source": "Supabase Cloud"})

    @output
    @render.ui
    def silent_inspector_area():
        return draw_silent_inspector()

    # ============================================
    # المخرجات الديناميكية للواجهة
    # ============================================
    
    @output
    @render.ui
    def results_workflow_view():
        res = workflow_state()
        if not res or res.get("status") not in [Status.SUCCESS.value, Status.PLAN2_SUCCESS.value]: 
            return None
        
        c = res.get("coords", {})
        comp = res.get("compatibles", {})
        
        return ui.TagList(
            draw_technical_coords(
                c.get("size"), 
                c.get("panel"), 
                c.get("sensor"), 
                c.get("real_name")
            ),
            draw_neon_section("مطابقة تماماً", comp.get("exact"), "#2ecc71", "✅", "exact"),
            draw_neon_section("إضافات", comp.get("plus"), "#3498db", "➕", "plus"),
            draw_neon_section("نواقص", comp.get("minus"), "#e67e22", "➖", "minus"),
            # ✅ جديد: إضافة قسم التحذيرات إذا وجد
            draw_neon_section("تحذيرات", comp.get("warn"), "#f39c12", "⚠️", "warn") if comp.get("warn") else None
        )

    @output
    @render.ui
    def dynamic_modal_container():
        m = modal_state()
        res = workflow_state()
        if not m: 
            return None
        
        # ✅ حذفنا draw_settings_modal لأن الإعدادات الآن في الـ Drawer
        if res:
            if m == "plan2": 
                return draw_plan_2_modal(
                    res.get("phone") or res.get("input_data", {}).get("phone", ""), 
                    res.get("panels"), 
                    res.get("sensors")
                )
            if m == "plan3": 
                return draw_plan_3_modal(
                    res.get("phone") or res.get("input_data", {}).get("phone", "")
                )
        return None

    @output
    @render.ui
    def suggestions_curtain():
        idx = autocomplete_index()
        q = local_normalize(input.search_query())
        if not suggestions_state() or not idx or len(q) < 2: 
            return None
        
        results = idx.search_prefix(q, 5)
        if not results: 
            return None
        
        return ui.div(
            *[
                ui.div(
                    r, 
                    class_="suggestion-row", 
                    onclick=f"Shiny.setInputValue('search_query', {json.dumps(r)}, {{priority:'event'}}); Shiny.setInputValue('_hide_curtain_trigger', true, {{priority:'event'}});"
                ) 
                for r in results
            ],
            class_="suggestions-curtain"
        )
    
    @output
    @render.ui
    def welcome_area():
        if workflow_state() is None: 
            return draw_welcome_section()
        return None
