import re


# =========================
# 🟢 تحسين الأداء (Precompiled regex)
# =========================
_clean_regex = re.compile(r'[-_/ \s]+')


def normalize_text(text):
    """
    تنظيف سريع وآمن للنصوص (محسن للأداء)
    """
    if not text:
        return ""

    return _clean_regex.sub(' ', str(text).lower()).strip()


# =========================
# 🟢 البحث اللحظي
# =========================
def filter_models_live(db_data, search_term):

    if not search_term:
        return []

    normalized_search = normalize_text(search_term)
    matched_models = []

    for panels in db_data.values():
        for sensors in panels.values():
            for sensor_data in sensors.values():

                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data

                for model in models_list:
                    if normalized_search in normalize_text(model):
                        matched_models.append(model)

    return sorted(set(matched_models))


# =========================
# 🟢 إيجاد موقع الهاتف
# =========================
def find_model_coords(db_data, model_name):

    if not model_name:
        return None, None, None, None

    target = normalize_text(model_name)

    for size_str, panels in db_data.items():

        # 🛡️ حماية من float crash
        try:
            float(size_str)
        except:
            continue

        for panel_name, sensors in panels.items():
            for sensor_name, sensor_data in sensors.items():

                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data

                for m in models_list:
                    if normalize_text(m) == target:
                        return size_str, panel_name, sensor_name, m

    return None, None, None, None


# =========================
# 🟢 التوافقات
# =========================
def get_compatibles_strict(db_data, model_name):

    results = {
        "current_model": {"size": "0.00", "panel": "", "sensor": ""},
        "exact": [],
        "plus": [],
        "minus": [],
        "warn": []
    }

    size_str, panel, sensor, real_name = find_model_coords(db_data, model_name)

    if not size_str:
        return results

    results["current_model"] = {"size": size_str, "panel": panel, "sensor": sensor}

    try:
        current_size = float(size_str)
    except:
        return results

    for size_key, panels in db_data.items():

        try:
            target_size = float(size_key)
        except:
            continue

        diff = round(target_size - current_size, 2)

        for panel_key, sensors in panels.items():

            if panel_key != panel:
                continue

            for sensor_key, sensor_data in sensors.items():

                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data

                for m in models_list:

                    if normalize_text(m) == normalize_text(real_name):
                        continue

                    if diff == 0.0:
                        (results["exact"] if sensor_key == sensor else results["warn"]).append(m)

                    elif 0.01 <= diff <= 0.03:
                        (results["plus"] if sensor_key == sensor else results["warn"]).append(m)

                    elif -0.03 <= diff <= -0.01:
                        (results["minus"] if sensor_key == sensor else results["warn"]).append(m)

    return {
        "current_model": results["current_model"],
        "exact": sorted(set(results["exact"])),
        "plus": sorted(set(results["plus"])),
        "minus": sorted(set(results["minus"])),
        "warn": sorted(set(results["warn"]))
    }


# =========================
# 🟢 تنظيف البيانات
# =========================
def run_intelligent_inspector(db_data):

    cleaned_db = {}
    changes_made = False

    for size_key, panels in db_data.items():

        cleaned_size = str(size_key).strip()
        cleaned_db.setdefault(cleaned_size, {})

        for panel_key, sensors in panels.items():

            cleaned_panel = str(panel_key).strip()
            cleaned_db[cleaned_size].setdefault(cleaned_panel, {})

            for sensor_key, sensor_data in sensors.items():

                cleaned_sensor = str(sensor_key).strip()

                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data

                seen = {}
                unique_models = []

                for m in models_list:

                    cleaned_name = " ".join(str(m).split())
                    norm = normalize_text(cleaned_name)

                    if norm and norm not in seen:
                        seen[norm] = True
                        unique_models.append(cleaned_name)
                    else:
                        changes_made = True

                cleaned_db[cleaned_size][cleaned_panel][cleaned_sensor] = {
                    "models": sorted(unique_models)
                }

    return cleaned_db, changes_made
