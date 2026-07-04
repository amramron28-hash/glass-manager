import re
from typing import Dict, List, Optional, Tuple, Any
from core.logger import get_logger

log = get_logger("logic_engine")
TOLERANCE = 0.05 
MIN_SEARCH_LEN = 3

def extract_numeric_size(size_string: Any) -> Optional[float]:
    if not isinstance(size_string, str): return None
    match = re.search(r"[-+]?\d*\.\d+|\d+", size_string)
    return float(match.group()) if match else None

def normalize_text(text: Any) -> str:
    return re.sub(r'[-\s]+', '', text.strip().lower()) if isinstance(text, str) else ""

def find_model_coords(db_data: Dict, phone_name: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    if not isinstance(db_data, dict) or not phone_name or not phone_name.strip(): 
        return None, None, None, None
    
    target = normalize_text(phone_name)
    partial_match = None
    
    for size_str, panels in db_data.items():
        if not isinstance(panels, dict): continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict): continue
            for sensor, s_data in sensors.items():
                models = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if not isinstance(models, list): continue
                
                for model in models:
                    if not isinstance(model, str): continue
                    clean_model = normalize_text(model)
                    if clean_model == target: return size_str, panel, sensor, model
                    if len(target) >= MIN_SEARCH_LEN and target in clean_model and not partial_match:
                        partial_match = (size_str, panel, sensor, model)
    return partial_match or (None, None, None, None)

def get_compatibles_strict(db_data: Dict, phone_name: str) -> Dict[str, List[str]]:
    compatibles = {"exact": set(), "plus": set(), "minus": set()}
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone_name)
    
    current_size = extract_numeric_size(size_str)
    if current_size is None: return {k: [] for k in compatibles}

    for size_key, panels in db_data.items():
        loop_size = extract_numeric_size(size_key)
        if loop_size is None or not isinstance(panels, dict): continue
        
        size_diff = loop_size - current_size
        for panel_key, sensors in panels.items():
            if not isinstance(panel_key, str) or panel_key != panel or not isinstance(sensors, dict): continue
            for sensor_key, s_data in sensors.items():
                if not isinstance(sensor_key, str): continue
                
                models = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if not isinstance(models, list): continue
                for model in models:
                    if not isinstance(model, str): continue
                    if real_name and model.lower() == real_name.lower(): continue
                    
                    if abs(size_diff) < 0.001 and sensor_key == sensor: compatibles["exact"].add(model)
                    elif 0 < size_diff <= TOLERANCE: compatibles["plus"].add(model)
                    elif -TOLERANCE <= size_diff < 0: compatibles["minus"].add(model)
                        
    return {k: sorted(list(v)) for k, v in compatibles.items()}

def run_system_workflows(phone: str, db_data: Dict) -> Dict:
    """إرجاع بيانات ليعالجها server.py."""
    if not isinstance(db_data, dict):
        log.error("Invalid database format")
        return {"status": "error", "message": "قاعدة بيانات تالفة"}

    try:
        size, panel, sensor, real_name = find_model_coords(db_data, phone)
        if not real_name:
            return {"status": "not_found", "message": f"الموديل {phone} غير موجود"}
        
        log.info(f"Successfully processed phone: {real_name}")
        return {
            "status": "success",
            "coords": {"size": size, "panel": panel, "sensor": sensor, "real_name": real_name},
            "compatibles": get_compatibles_strict(db_data, phone)
        }
    except Exception:
        log.exception("Workflow execution failed")
        return {"status": "error", "message": "حدث خطأ داخلي"}
