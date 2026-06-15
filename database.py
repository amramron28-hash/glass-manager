import os
from supabase import create_client

# 🔒 الاتصال السحابي الصريح والمستقر لكسر حاجز الصفر والانهيار
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX"

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
            "model_name": str(model).strip()
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
            model = str(r.get("model_name") or r.get("model") or "").strip()

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

def save_db(cleaned_db=None):
    return True
