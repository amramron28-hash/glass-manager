import json
import os
import shutil

DB_FILE = "models_db.json"
BACKUP_FILE = "models_db_backup.json"

def load_db():
    """
    قراءة قاعدة البيانات بأمان كلي. 
    في حال تلف الملف الرئيسي، يقوم النظام تلقائياً باسترجاع آخر نسخة احتياطية سليمة.
    """
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        # 🛡️ عين المراقب الصامت: الملف الرئيسي غائب أو فارغ، نبحث عن النسخة الاحتياطية
        if os.path.exists(BACKUP_FILE) and os.path.getsize(BACKUP_FILE) > 0:
            shutil.copy(BACKUP_FILE, DB_FILE)
        else:
            # إذا لم يوجد أي ملف مسبقاً، ننشئ قاموساً فارغاً لإقلاع السيستم
            return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, TypeError):
        # 🛡️ أذن المراقب الصامت: الملف الرئيسي معطوب، نقوم بالإنقاذ الفوري عبر الاحتياطي
        if os.path.exists(BACKUP_FILE) and os.path.getsize(BACKUP_FILE) > 0:
            shutil.copy(BACKUP_FILE, DB_FILE)
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

def save_db(data):
    """
    دالة الحماية والنسخ الاحتياطي التلقائي الصامت (صمام أمان Glass Manager):
    تأخذ نسخة احتياطية فورية قبل الكتابة، وتمنع حفظ أي ملفات فارغة أو معطوبة كلياً.
    """
    if not data:
        return False

    try:
        # 1. صناعة نسخة احتياطية فورية (Shadow Backup) من الملف الحالي السليم قبل لمسه
        if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
            shutil.copy(DB_FILE, BACKUP_FILE)

        # 2. الكتابة الآمنة داخل ملف مؤقت أولاً للتأكد من عدم حدوث انقطاع طاقة أو انهيار
        temp_file = "db_temp.json"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # 3. حماية الـ Zero-Byte: التحقق من أن الملف الجديد يحتوي على بيانات وليس فارغاً
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            # استبدال الملف المؤقت بالملف الرئيسي رسمياً بنجاح كلي
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            os.rename(temp_file, DB_FILE)
            return True
        else:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False

    except Exception:
        # في حال حدوث أي خلل عشوائي أثناء الكتابة، يتم إلغاء العملية لحماية شجرة البيانات
        if os.path.exists("db_temp.json"):
            os.remove("db_temp.json")
        return False
