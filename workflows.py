import re
import requests
from html import escape

def extract_numeric_size(size_string):
    try:
        match = re.search(r"[-+]?\d*\.\d+|\d+", str(size_string))
        if match:
            return float(match.group())
    except Exception:
        pass
    return None

def find_model_coords(db_data, phone_name):
    if not phone_name or not db_data:
        return None, None, None, None

    search = str(phone_name).strip().lower()

    # الخطة 1: تطابق كامل وصارم بالاسم
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

    # تطابق جزئي بالاسم
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

def get_compatibles_strict(db_data, current_size, current_panel, current_sensor, real_name):
    result = {"exact": [], "plus": [], "minus": []}
    
    current = extract_numeric_size(current_size)
    if current is None:
        return result

    tolerance = 0.03

    for size_key, panels in db_data.items():
        other = extract_numeric_size(size_key)
        if other is None:
            continue

        diff = other - current

        if not isinstance(panels, dict):
            continue

        for panel_key, sensors in panels.items():
            # قاعدة Redmi 9 و Redmi 9A الصارمة: يجب فحص التطابق الفني الكامل للمستشعر والشاشة
            if panel_key != current_panel or vec_sensor_check(sensors, current_sensor, diff, tolerance, real_name, result):
                continue

    return result

def vec_sensor_check(sensors, current_sensor, diff, tolerance, real_name, result):
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
    return False

def ai_background_global_verify(phone_name):
    try:
        url = "https://example.com" + requests.utils.quote(str(phone_name))
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            data = r.json()
            return {
                "size": str(data.get("size", "غير محدد")),
                "panel": str(data.get("panel", "غير محدد")),
                "sensor": str(data.get("sensor", "غير محدد"))
            }
    except Exception:
        pass
    return None

def run_system_workflows(phone, db_data, suggestions=None):
    from ui_components import draw_technical_coords, draw_neon_section

    if not phone:
        return ""

    size, panel, sensor, real_name = find_model_coords(db_data, phone)
    output = []

    # الخطة 1: الاسم موجود ومطابق تماماً في قاعدة البيانات
    if real_name:
        output.append(str(draw_technical_coords(size, panel, sensor, real_name)))
        compatible = get_compatibles_strict(db_data, size, panel, sensor, real_name)

        # عرض المجموعات بالألوان التنافسية الصحيحة (النيون والزجاجي)
        output.append(str(draw_neon_section("مطابقة تماماً", compatible["exact"], "#2ecc71", "🟢", "exact")))
        output.append(str(draw_neon_section("أكبر قليلاً (الخطة 2)", compatible["plus"], "#3498db", "🔵", "plus")))
        output.append(str(draw_neon_section("أصغر قليلاً (خطة الطوارئ 3)", compatible["minus"], "#e67e22", "🟠", "minus")))
        
        # كود إشارة لإغلاق الستارة تلقائياً في الواجهة
        output.append("<script>Shiny.setInputValue('hide_curtain_signal', Math.random());</script>")
    else:
        # لم يجد الاسم -> تفعيل واجهة الخطة 2 التفاعلية (إدخال يدوي)
        output.append(f"""
        <div class="flat-warning-card">
            ⚠️ الموديل ({escape(phone)}) غير موجود في قاعدة البيانات!
        </div>
        <div class="glass-card" style="margin-top:15px; border-color:#3498db;">
            <h4 style="color:#3498db; text-align:center;">📋 تشغيل الخطة 2: إدخال يدوي للبحث في المجموعات</h4>
            <p style="font-size:14px; text-align:center; color:#bbb;">لم نجد الهاتف بالاسم، يرجى إدخال المواصفات للبحث الفني:</p>
            <div style="display:flex; flex-direction:column; gap:10px; margin-top:15px;">
                <button onclick="Shiny.setInputValue('trigger_plan_2', '{escape(phone)}', {{priority: 'event'}})" class="btn-neon" style="width:100%; padding:12px; background:#3498db; border:none; border-radius:8px; color:white; font-weight:bold; cursor:pointer;">
                    🚀 ابدأ إدخال المواصفات والمطابقة الفنية
                </button>
            </div>
        </div>
        """)
        
    return "\n".join(output)
