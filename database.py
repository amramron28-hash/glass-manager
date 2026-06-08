import json

def load_db():
    try:
        with open('models_db.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"compatible_models": []} # حقل فارغ ونظيف

def save_db(data):
    # نضمن أن الملف يحتوي فقط على البيانات الحقيقية دون أي تنبيهات
    clean_data = {
        "compatible_models": data.get("compatible_models", [])
    }
    with open('models_db.json', 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)

def add_notification(message):
    pass # لا تفعل شيئاً، هذا يمنع ظهور رسائل الخطأ في تطبيقك
