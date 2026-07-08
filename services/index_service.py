from typing import Dict, List, Set, Tuple
from core.logger import get_logger

log = get_logger("index_service")


def build_fast_index(db: Dict) -> Dict[Tuple[str, str], Dict[str, Set[str]]]:
    """
    بناء فهرس سريع للوصول المباشر O(1)
    الهيكلية:
        {(panel, sensor): {size: set(models)}}

    استخدام set يزيل التكرارات تلقائيًا.
    """
    index: Dict[Tuple[str, str], Dict[str, Set[str]]] = {}

    if not isinstance(db, dict):
        return index

    for size, panels in db.items():
        if not isinstance(panels, dict):
            continue

        for panel, sensors in panels.items():
            if not isinstance(sensors, dict):
                continue

            for sensor, data in sensors.items():
                key = (panel, sensor)

                if key not in index:
                    index[key] = {}

                # استخراج قائمة الموديلات بأمان
                models = data.get("models", []) if isinstance(data, dict) else []

                clean_models = {
                    model.strip()
                    for model in models
                    if isinstance(model, str) and model.strip()
                }

                if clean_models:
                    index[key].setdefault(size, set()).update(clean_models)

    log.info(f"Built fast index with {len(index)} unique groups")
    return index


def extract_panels_sensors(db: Dict) -> Tuple[List[str], List[str]]:
    """
    استخراج جميع أنواع الـ Panel والـ Sensor الموجودة في قاعدة البيانات.
    """
    panels: Set[str] = set()
    sensors: Set[str] = set()

    if not isinstance(db, dict):
        return [], []

    for panels_dict in db.values():
        if not isinstance(panels_dict, dict):
            continue

        for panel_name, sensors_dict in panels_dict.items():
            panels.add(panel_name)

            if isinstance(sensors_dict, dict):
                sensors.update(sensors_dict.keys())

    return sorted(list(panels)), sorted(list(sensors))
