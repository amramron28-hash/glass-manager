import re

def normalize_text(text):
    """
    تنظيف وتوحيد النصوص بحذر شديد:
    إزالة المسافات الزائدة، الشرطات، وتحويل الحروف لصغيرة لضمان المطابقة المرنة الذكية.
    """
    if not text:
        return ""
    cleaned = text.lower().strip()
    cleaned = re.sub(re.compile(r'[-_/ \s]+'), ' ', cleaned)
    return cleaned.strip()

def filter_models_live(db_data, search_term):
    """
    فلترة الموديلات حياً من الذاكرة بناءً على الحروف المكتوبة مع دعم التقارب الذكي.
    متوافق تماماً مع الهيكل الحقيقي للقاموس المباشر.
    """
    if not search_term:
        return []
    
    normalized_search = normalize_text(search_term)
    matched_models = []
    
    for size_key, panels in db_data.items():
        for panel_key, sensors in panels.items():
            for sensor_key, sensor_data in sensors.items():
                # استخراج القائمة بشكل آمن سواء كانت قاموساً يحتوي على "models" أو قائمة مباشرة
                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data
                for model in models_list:
                    if normalized_search in normalize_text(model):
                        matched_models.append(model)
                            
    return sorted(list(set(matched_models)))

def find_model_coords(db_data, model_name):
    """
    البحث الحذر عن موقع الهاتف داخل شجرة البيانات وإرجاع إحداثياته الحقيقية.
    يمنع تخطي الخطة أ من خلال قراءة الهيكل الجديد بدقة.
    """
    if not model_name:
        return None, None, None, None
        
    normalized_target = normalize_text(model_name)
    
    for size_str, panels in db_data.items():
        for panel_name, sensors in panels.items():
            for sensor_name, sensor_data in sensors.items():
                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data
                for m in models_list:
                    if normalize_text(m) == normalized_target:
                        return size_str, panel_name, sensor_name, m
                            
    return None, None, None, None

def get_compatibles_strict(db_data, model_name):
    """
    محرك التوجيه الصارم لحساب التوافقات بناءً على المقاس الحقيقي (Exact / Plus / Minus)
    مع عزل الهواتف ذات الحساس المختلف في قائمة الـ warn وتحذير الفني.
    """
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
    current_size = float(size_str)
    
    for size_key, panels in db_data.items():
        try:
            target_size = float(size_key)
        except ValueError:
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
                        
                    if diff == 0.00:
                        if sensor_key == sensor:
                            results["exact"].append(m)
                        else:
                            results["warn"].append(m)
                    elif 0.01 <= diff <= 0.03:
                        if sensor_key == sensor:
                            results["plus"].append(m)
                        else:
                            results["warn"].append(m)
                    elif -0.03 <= diff <= -0.01:
                        if sensor_key == sensor:
                            results["minus"].append(m)
                        else:
                            results["warn"].append(m)
                            
    results["exact"] = sorted(list(set(results["exact"])))
    results["plus"] = sorted(list(set(results["plus"])))
    results["minus"] = sorted(list(set(results["minus"])))
    results["warn"] = sorted(list(set(results["warn"])))
    
    return results

def check_existing_size_group(db_data, size_str, panel_name):
    """
    التحقق من وجود مجموعة مقاسات متطابقة مسبقاً في الـ RAM لإجراء [الحالة ب].
    """
    matched_models = []
    size_str = str(size_str).strip()
    if size_str in db_data:
        if panel_name in db_data[size_str]:
            for sensor_key, sensor_data in db_data[size_str][panel_name].items():
                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data
                matched_models.extend(models_list)
    return sorted(list(set(matched_models)))

def run_intelligent_inspector(db_data):
    """
    🎯 المراقب الصامت الذكي والنشط (عينك ويدك داخل التطبيق):
    يقوم بفحص شامل وصيانة لقاعدة البيانات تلقائياً، ينظف الأسماء،
    يزيل التكرار المتشابه، ويرتب شجرة البيانات لرفع سرعة الاستجابة اللحظية.
    """
    cleaned_db = {}
    changes_made = False
    
    for size_key, panels in db_data.items():
        cleaned_size = size_key.strip()
        if cleaned_size not in cleaned_db:
            cleaned_db[cleaned_size] = {}
            
        for panel_key, sensors in panels.items():
            cleaned_panel = panel_key.strip()
            if cleaned_panel not in cleaned_db[cleaned_size]:
                cleaned_db[cleaned_size][cleaned_panel] = {}
                
            for sensor_key, sensor_data in sensors.items():
                cleaned_sensor = sensor_key.strip()
                
                models_list = sensor_data.get("models", []) if isinstance(sensor_data, dict) else sensor_data
                
                seen_normalized = {}
                unique_models = []
                
                for m in models_list:
                    cleaned_name = " ".join(m.split())
                    norm_name = normalize_text(cleaned_name)
                    
                    if norm_name and norm_name not in seen_normalized:
                        seen_normalized[norm_name] = cleaned_name
                        unique_models.append(cleaned_name)
                    else:
                        changes_made = True
                
                if len(unique_models) != len(models_list):
                    changes_made = True
                    
                cleaned_db[cleaned_size][cleaned_panel][cleaned_sensor] = {"models": sorted(unique_models)}
                
    return cleaned_db, changes_made
