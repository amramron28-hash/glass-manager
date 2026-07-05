import re
import time
from typing import Dict, Optional, Tuple, Any
from core.logger import get_logger

# =========================
# STATUS
# =========================
STATUS_SUCCESS = "success"
STATUS_PLAN_2 = "plan_2"
STATUS_PLAN2_SUCCESS = "plan2_success"
STATUS_PLAN_3 = "plan_3"
STATUS_ERROR = "error"
STATUS_NOT_FOUND = "not_found"

TOLERANCE = 0.05
EXACT_TOLERANCE = 0.001

log = get_logger("logic_engine")


# =========================
# FAST NORMALIZER (OPTIMIZED)
# =========================
_norm_cache = {}

def normalize_text(text: Any) -> str:
    if text in _norm_cache:
        return _norm_cache[text]

    cleaned = re.sub(r'[^a-z0-9\u0621-\u064a]+', '', str(text).lower())
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
# MODEL FINDER (STABLE)
# =========================
def find_model_coords(db_data: Dict, phone: str) -> Tuple[Optional[str], ...]:

    search_norm = normalize_text(phone)
    best_match = None

    for size, panels in db_data.items():

        if not isinstance(panels, dict):
            continue

        for panel, sensors in panels.items():

            if not isinstance(sensors, dict):
                continue

            for sensor, data in sensors.items():

                models = data.get("models")
                if not isinstance(models, list):
                    continue

                for model in models:

                    m_norm = normalize_text(model)

                    # exact match = exit immediately
                    if m_norm == search_norm:
                        return size, panel, sensor, model

                    # partial match fallback (only first best)
                    if best_match is None and (
                        m_norm.startswith(search_norm) or search_norm in m_norm
                    ):
                        best_match = (size, panel, sensor, model)

    return best_match if best_match else (None, None, None, None)


# =========================
# COMPATIBILITY ENGINE (FAST PATH)
# =========================
def get_compatibles_strict(db_data: Dict, size: str, panel: str, sensor: str, real_name: str) -> dict:

    curr_n = extract_numeric_size(size)
    if curr_n is None:
        return {"exact": [], "plus": [], "minus": []}

    res = {"exact": [], "plus": [], "minus": []}

    real_norm = normalize_text(real_name)

    for s_k, panels in db_data.items():

        if not isinstance(panels, dict):
            continue

        other_n = extract_numeric_size(s_k)
        if other_n is None:
            continue

        diff = other_n - curr_n

        panel_data = panels.get(panel)
        if not isinstance(panel_data, dict):
            continue

        sensor_data = panel_data.get(sensor)
        if not isinstance(sensor_data, dict):
            continue

        models = sensor_data.get("models")
        if not isinstance(models, list):
            continue

        if abs(diff) < EXACT_TOLERANCE:
            bucket = "exact"
        elif 0 < diff <= TOLERANCE:
            bucket = "plus"
        elif -TOLERANCE <= diff < 0:
            bucket = "minus"
        else:
            continue

        for m in models:
            if normalize_text(m) != real_norm:
                res[bucket].append(m)

    # remove duplicates
    for k in res:
        res[k] = sorted(list(dict.fromkeys(res[k])))

    return res


# =========================
# GROUP FINDER (SAFE)
# =========================
def find_group_by_specs(db_data: Dict, specs: dict, tol: float = TOLERANCE) -> Optional[dict]:

    req_n = extract_numeric_size(specs.get("size"))
    if req_n is None:
        return None

    p_norm = normalize_text(specs.get("panel"))
    s_norm = normalize_text(specs.get("sensor"))

    for s_key, panels in db_data.items():

        s_n = extract_numeric_size(s_key)
        if s_n is None or abs(s_n - req_n) > tol:
            continue

        if not isinstance(panels, dict):
            continue

        for p_key, sensors in panels.items():

            if normalize_text(p_key) != p_norm:
                continue

            if not isinstance(sensors, dict):
                continue

            for s_k_in, data in sensors.items():

                if normalize_text(s_k_in) != s_norm:
                    continue

                models = data.get("models", [])

                return {
                    "group_id": f"{p_key}-{s_k_in}",
                    "models": sorted(list(dict.fromkeys(models))),
                    "size": s_key,
                    "panel": p_key,
                    "sensor": s_k_in
                }

    return None


# =========================
# MAIN WORKFLOW (STATE MACHINE READY)
# =========================
def run_system_workflows(phone: str, db_data: Dict[str, Any], plan2_input: Optional[dict] = None) -> dict:

    start_time = time.time()

    phone = (phone or "").strip()

    if not isinstance(db_data, dict):
        return {"status": STATUS_ERROR, "message": "DB_INVALID"}

    try:
        # =========================
        # PLAN 1
        # =========================
        size, panel, sensor, real_name = find_model_coords(db_data, phone)

        if real_name:
            return {
                "status": STATUS_SUCCESS,
                "coords": {
                    "size": size,
                    "panel": panel,
                    "sensor": sensor,
                    "real_name": real_name
                },
                "compatibles": get_compatibles_strict(
                    db_data, size, panel, sensor, real_name
                )
            }

        # =========================
        # PLAN 2
        # =========================
        if isinstance(plan2_input, dict):
            matched = find_group_by_specs(db_data, plan2_input)

            if matched:
                return {
                    "status": STATUS_PLAN2_SUCCESS,
                    **matched
                }

        # =========================
        # PLAN 3
        # =========================
        return {
            "status": STATUS_PLAN_3,
            "input_data": plan2_input or {
                "size": None,
                "panel": None,
                "sensor": None
            }
        }

    except Exception as e:
        log.exception(f"Workflow error: {e}")
        return {"status": STATUS_ERROR, "message": "INTERNAL_ERROR"}

    finally:
        log.info(f"Execution time: {time.time() - start_time:.4f}s")
