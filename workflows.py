import re, requests
from html import escape


def extract_numeric_size(size_string):
    try:
        match = re.search(r"[-+]?\d*\.\d+|\d+", str(size_string))
        if match:
            return float(match.group())
    except:
        pass
    return None


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

                models = data.get("models", []) if isinstance(data, dict) else []

                for model in models:

                    if str(model).strip().lower() == search:

                        return size, panel, sensor, model



    for size, panels in db_data.items():

        if not isinstance(panels, dict):
            continue

        for panel, sensors in panels.items():

            if not isinstance(sensors, dict):
                continue

            for sensor, data in sensors.items():

                models = data.get("models", []) if isinstance(data, dict) else []

                for model in models:

                    if search in str(model).lower():

                        return size, panel, sensor, model



    return None, None, None, None




def get_compatibles_strict(
    db_data,
    current_size,
    current_panel,
    current_sensor,
    real_name
):

    result = {
        "exact": [],
        "plus": [],
        "minus": []
    }


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


                models = data.get("models", []) if isinstance(data, dict) else []



                for model in models:


                    if str(model).lower() == str(real_name).lower():
                        continue



                    if abs(diff) < 0.001:

                        if model not in result["exact"]:
                            result["exact"].append(model)



                    elif 0 < diff <= tolerance:

                        if model not in result["plus"]:
                            result["plus"].append(model)



                    elif -tolerance <= diff < 0:

                        if model not in result["minus"]:
                            result["minus"].append(model)



    return result





def run_system_workflows(phone, db_data, suggestions=None):

    from shiny import ui

    from ui_components import (
        draw_technical_coords,
        draw_neon_section
    )



    if not phone:

        return ui.div()



    size, panel, sensor, real_name = find_model_coords(
        db_data,
        phone
    )


    output = []



    if real_name:



        output.append(

            draw_technical_coords(
                size,
                panel,
                sensor,
                real_name
            )

        )



        compatible = get_compatibles_strict(
            db_data,
            size,
            panel,
            sensor,
            real_name
        )



        output.append(

            draw_neon_section(
                "مطابقة تماماً",
                compatible["exact"],
                "#2ecc71",
                "🟢",
                "exact"
            )

        )



        output.append(

            draw_neon_section(
                "أكبر بقليل ±0.03",
                compatible["plus"],
                "#3498db",
                "🔵",
                "plus"
            )

        )



        output.append(

            draw_neon_section(
                "أصغر قليلاً ±0.03",
                compatible["minus"],
                "#e67e22",
                "🟠",
                "minus"
            )

        )



    else:



        output.append(

            ui.HTML(

                f"""

                <div class="flat-warning-card">

                ⚠️ الموديل ({escape(phone)}) غير موجود في قاعدة البيانات!

                </div>


                <div class="glass-card"

                style="margin-top:15px;

                border-color:#3498db;

                text-align:center;">


                <h4 style="color:#3498db;">

                📋 تشغيل الخطة 2: إدخال يدوي للبحث في المجموعات

                </h4>


                <button

                onclick="Shiny.setInputValue('trigger_plan_2','{escape(phone)}',{{priority:'event'}})"

                class="btn-neon"

                style="width:100%;

                padding:12px;

                background:#3498db;

                border:none;

                border-radius:8px;

                color:white;

                font-weight:bold;

                cursor:pointer;

                margin-top:10px;">

                🚀 ابدأ إدخال المواصفات والمطابقة الفنية

                </button>


                </div>

                """

            )

        )



    return ui.div(*output)
