# sync_index.py
import json
import os
from database import load_db

INDEX_FILE = "models_index.txt"

def sync_old_models_to_index():
    print("⏳ جاري بدء مزامنة الأسماء القديمة وضخها في ملف المؤشر...")
    
    # تحميل قاعدة البيانات السحابية الحالية
    try:
        db_data = load_db()
    except Exception as e:
        print(f"❌ تعذر تحميل قاعدة البيانات: {e}")
        return

    extracted_names = []

    # تفكيك هيكل قاعدة البيانات (المقاس -> الشاشة -> المستشعر -> الموديلات)
    for size, panels in db_data.items():
        for panel, sensors in panels.items():
            for sensor, s_data in sensors.items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                for m in models_list:
                    if m.strip():
                        extracted_names.append(m.strip())

    # إزالة التكرار وترتيب الأسماء أبجدياً
    unique_names = sorted(list(set(extracted_names)))

    if not unique_names:
        print("⚠️ لم يتم العثور على أي هواتف مسجلة مسبقاً في قاعدة البيانات الحالية.")
        return

    # فتح وضخ كافة الأسماء داخل ملف المؤشر النصي (كل اسم في سطر)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        for name in unique_names:
            f.write(f"{name}\n")

    print(f"✅ تمت المزامنة بنجاح! تم ضخ إجمالي ({len(unique_names)}) هاتف قديم داخل ملف {INDEX_FILE} وهو جاهز للعمل الفوري.")

if __name__ == "__main__":
    sync_old_models_to_index()

