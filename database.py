import json
import os

DB_FILE = 'models_db.json'

def load_db():
    """
    تحميل البيانات مع الحفاظ على هيكل الـ JSON الحالي (metadata, data)
    """
    if not os.path.exists(DB_FILE):
        return {"metadata": {"version": 1}, "data": {}}
        
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"metadata": {"version": 1}, "data": {}}

def save_db(data):
    """
    حفظ البيانات كما هي دون حذف مفاتيح أساسية
    """
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_notification(message):
    # إذا كنت تريد تفعيل الإشعارات لاحقاً، يمكننا إضافتها هنا
    # ولكن حالياً نتركها فارغة كما طلبت
    pass
