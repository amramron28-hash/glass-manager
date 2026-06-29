import os
from core.logger import get_logger
from database import load_db

log = get_logger("sync_index")
INDEX_FILE = "models_index.txt"

def sync_old_models_to_index():
    """
    مزامنة الأسماء القديمة وضخها في ملف المؤشر النصي.
    يتم استخدام logger بدلاً من print لضمان التوحيد.
    """
    log.info("⏳ جاري بدء مزامنة الأسماء القديمة وضخها في ملف المؤشر...")
    
    # تحميل قاعدة البيانات السحابية الحالية
    try:
        db_data = load_db()
    except Exception as e:
        log.error(f"❌ تعذر تحميل قاعدة البيانات: {e}")
        return

    extracted_names = []

    # تفكيك هيكل قاعدة البيانات (المقاس -> الشاشة -> المستشعر -> الموديلات)
    for size, panels in db_data.items():
        if not isinstance(panels, dict): continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict): continue
            for sensor, s_data in sensors.items():
                # ✅ تم تصحيح مفتاح "models " ليصبح "models"
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                
                if not isinstance(models_list, list): continue
                
                for m in models_list:
                    if isinstance(m, str) and m.strip():
                        extracted_names.append(m.strip())

    # إزالة التكرار وترتيب الأسماء أبجدياً
    unique_names = sorted(list(set(extracted_names)))

    if not unique_names:
        log.warning("⚠️ لم يتم العثور على أي هواتف مسجلة مسبقاً في قاعدة البيانات الحالية.")
        return

    # ✅ تم تصحيح معاملات open لإزالة المسافات الزائدة
    try:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            for name in unique_names:
                f.write(f"{name}\n")
        
        log.info(f"✅ تمت المزامنة بنجاح! تم ضخ إجمالي ({len(unique_names)}) هاتف قديم داخل ملف {INDEX_FILE}")
        
    except OSError as e:
        log.error(f"❌ فشل في كتابة ملف المؤشر: {e}")

if __name__ == "__main__":
    sync_old_models_to_index()
