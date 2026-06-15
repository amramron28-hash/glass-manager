import os
import re
from database import supabase

_clean_regex = re.compile(r'[-_/ \s]+')

def normalize_text(text):
    if not text: return ""
    return _clean_regex.sub(' ', str(text).lower()).strip()

def find_model_coords(db_data, model_name):
    if not model_name or not db_data:
        return None, None, None, None
    target = normalize_text(model_name)
    for size_str, panels in db_data.items():
        for panel_name, sensors in panels.items():
            for sensor_name, sensor_data in sensors.items():
                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data
                for m in models_list:
                    if normalize_text(m) == target:
                        return size_str, panel_name, sensor_name, m
    return None, None, None, None

# ==========================================
# ⚖️ دالة الحساب الدقيق للفروقات بناءً على طلبك (±0.03)
# ==========================================
def get_compatibles_strict(db_data, model_name):
    results = {"exact": [], "plus": [], "minus": [], "warn": []}
    size_str, panel, sensor, real_name = find_model_coords(db_data, model_name)
    if not size_str: return results

    try:
        current_size = float(size_str)
    except ValueError:
        return results

    for size_key, panels in db_data.items():
        try:
            target_size = float(size_key)
        except ValueError: continue

        # 🎯 تطبيق الفارق الحسابي الدقيق لشاشات الزجاج (±0.03)
        diff = round(target_size - current_size, 2)

        for panel_key, sensors in panels.items():
            if panel_key != panel: continue
            for sensor_key, sensor_data in sensors.items():
                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data
                for m in models_list:
                    if normalize_text(m) == normalize_text(real_name): continue
                    
                    if diff == 0.0:
                        if sensor_key == sensor: results["exact"].append(m)
                        else: results["warn"].append(m)
                    elif 0.01 <= diff <= 0.03:
                        results["plus"].append(m)  # أكبر بقليل (±0.03)
                    elif -0.03 <= diff <= -0.01:
                        results["minus"].append(m) # أصغر بقليل (±0.03)
    return results

# ==========================================
# 🛡️ يد المراقب الصامت: التدمير التلقائي للتكرار في السحابة
# ==========================================
def run_intelligent_inspector(db_data=None):
    changes_made = False
    cleaned_db = {}
    try:
        res = supabase.table("phones").select("*").execute()
        rows = res.data or []
        for r in rows:
            row_id = r.get("id")
            size = str(r.get("size", "")).strip()
            panel = str(r.get("panel", "")).strip()
            sensor = str(r.get("sensor", "")).strip()
            model = str(r.get("model_name") or r.get("model") or "").strip()

            if not all([size, panel, sensor, model]) or size == "" or model == "":
                supabase.table("phones").delete().eq("id", row_id).execute()
                changes_made = True
                continue

            cleaned_db.setdefault(size, {})
            cleaned_db[size].setdefault(panel, {})
            cleaned_db[size][panel].setdefault(sensor, {"models": []})

            if model not in cleaned_db[size][panel][sensor]["models"]:
                cleaned_db[size][panel][sensor]["models"].append(model)
            else:
                # تدمير السطور المكررة مباشرة من السحابة
                supabase.table("phones").delete().eq("id", row_id).execute()
                changes_made = True
        return cleaned_db, changes_made
    except Exception:
        return db_data if db_data else {}, False

