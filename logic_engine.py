import re
import time
from typing import Dict, List, Optional, Tuple, Any
from core.logger import get_logger

# الثوابت
STATUS_SUCCESS = "success"
STATUS_PLAN_2 = "plan_2"
STATUS_PLAN2_SUCCESS = "plan2_success"
STATUS_PLAN_3 = "plan_3"
STATUS_ERROR = "error"
STATUS_NOT_FOUND = "not_found"

TOLERANCE = 0.05
EXACT_TOLERANCE = 0.001

log = get_logger("logic_engine")

def normalize_text(text: Any) -> str:
    """إزالة أي رمز غير أبجدي رقمي وتوحيد الأحرف (مع مراعاة دعم تعدد اللغات)."""
    return re.sub(r'[^a-z0-9\u0621-\u064a]+', '', str(text).lower())

def extract_numeric_size(size_string: Any) -> Optional[float]:
    """استخراج المقاس الرقمي، يعيد None في حال الفشل."""
    match = re.search(r"[-+]?\d*\.\d+|\d+", str(size_string))
    return float(match.group()) if match else None

def run_system_workflows(phone: str, db_data: Dict[str, Any], plan2_input: Optional[dict] = None) -> dict:
    start_time = time.time()
    phone = (phone or "").strip()
    
    if not isinstance(db_data, dict):
        return {"status": STATUS_ERROR, "message": "قاعدة بيانات غير صالحة"}
    
    try:
        # PLAN 1: البحث المباشر
        log.info(f"PLAN 1 STARTED: {phone}")
        size, panel, sensor, real_name = find_model_coords(db_data, phone)
        if real_name:
            log.info("PLAN 1 SUCCESS")
            compatibles = get_compatibles_strict(db_data, size, panel, sensor, real_name)
            return {"status": STATUS_SUCCESS, "coords": {"size": size, "panel": panel, "sensor": sensor, "real_name": real_name}, "compatibles": compatibles}
        
        # PLAN 2: البحث عبر المواصفات
        log.info("PLAN 1 FAILED. PLAN 2 STARTED.")
        if not isinstance(plan2_input, dict):
            return {"status": STATUS_NOT_FOUND, "message": "الموديل غير موجود"}
        
        if not all(plan2_input.get(k) for k in ["size", "panel", "sensor"]):
            return {"status": STATUS_ERROR, "message": "بيانات غير مكتملة"}
        
        matched_group = find_group_by_specs(db_data, plan2_input)
        if matched_group:
            log.info(f"PLAN 2 SUCCESS: {matched_group.get('group_id')}")
            return {"status": STATUS_PLAN2_SUCCESS, **matched_group}
        
        # PLAN 3: تحضير الإنشاء
        log.warning(f"PLAN 2 FAILED. Specs: {plan2_input}")
        return {
            "status": STATUS_PLAN_3, "input_data": plan2_input,
            "suggested_size": plan2_input.get("size"),
            "suggested_panel": plan2_input.get("panel"),
            "suggested_sensor": plan2_input.get("sensor")
        }
    except Exception as e:
        log.exception(f"Workflow error: {e}")
        return {"status": STATUS_ERROR, "message": "خطأ داخلي"}
    finally:
        log.info(f"Execution time: {time.time() - start_time:.4f}s")

def find_model_coords(db_data: Dict, phone: str) -> Tuple[Optional[str], ...]:
    search_norm = normalize_text(phone)
    best_match = None
    
    for size, panels in db_data.items():
        if not isinstance(panels, dict): continue
        for p, sensors in panels.items():
            if not isinstance(sensors, dict): continue
            for s, data in sensors.items():
                models = data.get("models")
                if not isinstance(models, list): continue
                for model in models:
                    m_norm = normalize_text(model)
                    if m_norm == search_norm: return size, p, s, model
                    if (m_norm.startswith(search_norm) or search_norm in m_norm) and not best_match:
                        best_match = (size, p, s, model)
    return best_match if best_match else (None, None, None, None)

def get_compatibles_strict(db_data: Dict, size: str, panel: str, sensor: str, real_name: str) -> dict:
    curr_n = extract_numeric_size(size) or 0.0
    res = {"exact": [], "plus": [], "minus": []}
    
    for s_k, panels in db_data.items():
        if not isinstance(panels, dict): continue
        panel_data = panels.get(panel)
        if not isinstance(panel_data, dict) or sensor not in panel_data: continue
        
        models = panel_data[sensor].get("models", [])
        other_n = extract_numeric_size(s_k)
        if other_n is None: continue
        
        diff = other_n - curr_n
        target = "exact" if abs(diff) < EXACT_TOLERANCE else ("plus" if 0 < diff <= TOLERANCE else ("minus" if -TOLERANCE <= diff < 0 else None))
        if target:
            res[target].extend([m for m in models if normalize_text(m) != normalize_text(real_name)])
    
    for k in res:
        res[k] = sorted(list(dict.fromkeys(res[k])))
    log.info(f"Compatibles found - Exact: {len(res['exact'])}, Plus: {len(res['plus'])}, Minus: {len(res['minus'])}")
    return res

def find_group_by_specs(db_data: Dict, specs: dict, tol: float = TOLERANCE) -> Optional[dict]:
    req_n = extract_numeric_size(specs.get("size"))
    if req_n is None: return None
    p_norm, s_norm = normalize_text(specs.get("panel")), normalize_text(specs.get("sensor"))
    
    for s_key, panels in db_data.items():
        s_n = extract_numeric_size(s_key)
        if s_n is None or abs(s_n - req_n) > tol: continue
        
        if not isinstance(panels, dict): continue
        for p_key, sensors in panels.items():
            if normalize_text(p_key) != p_norm: continue
            
            if not isinstance(sensors, dict): continue
            for s_k_in, data in sensors.items():
                if normalize_text(s_k_in) == s_norm:
                    return {
                        "group_id": f"{p_key}-{s_k_in}",
                        "models": sorted(list(dict.fromkeys(data.get("models", [])))),
                        "size": s_key, "panel": p_key, "sensor": s_k_in
                    }
    return None

