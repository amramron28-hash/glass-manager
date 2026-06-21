import os
import requests
import re
from html import escape
from database import load_db, save_db

def extract_numeric_size(size_string):
    """دالة مساعدة لاستخراج الأرقام العشرية من النصوص البرمجية للمقاسات"""
    try:
        match = re.search(r"[-+]?\d*\.\d+|\d+", size_string)
        if match:
            return float(match.group())
    except Exception:
        pass
    return None

def find_model_coords(db_data, phone_name):
    """البحث في قاعدة البيانات عن قياسات وأبعاد الهاتف المستهدف الذكي"""
    if not phone_name or not db_data:
        return None, None, None, None
        
    phone_name_clean = phone_name.strip().lower()
    
    # 1. محاولة المطابقة التامة بغض النظر عن حالة الأحرف الكبيرة أو الصغيرة
    for size_str, panels in db_data.items():
        for panel, sensors in (panels.items() if isinstance(panels, dict) else []):
            for sensor, s_data in (sensors.items() if isinstance(sensors, dict) else []):
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if isinstance(models_list, list):
                    for m in models_list:
                        if m.strip().lower() == phone_name_clean:
                            return size_str, panel, sensor, m

    # 2. محاولة المطابقة الجزئية الاحتياطية لمرونة عمليات البحث الصامتة
    for size_str, panels in db_data.items():
        for panel, sensors in (panels.items() if isinstance(panels, dict) else []):
            for sensor, s_data in (sensors.items() if isinstance(sensors, dict) else []):
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if isinstance(models_list, list):
                    for model in models_list:
                        if phone_name_clean in model.strip().lower():
                            return size_str, panel, sensor, model
                            
    return None, None, None, None

def get_compatibles_strict(db_data, phone_name):
    """تحديد الهواتف البديلة والمتوافقة عبر 3 مستويات دقيقة بحد تفاوت 0.03 الصارم"""
    compatibles = {"exact": [], "plus": [], "minus": []}
    
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone_name)
    if not size_str:
        return compatibles

    current_size = extract_numeric_size(size_str)
    if current_size is None:
        return compatibles

    # 🎯 الضبط الصارم والمطلوب لنسبة التسامح بدقة متناهية لمنع زيادة النطاق
    TOLERANCE = 0.03 

    for size_key, panels in db_data.items():
        loop_size = extract_numeric_size(size_key)
        if loop_size is None: 
            continue
            
        size_diff = loop_size - current_size
        
        for panel_key, sensors in (panels.items() if isinstance(panels, dict) else []):
            if panel_key != panel: 
                continue
                
            for sensor_key, s_data in (sensors.items() if isinstance(sensors, dict) else []):
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if isinstance(models_list, list):
                    for model in models_list:
                        if real_name and model.lower() == real_name.lower(): 
                            continue
                            
                        if abs(size_diff) < 0.001 and sensor_key == sensor:
                            if model not in compatibles["exact"]: 
                                compatibles["exact"].append(model)
                        elif 0 < size_diff <= TOLERANCE:
                            if model not in compatibles["plus"]: 
                                compatibles["plus"].append(model)
                        elif -TOLERANCE <= size_diff < 0:
                            if model not in compatibles["minus"]: 
                                compatibles["minus"].append(model)

    return compatibles

def local_check_existing_size_group(db, target_size, target_panel):
    matched_models = []
    if target_size in db and target_panel in db[target_size]:
        for sensor, s_data in db[target_size][target_panel].items():
            models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
            for m in models_list:
                matched_models.append(m)
    return matched_models

def ai_background_global_verify(phone_name):
    try:
        # 🌐 تصحيح الرابط بإضافة الشرطة المائلة لحماية الاتصال بالـ API
        url = f"https://vercel.app{requests.utils.quote(phone_name)}"
        res = requests.get(url, timeout=2.0).json()
        if res and "specs" in res:
            return {
                "size": str(res["specs"].get("display_size", "غير مدرج")),
                "panel": str(res["specs"].get("display_type", "غير مدرج")),
                "sensor": str(res["specs"].get("proximity_type", "غير مدرج"))
            }
    except:
        pass
    return None

def run_system_workflows(phone, db_data, suggestions):
    """المحرك المركزي المصحح المسافات البادئة لربط الحسابات السحابية والخطط الثلاث"""
    from ui_components import draw_technical_coords, draw_neon_section

    if not phone or not phone.strip():
        return ""

    size_str, panel, sensor, real_name = find_model_coords(db_data, phone)
    
    # معيار التحقق الآمن لضمان التطابق الفعلي التام في قاعدة البيانات
    is_exact_match = True if real_name and phone.strip().lower() == real_name.strip().lower() else False
    
    html_output = []

    # 🟢 الخطة 1: وجود تطابق تام في قاعدة البيانات
    if is_exact_match:
        coords_html = draw_technical_coords(size_str, panel, sensor, real_name)
        if coords_html:
            html_output.append(str(coords_html))
            
        compatibles_dict = get_compatibles_strict(db_data, phone)
        all_compatibles = []
        if compatibles_dict:
            all_compatibles.extend(compatibles_dict.get("exact", []))
            all_compatibles.extend(compatibles_dict.get("plus", []))
            all_compatibles.extend(compatibles_dict.get("minus", []))
            
        compat_html = draw_neon_section(all_compatibles)
        if compat_html:
            html_output.append(str(compat_html))
            
    # 🟡 الخطة 2 & 3: تفعيل المعالجة الفورية والآمنة لعدم المطابقة التامة
    else:
        # الخطة 2: كارت نيون زجاجي أزرق فاخر لمعالجة الـ API
        html_output.append(f"""
            <div style="font-size: 20px !important; font-weight: bold !important; color: #ffffff !important; margin-top: 25px !important; margin-bottom: 12px !important; text-align: right !important; direction: rtl !important;">
                <span style="color:#00bfff; margin-left: 6px;">🔍</span>حالة معالجة وفحص الموديل:
            </div>
            <div class="ammar-flat-card" style="background: linear-gradient(135deg, #0b1a33, #060e1c) !important; border: 2px solid #00bfff !important; padding: 16px 20px !important; margin-bottom: 14px !important; border-radius: 12px !important; display: flex !important; align-items: center !important; justify-content: space-between !important; direction: ltr !important; width: 100% !important; box-shadow: 0px 4px 12px rgba(0, 191, 255, 0.25) !important; box-sizing: border-box !important;">
                <div style="color: #ffffff !important; font-size: 21px !important; font-weight: 800 !important; text-align: left !important; margin: 0 !important;">جاري معالجة ومطابقة: {escape(phone)}</div>
            </div>
        """)
        
        ai_result = ai_background_global_verify(phone)
        if ai_result:
            # نتائج الفحص العالمي في كارت نيون فيروزي فخم ومستقل تماماً
            html_output.append(f"""
                <div class="ammar-flat-card" style="background: linear-gradient(135deg, #071f21, #030f10) !important; border: 2px solid #00ffcc !important; padding: 16px 20px !important; margin-bottom: 14px !important; border-radius: 12px !important; display: flex !important; align-items: center !important; justify-content: space-between !important; direction: ltr !important; width: 100% !important; box-shadow: 0px 4px 12px rgba(0, 255, 204, 0.25) !important; box-sizing: border-box !important;">
                    <div style="color: #00ffcc !important; font-size: 19px !important; font-weight: 800 !important; text-align: left !important; direction: rtl !important; width:100%;">
                        🤖 <b>نتائج الفحص العالمي الذكي:</b><br>
                        📏 الحجم المتوقع: {escape(ai_result['size'])} | 📺 الشاشة: {escape(ai_result['panel'])} | 🔌 الحساس: {escape(ai_result['sensor'])}
                    </div>
                </div>
            """)
        else:
            # الخطة 3 (خطة الطوارئ): كارت نيون برتقالي مضيء منفصل في حال عدم استجابة الـ API أو غياب البيانات
            html_output.append(f"""
                <div style="font-size: 20px !important; font-weight: bold !important; color: #ffffff !important; margin-top: 25px !important; margin-bottom: 12px !important; text-align: right !important; direction: rtl !important;">
                    <span style="color:#ff4500; margin-left: 6px;">⚠️</span>تنبيه النظام الموحد لعدم الإدراج:
                </div>
                <div class="flat-warning-card" style="background: linear-gradient(135deg, #26090b, #120405) !important; border: 2px solid #ff4500 !important; padding: 16px 20px !important; margin-bottom: 14px !important; border-radius: 12px !important; display: flex !important; align-items: center !important; justify-content: space-between !important; direction: rtl !important; width: 100% !important; box-shadow: 0px 4px 12px rgba(255, 69, 0, 0.3) !important; box-sizing: border-box !important;">
                    <div style="color: #ffb3b9 !important; font-size: 20px !important; font-weight: 700 !important; text-align: right !important; line-height: 1.5; width:100%;">
                        الموديل غير مدرج حالياً. يمكنك استخدام نموذج الإدخال اليدوي بأسفل لوحة التحكم لتوثيقه وضخه في قاعدة بيانات النظام.
                    </div>
