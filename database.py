import json

def load_db():
    try:
        with open('models_db.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # التأكد من وجود البيانات الأساسية فقط
            if "compatible_models" not in data:
                data["compatible_models"] = []
            return data
    except FileNotFoundError:
        return {"compatible_models": []}

def save_db(data):
    # إنشاء نسخة نظيفة من البيانات لا تحتوي على "system_notifications"
    clean_data = {
        "compatible_models": data.get("compatible_models", [])
    }
    
    # الكتابة للملف وتخزينه بصيغة نظيفة
    with open('models_db.json', 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)

def add_notification(message):
    # هذه الدالة أصبحت فارغة لضمان عدم إضافة أي رسائل خطأ للملف
    pass
