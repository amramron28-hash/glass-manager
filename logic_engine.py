import os
import re
import time
from typing import Dict, Optional, Tuple, Any
from database import supabase
from core.logger import get_logger

# =========================
# CONFIG & STATUS
# =========================
STATUS_SUCCESS = "success"
STATUS_PLAN_2 = "plan_2"
STATUS_PLAN2_SUCCESS = "plan2_success"
STATUS_PLAN_3 = "plan_3"
STATUS_ERROR = "error"

TOLERANCE = 0.05
EXACT_TOLERANCE = 0.001

log = get_logger("logic_engine_supabase")
_clean_regex = re.compile(r'[^a-z0-9\u0621-\u064a]+')

# =========================
# FAST NORMALIZER (OPTIMIZED)
# =========================
_norm_cache = {}

def normalize_text(text: Any) -> str:
    """تنظيف النص للبحث الدقيق والسريع"""
    if text in _norm_cache:
        return _norm_cache[text]
    
    if not text:
        cleaned = ""
    else:
        # إزالة كل ما ليس حرفاً أو رقماً (يدعم العربية والإنجليزية)
        cleaned = _clean_regex.sub('', str(text).lower())
        
    _norm_cache[text] = cleaned
    return cleaned

# =========================
# SIZE EXTRACTOR
# =========================
def extract_numeric_size(size_string: Any) -> Optional[float]:
    if not size_string:
        return None
    match = re.search(r"[-+]?\d*\.\d+|\d+", str(size_string))
    return float(match.group()) if match else None

# =========================
# DATA FETCHER (SUPABASE TO STRUCTURE)
# =========================
def fetch_db_structure() -> Dict:
    """جلب البيانات من Supabase وتحويلها لهيكلية متداخلة سريعة للبحث"""
    try:
        res = supabase.table("phones").select("*").execute()
        rows = res.data or []
        
        db_structure = {}
        for r in rows:
            size = str(r.get("size", "")).strip()
            panel = str(r.get("panel", "")).strip()
            sensor = str(r.get("sensor", "")).strip()
            model = str(r.get("model_name") or r.get("model") or "").strip()
            
            if not all([size, panel, sensor, model]):
                continue
                
            db_structure.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, []).append(model)
            
        return db_structure
    except Exception as e:
        log.error(f"Error fetching DB structure: {e}")
        return {}

# =========================
# MODEL FINDER (STABLE & FAST)
# =========================
def find_model_coords(db_data: Dict, phone: str) -> Tuple[Optional[str], ...]:
    search_norm = normalize_text(phone)
    best_match = None

    for size, panels in db_data.items():
        if not isinstance(panels, dict): continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict): continue
            for sensor, models_list in sensors.items():
                # التعامل مع القائمة سواء كانت dict بداخلها models أو list مباشرة
                if isinstance(models_list, dict):
                    models_list = models_list.get("models", [])
                
                for model in models_list:
                    m_norm = normalize_text(model)
                    
                    # Exact Match
                    if m_norm == search_norm:
                        return size, panel, sensor, model
                    
                    # Partial Match Fallback
                    if best_match is None and (m_norm.startswith(search_norm) or search_norm in m_norm):
                        best_match = (size, panel, sensor, model)

    return best_match if best_match else (None, None, None, None)

# =========================
# COMPATIBILITY ENGINE (FAST PATH)
# =========================
def get_compatibles_strict(db_data: Dict, size: str, panel: str, sensor: str, real_name: str) -> dict:
    curr_n = extract_numeric_size(size)
    if curr_n is None:
        return {"exact": [], "plus": [], "minus": [], "warn": []}

    res = {"exact": [], "plus": [], "minus": [], "warn": []}
    real_norm = normalize_text(real_name)

    for s_k, panels in db_data.items():
        if not isinstance(panels, dict): continue
        other_n = extract_numeric_size(s_k)
        if other_n is None: continue

        diff = other_n - curr_n

        panel_data = panels.get(panel)
        if not isinstance(panel_data, dict): continue
        
        # البحث في جميع المستشعرات لنفس الشاشة للمقارنة
        for s_key_in, sensor_data in panel_data.items():
            if isinstance(sensor_data, dict):
                models = sensor_data.get("models", [])
            else:
                models = sensor_data

            if not isinstance(models, list): continue

            bucket = None
            if abs(diff) < EXACT_TOLERANCE:
                bucket = "exact" if s_key_in == sensor else "warn"
            elif 0 < diff <= TOLERANCE:
                bucket = "plus"
            elif -TOLERANCE <= diff < 0:
                bucket = "minus"
            
            if bucket:
                for m in models:
                    if normalize_text(m) != real_norm:
                        res[bucket].append(m)

    # Remove duplicates
    for k in res:
        res[k] = sorted(list(dict.fromkeys(res[k])))
        
    return res

# =========================
# GROUP FINDER (PLAN 2)
# =========================
def find_group_by_specs(db_data: Dict, specs: dict, tol: float = TOLERANCE) -> Optional[dict]:
    req_n = extract_numeric_size(specs.get("size"))
    if req_n is None: return None

    p_norm = normalize_text(specs.get("panel"))
    s_norm = normalize_text(specs.get("sensor"))

    for s_key, panels in db_data.items():
        s_n = extract_numeric_size(s_key)
        if s_n is None or abs(s_n - req_n) > tol: continue
        if not isinstance(panels, dict): continue

        for p_key, sensors in panels.items():
            if normalize_text(p_key) != p_norm: continue
            if not isinstance(sensors, dict): continue

            for s_k_in, data in sensors.items():
                if normalize_text(s_k_in) != s_norm: continue
                
                models = data.get("models", []) if isinstance(data, dict) else data
                return {
                    "group_id": f"{p_key}-{s_k_in}",
                    "models": sorted(list(dict.fromkeys(models))),
                    "size": s_key,
                    "panel": p_key,
                    "sensor": s_k_in
                }
    return None

# =========================
# 🛡️ INTELLIGENT INSPECTOR (CLEANER)
# =========================
def run_intelligent_inspector(db_data=None):
    """
    يقوم بفحص جدول phones في Supabase، يحذف الصفوف الفارغة، 
    ويوحد التكرارات بناءً على (Size, Panel, Sensor, Model).
    """
    changes_made = False
    cleaned_db = {}
    seen_combinations = set()

    try:
        res = supabase.table("phones").select("id, size, panel, sensor, model_name, model").execute()
        rows = res.data or []

        for r in rows:
            row_id = r.get("id")
            size = str(r.get("size", "")).strip()
            panel = str(r.get("panel", "")).strip()
            sensor = str(r.get("sensor", "")).strip()
            model = str(r.get("model_name") or r.get("model") or "").strip()

            # 1. حذف البيانات الناقصة
            if not all([size, panel, sensor, model]):
                supabase.table("phones").delete().eq("id", row_id).execute()
                changes_made = True
                continue

            # 2. بناء الهيكل النظيف والتحقق من التكرار
            combo_key = f"{size}|{panel}|{sensor}|{model}"
            if combo_key in seen_combinations:
                # تكرار موجود، نحذف الصف الزائد من السحابة
                supabase.table("phones").delete().eq("id", row_id).execute()
                changes_made = True
            else:
                seen_combinations.add(combo_key)
                cleaned_db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})
                cleaned_db[size][panel][sensor]["models"].append(model)

        return cleaned_db, changes_made

    except Exception as e:
        log.exception(f"Inspector Error: {e}")
        return (db_data if db_data else {}, False)

# =========================
# MAIN WORKFLOW
# =========================
def run_system_workflows(phone: str, db_data: Optional[dict] = None, plan2_input: Optional[dict] = None) -> dict:
    start_time = time.time()
    phone = (phone or "").strip()

    # إذا تم تمرير قاعدة بيانات جاهزة (من silent_monitor مع دعم النسخة الاحتياطية
    # عند تعطل Supabase)، نستخدمها مباشرة بدل تكرار الاتصال بالسحابة في كل بحث
    if not db_data:
        db_data = fetch_db_structure()

    if not db_data:
        return {"status": STATUS_ERROR, "message": "DB_EMPTY_OR_ERROR"}

    try:
        # PLAN 1
        size, panel, sensor, real_name = find_model_coords(db_data, phone)

        if real_name:
            return {
                "status": STATUS_SUCCESS,
                "coords": {"size": size, "panel": panel, "sensor": sensor, "real_name": real_name},
                "compatibles": get_compatibles_strict(db_data, size, panel, sensor, real_name)
            }

        # PLAN 2
        if isinstance(plan2_input, dict):
            matched = find_group_by_specs(db_data, plan2_input)
            if matched:
                return {"status": STATUS_PLAN2_SUCCESS, **matched}

        # PLAN 3
        return {
            "status": STATUS_PLAN_3,
            "input_data": plan2_input or {"size": None, "panel": None, "sensor": None}
        }

    except Exception as e:
        log.exception(f"Workflow error: {e}")
        return {"status": STATUS_ERROR, "message": "INTERNAL_ERROR"}

    finally:
        log.info(f"Execution time: {time.time() - start_time:.4f}s")
