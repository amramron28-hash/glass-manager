import re
from html import escape
from functools import lru_cache
from shiny import ui


def extract_numeric_size(size_string):
    try:
        match = re.search(r"[-+]?\d*\.\d+|\d+", str(size_string))
        return float(match.group()) if match else None
    except:
        return None


# =========================
# FAST INDEX LOOKUP (OPTIMIZED)
# =========================
def find_model_coords(db_data, phone_name):

    if not phone_name or not db_data:
        return None, None, None, None

    search = str(phone_name).strip().lower()

    for size, panels in db_data.items():

        if not isinstance(panels, dict):
            continue

        for panel, sensors in panels.items():

            if not isinstance(sensors, dict):
                continue

            for sensor, data in sensors.items():

                models = data.get("models") if isinstance(data, dict) else None
                if not models:
                    continue

                for model in models:
                    m = str(model).strip().lower()
                    if m == search:
                        return size, panel, sensor, model

    # fallback partial match
    for size, panels in db_data.items():

        if not isinstance(panels, dict):
            continue

        for panel, sensors in panels.items():

            if not isinstance(sensors, dict):
                continue

            for sensor, data in sensors.items():

                models = data.get("models") if isinstance(data, dict) else None
                if not models:
                    continue

                for model in models:
                    if search in str(model).lower():
                        return size, panel, sensor, model

    return None, None, None, None


# =========================
# COMPATIBILITY ENGINE (SAFE)
# =========================
def get_compatibles_strict(db_data, current_size, current_panel, current_sensor, real_name):

    result = {"exact": [], "plus": [], "minus": []}

    current = extract_numeric_size(current_size)
    if current is None:
        return result

    tolerance = 0.03

    for size_key, panels in db_data.items():

        other = extract_numeric_size(size_key)
        if other is None or not isinstance(panels, dict):
            continue

        diff = other - current

        for panel_key, sensors in panels.items():

            if panel_key != current_panel:
                continue

            if not isinstance(sensors, dict):
                continue

            for sensor_key, data in sensors.items():

                if sensor_key != current_sensor:
                    continue

                models = data.get("models") if isinstance(data, dict) else None
                if not models:
                    continue

                for model in models:

                    if str(model).lower() == str(real_name).lower():
                        continue

                    if abs(diff) < 0.001:
                        result["exact"].append(model)

                    elif 0 < diff <= tolerance:
                        result["plus"].append(model)

                    elif -tolerance <= diff < 0:
                        result["minus"].append(model)

    return result


# =========================
# MAIN WORKFLOW (FIXED RENDER FLOW)
# =========================
def run_system_workflows(phone, db_data, suggestions=None):

    if not phone:
        return ui.div()

    size, panel, sensor, real_name = find_model_coords(db_data, phone)

    output = []

    if not real_name:

        return ui.div(
            ui.HTML(f"""
            <div class="flat-warning-card">
                ⚠️ الموديل ({escape(phone)}) غير موجود
            </div>

            <div style="margin-top:15px;text-align:center;">
                <button onclick="Shiny.setInputValue('trigger_plan_2','{escape(phone)}',{{priority:'event'}})"
                        style="padding:12px;background:#3498db;color:white;border:none;border-radius:8px;width:100%;">
                    تشغيل الخطة 2
                </button>
            </div>
            """)
        )

    # =========================
    # VALID MODEL FOUND
    # =========================

    from ui_components import draw_technical_coords, draw_neon_section

    output.append(draw_technical_coords(size, panel, sensor, real_name))

    compatible = get_compatibles_strict(db_data, size, panel, sensor, real_name)

    output.append(draw_neon_section("مطابقة تماماً", compatible["exact"], "#2ecc71", "🟢", "exact"))
    output.append(draw_neon_section("أكبر قليلاً", compatible["plus"], "#3498db", "🔵", "plus"))
    output.append(draw_neon_section("أصغر قليلاً", compatible["minus"], "#e67e22", "🟠", "minus"))

    return ui.div(*output)
