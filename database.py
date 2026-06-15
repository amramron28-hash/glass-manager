import os
from supabase import create_client

# 🔒 الاتصال الآمن بالسحابة
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# ✔ إضافة هاتف جديد إلى السحابة
# ==========================================
def add_model(size, panel, sensor, model):
    if not all([size, panel, sensor, model]):
        return False
    try:
        # قمنا بتأمين كتابة الاسم لإرساله للعمودين المتوقعين لضمان التعرف عليه
        supabase.table("phones").insert({
            "size": str(size).strip(),
            "panel": str(panel).strip(),
            "sensor": str(sensor).strip(),
            "model_name": str(model).strip(),
            "model": str(model).strip()
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
            
            # محاولة قراءة الحقل بأي سبلنج متوقع (model_name أو model أو اسم_النموذج)
            model = r.get("model_name") or r.get("model") or r.get("اسم_النموذج") or ""
            model = str(model).strip()

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
    try:
        if cleaned_db:
            for size, panels in cleaned_db.items():
                for panel, sensors in panels.items():
                    for sensor, data in sensors.items():
                        for model in data.get("models", []):
                            add_model(size, panel, sensor, model)
        return True
    except Exception:
        return False
