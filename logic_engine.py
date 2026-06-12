Enterimport re

def normalize_text(text):
    """ تنظيف وتوحيد نصوص الهواتف لضمان دقة المطابقة ومنع التكرار بسبب المسافات أو الحروف الكبيرة """
    if not text:
        return ""
    # تحويل النص إلى حروف صغيرة، مسح المسافات الزائدة، وتوحيد الفواصل
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def find_model_coords(db_data, target_model):
    """ 
    [الخطة أ]: البحث العميق في شجرة الـ JSON للعثور على إحداثيات الهاتف المستهدف.
    تُرجع: (المقاس، نوع الشاشة، نوع المستشعر، الاسم الرسمي الصحيح)
    """
    if not target_model or not db_data:
        return None, None, None, None
        
    target_norm = normalize_text(target_model)
    data_cluster = db_data.get("data", db_data) # حماية مرنة لقراءة البيانات سواء كانت مغلفة أو مباشرة

    if isinstance(data_cluster, dict):
        for size, screens in data_cluster.items():
            if size in ["metadata", "status", "last_updated", "notifications"]: continue
            if isinstance(screens, dict):
                for panel, sensors in screens.items():
                    if isinstance(sensors, dict):
                        for sensor, models in sensors.items():
                            if isinstance(models, list):
                                for model in models:
                                    if normalize_text(model) == target_norm:
                                        return size, panel, sensor, model
    return None, None, None, None

def get_compatibles_strict(db_data, target_model):
    """
    المحرك الصارم لفرز وفرز مجموعات التوافق الثلاثية (Exact, Plus, Minus)
    مع عزل الهواتف التي تمتلك نفس المقاس ولكن بمستشعر مختلف تماماً (Warn)
    """
    results = {
        "current_model": {"size": "غير معروف", "panel": "غير معروف", "sensor": "غير معروف"},
        "exact": [], "plus": [], "minus": [], "warn": []
    }
    
    size_str, panel, sensor, real_name = find_model_coords(db_data, target_model)
    if not size_str:
        return results
        
    results["current_model"] = {"size": size_str, "panel": panel, "sensor": sensor}
    
    try:
        target_size = float(size_str)
    except ValueError:
        return results

    data_cluster = db_data.get("data", db_data)
    
    if isinstance(data_cluster, dict):
        for size_key, screens in data_cluster.items():
            if size_key in ["metadata", "status", "last_updated", "notifications"]: continue
            try:
                current_size = float(size_key)
            except ValueError:
                continue
                
            # حساب التباين الرقمي الدقيق للمقاسات السحابية
            diff = round(current_size - target_size, 2)
            
            # فحص المقاسات المتوافقة ضمن النطاق المسموح به (-0.03 إلى +0.03)
            if -0.03 <= diff <= 0.03:
                if isinstance(screens, dict) and panel in screens:
                    sensors_dict = screens[panel]
                    if isinstance(sensors_dict, dict):
                        for s_name, models in sensors_dict.items():
                            if isinstance(models, list):
                                for m in models:
                                    # عزل الهواتف ذات المستشعرات المختلفة لمنع اختلاط الألوان والأخطاء الحساسة
                                    if s_name != sensor and diff == 0.00:
                                        if m not in results["warn"]:
                                            results["warn"].append(m)
                                    elif s_name == sensor:
                                        if diff == 0.00:
                                            results["exact"].append(m)
                                        elif 0.00 < diff <= 0.03:
                                            results["plus"].append(m)
                                        elif -0.03 <= diff < 0.00:
                                            results["minus"].append(m)
                                            
    return results

def check_existing_size_group(db_data, new_size, new_panel):
    """
    [الخطة ب]: فحص تقاطعي فوري لمعرفة ما إذا كان مقاس الهاتف الجديد المكتشف للزبون
    يمتلك عائلة أو مجموعة مقاسات وشاشات متطابقة مسجلة مسبقاً في السيستم لتوفير بدائل حماية فورية.
    """
    if not new_size or not new_panel or not db_data:
        return []
        
    size_norm = new_size.strip()
    data_cluster = db_data.get("data", db_data)
    models_found = []
    
    if isinstance(data_cluster, dict) and size_norm in data_cluster:
        screens = data_cluster[size_norm]
        if isinstance(screens, dict) and new_panel in screens:
            sensors_dict = screens[new_panel]
            if isinstance(sensors_dict, dict):
                for sensor_name, models in sensors_dict.items():
                    if isinstance(models, list):
                        models_found.extend(models)
                        
    return sorted(list(set(models_found)))
