# database.py - النسخة الاحترافية المتكاملة والمحدثة لـ ZEGAAR AMMAR

import os
import requests
import json
import threading
from fuzzywuzzy import process

# جلب رابط قاعدة البيانات السحابية من بيئة عمل خوادم Hugging Face
NPOINT_API_URL = os.environ.get("NPOINT_URL")
DB_FILE = "models_db.json"

def load_db():
    """تحميل قاعدة البيانات من الرابط السحابي npoint، أو محلياً في حال انقطاع الاتصال"""
    try:
        if NPOINT_API_URL:
            res = requests.get(NPOINT_API_URL, timeout=5)
            if res.status_code == 200: 
                return res.json()
    except: 
        pass
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    return {}

def save_db(data):
    """حفظ البيانات وتزامنها فورياً على السحاب npoint ومحلياً لضمان عدم ضياع فهارس عمار"""
    if NPOINT_API_URL:
        try: 
            requests.put(NPOINT_API_URL, data=json.dumps(data), headers={"Content-Type": "application/json"}, timeout=5)
        except: 
            pass
    with open(DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_models(data):
    """استخراج مصفى وقاطع لجميع الأجهزة بدون أي تكرار وتصفيفها أبجدياً"""
    all_models = []
    for sz, scs in data.items():
        if sz == "system_notifications": 
            continue
        for sc, sns in scs.items():
            for sn, info in sns.items():
                if isinstance(info, list): 
                    all_models.extend(info)
    return sorted(list(set(all_models)))

def google_prefix_search(search_term, all_models_list):
    """محاكاة ذكية لبحث جوجل الفوري بالاعتماد على خوارزمية Fuzzy التقريبية السريعة"""
    if not search_term or str(search_term).strip() == "": 
        return []
    clean_term = str(search_term).strip().lower()
    matches = process.extract(clean_term, all_models_list, limit=8)
    result = []
    if matches:
        for match in matches: 
            result.append(match[0] if isinstance(match, tuple) else match)
    return result
# تابع للملف البرمجي database.py مباشرة بعد سطر دالة البحث

def get_compatible_sizes(db_data, base_size_str, mode="search"):
    """حساب النطاق الفيزيائي المطاطي للتوافق بمقدار 0.03 إنش للأجهزة المقاربة"""
    try: 
        base_val = float(base_size_str)
    except: 
        return [base_size_str]
        
    compatible = []
    for sz in db_data.keys():
        if sz == "system_notifications": 
            continue
        try:
            curr_val = float(sz)
            diff = round(abs(curr_val - base_val), 2)
            if diff <= 0.03: 
                compatible.append(sz)
        except:
            if str(sz) == str(base_size_str): 
                compatible.append(sz)
    return compatible if compatible else [base_size_str]

def get_notifications(): 
    """جلب تنبيهات النظام الصامتة لعرضها في جرس اللوحة الجانبية للتطبيق"""
    return load_db().get("system_notifications", [])

def add_notification(text):
    """حقن إشعار صامت جديد في اللوحة الجانبية مع تحديد سقف الإشعارات بـ 30 تنبيهاً"""
    db_data = load_db()
    if "system_notifications" not in db_data: 
        db_data["system_notifications"] = []
    db_data["system_notifications"].insert(0, text)
    db_data["system_notifications"] = db_data["system_notifications"][:30]
    save_db(db_data)

def clear_notifications(): 
    """تفريغ وتنظيف جرس التنبيهات من لوحة عمار الجانبية"""
    db_data = load_db()
    db_data["system_notifications"] = []
    save_db(db_data)

def _async_internet_checker_worker(phone_name, current_size, current_screen, current_sensor):
    """خادم الفحص الخلفي المتصل بالإنترنت للتصحيح التلقائي لمقاسات الشاشات الجديدة ونقلها"""
    try:
        url = f"https://open-specs-api.com{phone_name}"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            api_data = res.json()
            if api_data and "results" in api_data and len(api_data["results"]) > 0:
                best_match = api_data["results"][0]
                true_size_float = float(best_match.get("screen_size_inch", 0))
                if true_size_float > 0:
                    true_size_str = str(true_size_float)
                    if true_size_str != str(current_size).strip():
                        db_data = load_db()
                        if current_size in db_data and current_screen in db_data[current_size] and current_sensor in db_data[current_size][current_screen]:
                            if phone_name in db_data[current_size][current_screen][current_sensor]: 
                                db_data[current_size][current_screen][current_sensor].remove(phone_name)
                        
                        db_data.setdefault(true_size_str, {}).setdefault(current_screen, {}).setdefault(current_sensor, [])
                        if phone_name not in db_data[true_size_str][current_screen][current_sensor]: 
                            db_data[true_size_str][current_screen][current_sensor].append(phone_name)
                        
                        save_db(db_data)
                        add_notification(f"🔄 ضبط تلقائي: تم نقل [{phone_name}] إلى مقاس {true_size_str}")
    except: 
        pass

def trigger_silent_validation(phone_name, current_size, current_screen, current_sensor):
    """إطلاق الـ Thread الصامت في الخلفية لفحص الهاتف دون التسبب في ثقل أو تجميد التطبيق"""
    threading.Thread(target=_async_internet_checker_worker, args=(phone_name.strip(), current_size, current_screen, current_sensor), daemon=True).start()
