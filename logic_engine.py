import re
from typing import Dict, List, Optional, Tuple, Any

# الثوابت
STATUS_SUCCESS = "success"
STATUS_PLAN_2 = "plan_2"
STATUS_PLAN2_SUCCESS = "plan2_success"
STATUS_PLAN_3 = "plan_3"
STATUS_ERROR = "error"

TOLERANCE = 0.05
EXACT_TOLERANCE = 0.001
PLAN_ORDER = (1, 2, 3)

# الرسائل
MSG_DB_ERROR = "قاعدة البيانات غير متوفرة."
MSG_INPUT_ERROR = "بيانات المواصفات غير مكتملة."
MSG_SYS_ERROR = "حدث خطأ أثناء تنفيذ البحث."
MSG_NOT_FOUND = "الموديل غير موجود."

from core.logger import get_logger
log = get_logger("logic_engine")

def normalize_text(text: str) -> str:
    """إزالة أي رمز غير أبجدي رقمي وتوحيد الأحرف."""
    return re.sub(r'[^a-z0-9]+', '', str(text).lower())

def extract_numeric_size(size_string: str) -> float:
    match = re.search(r"[-+]?\d*\.\d+|\d+", str(size_string))
    return float(match.group()) if match else 0.0

def run_system_workflows(phone: str, db_data: Dict[str, Any], plan2_input: Optional[dict] = None) -> dict:
    """
    عقل النظام: ينفذ خطط البحث بالترتيب (1 -> 2 -> 3).
    """
    phone = phone.strip()
    if not isinstance(db_data, dict):
        return {"status": STATUS_ERROR, "message": MSG_DB_ERROR}
    
    try:
        # PLAN 1
        log.info(f"PLAN 1 STARTED: {phone}")
        size, panel, sensor, real_name = find_model_coords(db_data, phone)
        if real_name:
            log.info("PLAN 1 SUCCESS")
            return {
                "status": STATUS_SUCCESS,
                "coords": {"size": size, "panel": panel, "sensor": sensor, "real_name": real_name},
                "compatibles": get_compatibles_strict(db_data, size, panel, sensor, real_name)
            }
        
        # PLAN 2
        log.info("PLAN 1 FAILED. PLAN 2 STARTED.")
        if not plan2_input:
            return {"status": STATUS_PLAN_2, "message": MSG_NOT_FOUND}
        
        if not all([plan2_input.get(k) for k in ["size", "panel", "sensor"]]):
            return {"status": STATUS_ERROR, "message": MSG_INPUT_ERROR}
        
        matched_group = find_group_by_specs(db_data, plan2_input)
        if matched_group:
            log.info(f"PLAN 2 SUCCESS: {matched_group.get('group_id')}")
            return {"status": STATUS_PLAN2_SUCCESS, **matched_group}
        
        # PLAN 3
        log.info("PLAN 2 FAILED. PLAN 3 STARTED.")
        return {
            "status": STATUS_PLAN_3,
            "phone": phone, "input_data": plan2_input,
            "suggested_size": plan2_input.get("size"),
            "suggested_panel": plan2_input.get("panel"),
            "suggested_sensor": plan2_input.get("sensor"),
            "group_name_suggestion": f"{plan2_input.get('panel')}-{plan2_input.get('sensor')}"
        }
    except Exception as e:
        log.exception(f"CRITICAL ERROR for {phone}: {e}")
        return {"status": STATUS_ERROR, "message": MSG_SYS_ERROR}

def find_model_coords(db_data: Dict, phone: str) -> Tuple[Optional[str], ...]:
    search_norm = normalize_text(phone)
    best_match = None
    
    for size, panels in db_data.items():
        if not isinstance(panels, dict): continue
        for p, sensors in panels.items():
            if not isinstance(sensors, dict): continue
            for s, data in sensors.items():
                for model in data.get("models", []):
                    m_norm = normalize_text(model)
                    if m_norm == search_norm: return size, p, s, model # Priority 1: Exact
                    if (m_norm.startswith(search_norm) or search_norm in m_norm) and not best_match:
                        best_match = (size, p, s, model) # Priority 2: Partial
    return best_match if best_match else (None, None, None, None)

def get_compatibles_strict(db_data: Dict, size: str, panel: str, sensor: str, real_name: str, tol: float = TOLERANCE) -> dict:
    curr_n = extract_numeric_size(size)
    res = {"exact": [], "plus": [], "minus": []}
    
    for s_k, panels in db_data.items():
        if not isinstance(panels, dict) or panel not in panels or sensor not in panels[panel]: continue
        models = panels[panel][sensor].get("models", [])
        diff = extract_numeric_size(s_k) - curr_n
        
        target = "exact" if abs(diff) < EXACT_TOLERANCE else ("plus" if 0 < diff <= tol else ("minus" if -tol <= diff < 0 else None))
        if target:
            res[target].extend([m for m in models if normalize_text(m) != normalize_text(real_name)])
    
    for k in res: res[k] = sorted(list(dict.fromkeys(res[k])))
    return res

def find_group_by_specs(db_data: Dict, specs: dict, tol: float = TOLERANCE) -> Optional[dict]:
    req_n = extract_numeric_size(specs.get("size"))
    p_norm, s_norm = normalize_text(specs.get("panel")), normalize_text(specs.get("sensor"))
    
    for s_key, panels in db_data.items():
        if not isinstance(panels, dict) or abs(extract_numeric_size(s_key) - req_n) > tol: continue
        for p_key, sensors in panels.items():
            if not isinstance(sensors, dict) or normalize_text(p_key) != p_norm: continue
            for s_k_in, data in sensors.items():
                if normalize_text(s_k_in) == s_norm:
                    return {
                        "group_id": f"{p_key}-{s_k_in}",
                        "models": sorted(list(dict.fromkeys(data.get("models", [])))),
                        "size": s_key, "panel": p_key, "sensor": s_k_in
                    }
    return None
