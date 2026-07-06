# server.py
"""
ZEGAAR GLASS MANAGER - Server Module (Production Ready v4.0)
النسخة النهائية المثالية - 10/10
"""
from __future__ import annotations

import json
import time
import re
import hashlib
from enum import Enum
from typing import Dict, Optional, Any
from collections import OrderedDict

from shiny import reactive, render, ui
from services import build_autocomplete_index, build_fast_index, process_plan
from silent_monitor import get_database, get_status
from logic_engine import find_model_coords, get_compatibles_strict
from ui_components import draw_technical_coords, draw_neon_section, draw_welcome_section
from core.logger import get_logger

log = get_logger("server")


# =========================
# Enums لحالات النتائج (محسّن باستخدام Enum حقيقي)
# =========================
class ResultStatus(str, Enum):
    """حالات نتائج Workflow - يمنع الأخطاء الإملائية"""
    SUCCESS = "success"
    PLAN_2_PENDING = "plan_2_pending"
    PLAN_2_MATCH = "plan_2_match"
    PLAN_3_REQUIRED = "plan_3_required"
    ERROR = "error"
    EMPTY = "empty"


# =========================
# LRU Cache محسّن
# =========================
class LRUCache:
    """Cache بحد أقصى وحذف تلقائي للأقدم"""
    def __init__(self, max_size: int = 100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def clear(self):
        self.cache.clear()
    
    def __len__(self):
        return len(self.cache)


def server(input, output, session):
    # =========================
    # 1. إدارة الحالة (State Management)
    # =========================
    database_data = reactive.value({})
    models_index = reactive.value([])
    autocomplete_index = reactive.value(None)
    custom_panels = reactive.value([])
    custom_sensors = reactive.value([])
    fast_index_cache = reactive.value(None)

    current_phone = reactive.value("")
    suggestions_list = reactive.value([])
    show_curtain = reactive.value(False)

    plan_results = reactive.value(None)
    last_monitor_status = reactive.value("OFFLINE")
    last_sync_timestamp = reactive.value("لم تتم المزامنة بعد")

    # متغيرات التحكم
    last_sync_time = reactive.value(0.0)
    last_db_hash = reactive.value("")
    
    SYNC_INTERVAL = 5.0
    
    workflow_cache = LRUCache(max_size=100)

    # =========================
    # 2. دوال مساعدة محسنة
    # =========================
    def normalize_text(text: str) -> str:
        """توحيد تطبيع النص مع autocomplete index"""
        if not text:
            return ""
        cleaned = re.sub(r'[^\w\s\u0621-\u064a+\-.]', '', str(text).lower())
        return re.sub(r'\s+', ' ', cleaned).strip()

    def safe_float(value: str) -> Optional[float]:
        """دعم الفاصلة والنقطة في المقاسات"""
        try:
            normalized = str(value).replace(',', '.').strip()
            return float(normalized)
        except (ValueError, TypeError):
            return None

    def compute_db_hash(db: dict) -> str:
        """حساب hash آمن مع استخدام .get() لمنع KeyError"""
        try:
            status = get_status()
            if isinstance(status, dict):
                last_sync = status.get("last_sync", "")
                if last_sync:
                    return hashlib.sha256(str(last_sync).encode()).hexdigest()
            
            # Fallback: حساب hash للموديلات
            flat_models = sorted({
                m for p in db.values() 
                for s in p.values() 
                for m in s.get("models", [])
                if isinstance(m, str)
            })
            return hashlib.sha256(str(flat_models).encode()).hexdigest()
        except Exception:
            return ""

    def toggle_loading(show: bool):
        """التحكم في مؤشر التحميل مع تسجيل الأخطاء"""
        try:
            session.send_custom_message('toggle_loading', {'show': show})
        except Exception as e:
            log.debug(f"Failed to toggle loading: {e}")

    # =========================
    # 3. Workflow منظم
    # =========================
    def run_workflow_structured(phone: str, db: dict) -> Dict[str, Any]:
        """تشغيل Workflow وإرجاع قاموس منظم"""
        start = time.time()
        try:
            cache_key = f"{normalize_text(phone)}:{last_db_hash()[:8]}"
            
            cached = workflow_cache.get(cache_key)
            if cached is not None:
                log.debug(f"Cache hit for: {phone}")
                return cached
            
            size, panel, sensor, real_name = find_model_coords(db, phone)
            
            if real_name:
                # حماية من None
                compatibles = get_compatibles_strict(db, size, panel, sensor, real_name) or {}
                result = {
                    "status": ResultStatus.SUCCESS,
                    "coords": {
                        "size": size,
                        "panel": panel,
                        "sensor": sensor,
                        "real_name": real_name
                    },
                    "compatibles": compatibles
                }
            else:
                result = {
                    "status": ResultStatus.PLAN_2_PENDING,
                    "phone": phone,
                    "message": f"الموديل ({phone}) غير موجود في قاعدة البيانات"
                }
            
            workflow_cache.put(cache_key, result)
            
            elapsed = time.time() - start
            log.info(f"Workflow executed in {elapsed:.3f}s for: {phone} → {result['status']}")
            return result
            
        except Exception as e:
            log.error(f"Workflow error: {e}")
            return {"status": ResultStatus.ERROR, "message": str(e)}

    # =========================
    # 4. مزامنة قاعدة البيانات
    # =========================
    @reactive.effect
    def _sync_database():
        reactive.invalidate_later(SYNC_INTERVAL)
        
        now = time.time()
        if now - last_sync_time() < SYNC_INTERVAL - 0.5:
            return

        try:
            db = get_database()
            # ✅ حماية من None
            status_info = get_status() or {}

            if db and isinstance(db, dict):
                database_data.set(db)
                last_monitor_status.set(status_info.get("status", "UNKNOWN"))
                last_sync_timestamp.set(time.strftime("%H:%M:%S"))

                current_hash = compute_db_hash(db)
                
                if current_hash != last_db_hash():
                    last_db_hash.set(current_hash)
                    
                    index_start = time.time()
                    
                    new_flat_list = []
                    p_set = set()
                    s_set = set()
                    
                    for panels in db.values():
                        if not isinstance(panels, dict):
                            continue
                        for p_name, sensors in panels.items():
                            p_set.add(str(p_name))
                            if not isinstance(sensors, dict):
                                continue
                            for s_name, s_data in sensors.items():
                                s_set.add(str(s_name))
                                if isinstance(s_data, dict):
                                    new_flat_list.extend(s_data.get("models", []))

                    unique_models = sorted(list(set(new_flat_list)))
                    models_index.set(unique_models)
                    
                    try:
                        autocomplete_index.set(build_autocomplete_index(unique_models))
                    except Exception as e:
                        log.error(f"Failed to build autocomplete index: {e}")
                        autocomplete_index.set(None)
                    
                    try:
                        fast_index_cache.set(build_fast_index(db))
                    except Exception as e:
                        log.error(f"Failed to build fast index: {e}")
                        fast_index_cache.set(None)
                    
                    custom_panels.set(sorted(list(p_set)))
                    custom_sensors.set(sorted(list(s_set)))
                    
                    workflow_cache.clear()

                    index_elapsed = time.time() - index_start
                    log.info(f"Database synced: {len(models_index())} models | Index built in {index_elapsed:.3f}s")
            else:
                last_monitor_status.set("OFFLINE")
                log.warning("Database unavailable, will retry...")

        except Exception as e:
            log.error(f"Sync Error: {e}")
        
        finally:
            last_sync_time.set(time.time())

    # =========================
    # 5. البحث والاقتراحات
    # =========================
    @reactive.effect
    @reactive.event(input.search_query)
    def _handle_search():
        """
        تشغيل البحث عند كل تغير في مربع البحث.
        يمكن إضافة Debounce لاحقًا إذا لزم الأمر عبر reactive.invalidate_later().
        """
        query = normalize_text(input.search_query())
        current_phone.set(query)

        trie = autocomplete_index()
        if not query or not trie:
            suggestions_list.set([])
            show_curtain.set(False)
            return

        matches = trie.search_prefix(query, 10)
        if matches:
            suggestions_list.set(matches)
            show_curtain.set(True)
        else:
            suggestions_list.set([])
            show_curtain.set(False)

    @output
    @render.ui
    def suggestions_curtain():
        if not show_curtain():
            return None
        items = suggestions_list()
        if not items:
            return None

        # حماية HTML من الكسر
        safe_items = [json.dumps(m, ensure_ascii=False).replace("</", "<\\/") for m in items]
        
        return ui.div(
            *[
                ui.div(
                    m,
                    class_="suggestion-row",
                    onclick=f"Shiny.setInputValue('search_query', {safe}); Shiny.setInputValue('_hide_curtain_trigger', true, {{priority: 'event'}});"
                )
                for m, safe in zip(items, safe_items)
            ],
            class_="suggestions-curtain",
        )

    @reactive.effect
    @reactive.event(input._hide_curtain_trigger)
    def _hide_curtain_on_select():
        show_curtain.set(False)

    # =========================
    # 6. عرض النتائج
    # =========================
    @reactive.effect
    @reactive.event(input.search_query)
    def _on_model_selected():
        phone = current_phone()
        
        # مسح النتائج عند إفراغ البحث
        if not phone:
            plan_results.set(None)
            toggle_loading(False)
            return

        db = database_data()
        if not db:
            plan_results.set({
                "status": ResultStatus.ERROR,
                "message": "تعذر تحميل قاعدة البيانات. جاري إعادة المحاولة..."
            })
            toggle_loading(False)
            return

        toggle_loading(True)

        try:
            result = run_workflow_structured(phone, db)
            plan_results.set(result)
        except Exception as e:
            log.error(f"Search error: {e}")
            plan_results.set({
                "status": ResultStatus.ERROR,
                "message": f"حدث خطأ: {str(e)}"
            })
        finally:
            toggle_loading(False)

    @output
    @render.ui
    def results_workflow_view():
        res = plan_results()
        if not res:
            return None

        children = []
        status = res.get("status")
        
        if status == ResultStatus.SUCCESS:
            coords = res.get("coords", {})
            compatibles = res.get("compatibles", {})
            
            children.append(
                draw_technical_coords(
                    coords.get("size"),
                    coords.get("panel"),
                    coords.get("sensor"),
                    coords.get("real_name")
                )
            )
            
            # استخدام or [] لضمان عدم تمرير None
            exact_section = draw_neon_section(
                "مطابقة تماماً", 
                compatibles.get("exact") or [],
                "#2ecc71", "", "exact"
            )
            if exact_section:
                children.append(exact_section)
            
            plus_section = draw_neon_section(
                "أكبر بقليل ±0.03", 
                compatibles.get("plus") or [],
                "#3498db", "", "plus"
            )
            if plus_section:
                children.append(plus_section)
            
            minus_section = draw_neon_section(
                "أصغر قليلاً ±0.03", 
                compatibles.get("minus") or [],
                "#e67e22", "", "minus"
            )
            if minus_section:
                children.append(minus_section)
        
        elif status == ResultStatus.PLAN_2_PENDING:
            children.append(
                ui.div(
                    ui.h3("📋 خطة 2: إدخال المواصفات يدوياً", style="text-align:center; color: var(--primary-color);"),
                    ui.p(res.get("message", ""), style="text-align:center; opacity: 0.8; margin-bottom: 15px;"),
                    ui.input_text("p2_size", "المقاس:", placeholder="مثال: 6.67 أو 6,67"),
                    ui.input_selectize("p2_panel", "نوع الشاشة:", choices=custom_panels()),
                    ui.input_selectize("p2_sensor", "المستشعر:", choices=custom_sensors()),
                    ui.tags.button(
                        "🔍 بحث في المجموعات",
                        class_="btn-neon",
                        style="width:100%; background: var(--primary-color); margin-top:10px;",
                        onclick="Shiny.setInputValue('exec_plan2', true, {priority:'event'});"
                    ),
                    class_="glass-card",
                )
            )
        
        elif status == ResultStatus.PLAN_2_MATCH:
            children.append(
                ui.div(
                    ui.h3("✅ تم العثور على تطابق!", style="color: var(--success-color); text-align: center;"),
                    ui.div(res.get("message", ""), style="text-align: center;"),
                    class_="glass-card"
                )
            )
        
        elif status == ResultStatus.PLAN_3_REQUIRED:
            children.append(
                ui.div(
                    ui.h3("🚨 خطة الطوارئ 3", style="color: var(--danger-color); text-align: center;"),
                    ui.p("لم يُوجد تطابق. يرجى إنشاء مجموعة جديدة.", style="text-align: center;"),
                    class_="glass-card"
                )
            )
        
        elif status == ResultStatus.ERROR:
            children.append(
                ui.div(
                    ui.h3("⚠️ خطأ", style="color: var(--danger-color); text-align: center;"),
                    ui.p(res.get("message", ""), style="text-align: center;"),
                    class_="glass-card"
                )
            )

        return ui.div(*children, class_="fade-in")

    @reactive.effect
    @reactive.event(input.exec_plan2)
    def _exec_plan2():
        toggle_loading(True)
        
        try:
            size_val = safe_float(input.p2_size())
            panel = input.p2_panel()
            sensor = input.p2_sensor()
            
            # تحقق دقيق من المدخلات
            if size_val is None or not panel or not sensor:
                log.warning("Plan 2: Missing or invalid inputs")
                plan_results.set({
                    "status": ResultStatus.ERROR,
                    "message": "يرجى ملء جميع الحقول بشكل صحيح"
                })
                return

            idx = fast_index_cache()
            
            # حماية من None عند بناء الفهرس
            if idx is None:
                try:
                    idx = build_fast_index(database_data())
                    fast_index_cache.set(idx)
                except Exception as e:
                    log.error(f"Failed to build fast index: {e}")
                    plan_results.set({
                        "status": ResultStatus.ERROR,
                        "message": "فشل في بناء الفهرس السريع"
                    })
                    return
            
            # تمرير القيمة الرقمية مباشرة
            res = process_plan(size_val, panel, sensor, database_data(), idx)
            
            if res:
                plan_results.set({
                    "status": ResultStatus.PLAN_2_MATCH,
                    "message": f"المقاس: {res['size']} | الشاشة: {res['panel']} | المستشعر: {res['sensor']}",
                    "data": res
                })
                log.info(f"Plan 2 match found: {res}")
            else:
                plan_results.set({
                    "status": ResultStatus.PLAN_3_REQUIRED,
                    "message": "لم يُوجد تطابق في المجموعات"
                })
                log.info("Plan 2: No match found, escalating to Plan 3")
                
        except Exception as e:
            log.error(f"Plan 2 execution error: {e}")
            plan_results.set({
                "status": ResultStatus.ERROR,
                "message": f"خطأ في التنفيذ: {str(e)}"
            })
        finally:
            toggle_loading(False)

    # =========================
    # 7. نافذة الإعدادات
    # =========================
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _open_drawer():
        session.send_custom_message("toggle_drawer", {"action": "open"})

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    def _close_drawer():
        session.send_custom_message("toggle_drawer", {"action": "close"})

    # =========================
    # 8. مكونات حالة النظام
    # =========================
    @output
    @render.ui
    def database_status_area():
        total = len(models_index())
        sync_time = last_sync_timestamp()
        return ui.div(
            ui.div("📊 عدد الموديلات", class_="metric-title"),
            ui.div(str(total), class_="metric-value", style="color: var(--primary-color);"),
            ui.div(f"آخر تحديث: {sync_time}", style="font-size: 10px; opacity: 0.5; margin-top: 4px;"),
            class_="metric-box",
        )

    @output
    @render.ui
    def monitor_area():
        st = last_monitor_status()
        col = "#2ecc71" if st == "ONLINE" else ("#e67e22" if st == "FALLBACK" else "#ff5252")
        return ui.div(
            ui.div("🛰️ حالة المراقب", class_="metric-title"),
            ui.div(st, class_="metric-value", style=f"color: {col};"),
            class_="metric-box",
        )

    @output
    @render.ui
    def notifications_area():
        # حماية get_status() من إرجاع None
        status = get_status() or {}
        src = status.get("source", "N/A")
        return ui.div(
            ui.div("🔔 مصدر البيانات", class_="metric-title"),
            ui.div(src, class_="metric-value", style="color: var(--foundation-color);"),
            class_="metric-box",
        )

    # =========================
    # 9. منطقة الترحيب
    # =========================
    @output
    @render.ui
    def welcome_area():
        """إظهار الترحيب فقط عند عدم وجود نتائج"""
        if plan_results() is None:
            return draw_welcome_section()
        return None

    # =========================
    # 10. تنظيف الموارد
    # =========================
    def _on_session_ended():
        log.info("Session ended. Cleaning up resources...")
        workflow_cache.clear()
    
    session.on_ended(_on_session_ended)
