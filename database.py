import os
import json
from supabase import create_client, Client
from core.logger import get_logger

log = get_logger("database")

# =========================
# SUPABASE CONFIGURATION
# =========================
# يفضل استخدام متغيرات البيئة للأمان
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mgmphimlcdchtbiyhhbt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX")

# إنشاء عميل Supabase الرسمي
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    log.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

# =========================
# DATA LOADING (STRUCTURED)
# =========================
def load_db():
    """
    تحميل قاعدة البيانات من Supabase وتحويلها لهيكلية متداخلة:
    size -> panel -> sensor -> {"models": [...]}
    هذه الهيكلية ضرورية لسرعة البحث في logic_engine
    """
    if not supabase:
        return {}

    try:
        # جلب كل البيانات من جدول phones
        res = supabase.table("phones").select("*").execute()
        rows = res.data or []
        
        db_structure = {}
        total_models = 0

        for row in rows:
            size = str(row.get("size", "")).strip()
            panel = str(row.get("panel", "Notch Screen")).strip()
            sensor = str(row.get("sensor", "hardware_top_sensor")).strip()
            model = str(row.get("model_name") or row.get("model", "")).strip()

            if not size or not model:
                continue

            # بناء الهيكل المتداخل
            db_structure.setdefault(size, {})
            db_structure[size].setdefault(panel, {})
            db_structure[size][panel].setdefault(sensor, {"models": []})

            if model not in db_structure[size][panel][sensor]["models"]:
                db_structure[size][panel][sensor]["models"].append(model)
                total_models += 1

        log.info(f"Loaded database with {total_models} models from Supabase")
        return db_structure

    except Exception as e:
        log.error(f"Error loading database structure: {e}")
        return {}

# =========================
# DATA SAVING & ADDING
# =========================
def add_model(size, panel, sensor, model):
    """إضافة موديل جديد إلى جدول phones في Supabase"""
    if not supabase:
        return False

    try:
        payload = {
            "size": str(size).strip(),
            "panel": str(panel).strip(),
            "sensor": str(sensor).strip(),
            "model_name": str(model).strip()
        }

        if not all(payload.values()):
            return False

        res = supabase.table("phones").insert(payload).execute()
        
        if res.data:
            log.info(f"Model added successfully: {payload['model_name']}")
            return True
        return False

    except Exception as e:
        log.error(f"Error adding model: {e}")
        return False

def delete_model(model, size, panel, sensor):
    """حذف موديل محدد بمواصفاته بالضبط (يُستخدم لتصحيح الأخطاء/التكرارات)"""
    if not supabase:
        return False

    try:
        supabase.table("phones") \
            .delete() \
            .eq("model_name", str(model).strip()) \
            .eq("size", str(size).strip()) \
            .eq("panel", str(panel).strip()) \
            .eq("sensor", str(sensor).strip()) \
            .execute()

        log.info(f"Model deleted: {model} ({size}/{panel}/{sensor})")
        return True

    except Exception as e:
        log.error(f"Error deleting model: {e}")
        return False

def save_db(data=None, new_phone_name=None, size=None, panel=None, sensor=None):
    """
    دالة متوافقة مع الإصدارات القديمة والمنطق السابق.
    إذا تم تمرير بيانات جديدة، تقوم بإضافتها.
    """
    if new_phone_name and size and panel and sensor:
        return add_model(size, panel, sensor, new_phone_name)
    
    # في حالة Supabase، لا نحتاج لحفظ هيكل كامل لأن كل تعديل يتم عبر insert/delete مباشر
    return True

def add_notification(message, level="info"):
    """دالة وهمية للتوافق مع الكود القديم، يمكن ربطها لاحقاً بجدول notifications"""
    pass
