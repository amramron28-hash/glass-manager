import json

def load_db():
    try:
        with open('models_db.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"compatible_models": [], "system_notifications": []}

def save_db(data):
    # مسح أي تنبيهات قديمة لضمان نظافة الملف
    data["system_notifications"] = [] 
    with open('models_db.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_notification(message):
    # دالة فارغة لإرضاء السكربت ومنع خطأ الاستيراد
    pass
