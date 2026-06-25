import re

def find_model_coords(db_data, phone_name):
    """
    البحث في قاعدة البيانات عن قياسات وأبعاد الهاتف المستهدف.
    تعتمد على مطابقة النصوص بغض النظر عن حالة الأحرف (Case-insensitive).
    """
    if not phone_name or not db_data:
        return None, None, None, None
        
    phone_name_clean = phone_name.strip().lower()
    
    # المرور على أبعاد الشاشات في قاعدة البيانات المسجلة
    for size_str, panels in db_data.items():
        if not isinstance(panels, dict):
            continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict):
                continue
            for sensor, s_data in sensors.items():
                # استخراج قائمة الموديلات التابعة لهذا التصنيف
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if not isinstance(models_list, list):
                    continue
                    
                for model in models_list:
                    if model.strip().lower() == phone_name_clean:
                        # إرجاع: المقاس، نوع الشاشة، الحساس، والاسم الحقيقي المسجل
                        return size_str, panel, sensor, model
                        
    # في حال لم يتم العثور على تطابق تام، يتم البحث عن تطابق جزئي كخيار احتياطي
    for size_str, panels in db_data.items():
        if not isinstance(panels, dict):
            continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict):
                continue
            for sensor, s_data in sensors.items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if not isinstance(models_list, list):
                    continue
                for model in models_list:
                    if phone_name_clean in model.strip().lower():
                        return size_str, panel, sensor, model

    return None, None, None, None


def get_compatibles_strict(db_data, phone_name):
    """
    تحديد الهواتف البديلة والمتوافقة عبر 3 مستويات دقيقة:
    1. exact: نفس المقاس ونفس خصائص الشاشة والحساس تماماً.
    2. plus: الهواتف التي تزيد بمقدار تفاوت ضئيل جداً مسموح به.
    3. minus: الهواتف التي تقل بمقدار تفاوت ضئيل جداً مسموح به.
    """
    compatibles = {"exact": [], "plus": [], "minus": []}
    
    # جلب أبعاد الهاتف الحالي أولاً
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone_name)
    
    if not size_str:
        return compatibles

    # استخراج القيمة الرقمية للمقاس بالإنش (مثال: "6.5" من "6.5 inches")
    current_size = extract_numeric_size(size_str)
    if current_size is None:
        return compatibles

    # حد التفاوت المسموح به في قياسات زجاج الحماية (Tolerance Threshold)
    TOLERANCE = 0.05 

    for size_key, panels in db_data.items():
        if not isinstance(panels, dict):
            continue
            
        loop_size = extract_numeric_size(size_key)
        if loop_size is None:
            continue
            
        # فحص مستويات التطابق بناءً على المقاس الرياضي والتفاوت
        size_diff = loop_size - current_size
        
        for panel_key, sensors in panels.items():
            # فلترة صارمة: يجب تطابق نوع الشاشة لضمان انحناءات الزجاج وحواف الحماية
            if panel_key != panel:
                continue
                
            for sensor_key, s_data in sensors.items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if not isinstance(models_list, list):
                    continue
                    
                for model in models_list:
                    # استبعاد الهاتف المبحوث عنه من قائمة البدائل
                    if model.lower() == real_name.lower():
                        continue
                        
                    # 1. تطابق تام ومباشر
                    if abs(size_diff) < 0.001 and sensor_key == sensor:
                        if model not in compatibles["exact"]:
                            compatibles["exact"].append(model)
                    
                    # 2. زيادة طفيفة ضمن حدود التفاوت المقبولة
                    elif 0 < size_diff <= TOLERANCE:
                        if model not in compatibles["plus"]:
                            compatibles["plus"].append(model)
                            
                    # 3. نقصان طفيف ضمن حدود التفاوت المقبولة
                    elif -TOLERANCE <= size_diff < 0:
                        if model not in compatibles["minus"]:
                            compatibles["minus"].append(model)

    return compatibles


def extract_numeric_size(size_string):
    """دالة مساعدة لاستخراج الأرقام العشرية من النصوص البرمجية للمقاسات"""
    try:
        match = re.search(r"[-+]?\d*\.\d+|\d+", size_string)
        if match:
            return float(match.group())
    except Exception:
        pass
    return None
def run_system_workflows(phone, db_data, suggestions=None):

    from ui_components import (
        draw_technical_coords,
        draw_neon_section,
        draw_warning_card
    )

    if not phone:
        return ""


    size, panel, sensor, real_name = find_model_coords(
        db_data,
        phone
    )


    output = []


    if real_name:


        output.append(
            str(
                draw_technical_coords(
                    size,
                    panel,
                    sensor,
                    real_name
                )
            )
        )


        compatible = get_compatibles_strict(
            db_data,
            phone
        )


        output.append(
            str(
                draw_neon_section(
                    "مطابقة تماماً",
                    compatible.get("exact", []),
                    "#2ecc71",
                    "🟢",
                    "exact"
                )
            )
        )


        output.append(
            str(
                draw_neon_section(
                    "أكبر بقليل",
                    compatible.get("plus", []),
                    "#3498db",
                    "🔵",
                    "plus"
                )
            )
        )


        output.append(
            str(
                draw_neon_section(
                    "أصغر قليلاً",
                    compatible.get("minus", []),
                    "#e67e22",
                    "🟠",
                    "minus"
                )
            )
        )


    else:


        output.append(
            str(
                draw_warning_card(
                    f"الموديل {phone} غير موجود"
                )
            )
        )


    return "\n".join(output)
