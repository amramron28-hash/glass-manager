import json
import os
from core.logger import get_logger

log = get_logger("database_service")

# تأكد أن هذا المسار يشير إلى ملف models_db.json الذي أرسلته
MODELS_DB_FILE = "models_db.json"


def load_models_index():
    """تحميل وقراءة ملف قاعدة البيانات المتداخل"""
    if not os.path.exists(MODELS_DB_FILE):
        log.error(f"File not found: {MODELS_DB_FILE}")
        return []

    try:
        with open(MODELS_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # تحويل البيانات المتداخلة إلى قائمة مسطحة
            return convert_database_from_raw(data)
    except Exception as e:
        log.error(f"Error loading models index: {e}")
        return []


def convert_database_from_raw(data):
    """
    تحويل الهيكل المتداخل الموجود في models_db.json
    إلى قائمة مسطحة (Flat List) من الموديلات.
    """
    flattened_db = []

    if not isinstance(data, dict):
        return flattened_db

    try:
        for size, screens in data.items():
            for screen_type, sensors in screens.items():
                for sensor_type, content in sensors.items():
                    models = content.get("models", [])
                    for model in models:
                        flattened_db.append(
                            {
                                "model": model,
                                "size": size,
                                "screen": screen_type,
                                "sensor": sensor_type,
                            }
                        )
    except Exception as e:
        log.error(f"Conversion error: {e}")

    return flattened_db
