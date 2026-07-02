MODELS_INDEX_FILE = "models_index.txt"


def load_models_index():
    try:
        with open(MODELS_INDEX_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except OSError as e:
        log.error(f"Index load error: {e}")
        return []


def convert_database_from_raw(rows):
    db = {}

    if not isinstance(rows, list):
        return db

    for item in rows:
        if not isinstance(item, dict):
            continue

        size = str(item.get("size") or "").strip()
        panel = str(item.get("panel") or "Notch Screen").strip()
        sensor = str(item.get("sensor") or "hardware_top_sensor").strip()
        model = str(item.get("model_name") or "").strip()

        if not size or not model:
            continue

        db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})

        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)

    return db
