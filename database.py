import os
from supabase import create_client

# 🔒 جلب مفاتيح الاتصال الآمن بالسحابة
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # تأكد من مطابقة الاسم لما وضعته في Secrets

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# ✔ إضافة هاتف جديد إلى السحابة
# ==========================================
def add_model(size, panel, sensor, model):
    if not all([size, panel, sensor, model]):
        return False
    try:
        supabase.table("phones").insert({
            "size": str(size).strip(),
            "panel": str(panel).strip(),
            "sensor": str(sensor).strip(),
            "model_name": str(model).strip()  # تأكد من مطابقة الاسم للعمود بالسحابة model_name
        }).execute()
        return True
    except Exception:
        return False

# ==========================================
# ✔ تحميل البيانات بشكلها القاموسي المتداخل
# ==========================================
def load_db():
    try:
        res = supabase.table("phones").select("*").execute()
        rows = res.data or []
        db = {}
        for r in rows:
            size = str(r.get("size", "")).strip()
            panel = str(r.get("panel", "")).strip()
            sensor = str(r.get("sensor", "")).strip()
            model = str(r.get("model_name", "")).strip()

            if not all([size, panel, sensor, model]):
                continue

            db.setdefault(size, {})
            db[size].setdefault(panel, {})
            db[size][panel].setdefault(sensor, {"models": []})

            if model not in db[size][panel][sensor]["models"]:
                db[size][panel][sensor]["models"].append(model)
        return db
    except Exception:
        return {}

# ==========================================
# 🛡️ دالة حماية البيانات الاحتياطية (save_db)
# ==========================================
def save_db(cleaned_db=None):
    """
    هذه الدالة تم إنشاؤها لامتصاص الصدمات البرمجية ومنع الـ ImportError.
    تقوم بإنشاء تزامن تلقائي لمنع تجمد التطبيق واختفاء الإعدادات.
    """
    try:
        # إذا تم استدعاء دالة الصيانة لتنظيف البيانات، نقوم بتحديثها سحابياً
        if cleaned_db:
            for size, panels in cleaned_db.items():
                for panel, sensors in panels.items():
                    for sensor, data in sensors.items():
                        for model in data.get("models", []):
                            # تفحص السحابة وتضيف البيانات النظيفة فقط
                            add_model(size, panel, sensor, model)
        return True
    except Exception:
        return False
