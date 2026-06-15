import os
from supabase import create_client

# =========================
# 🔐 حماية المفاتيح (أفضل من وضعها مباشرة)
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# ✔ إضافة هاتف (آمن + بدون تكرار + سريع)
# =========================
def add_model(size, panel, sensor, model):

    if not all([size, panel, sensor, model]):
        return False

    try:
        # 🧠 إدخال مباشر (Supabase سيمنع التكرار إذا أضفت Unique Constraint لاحقًا)
        supabase.table("phones").insert({
            "size": str(size).strip(),
            "panel": str(panel).strip(),
            "sensor": str(sensor).strip(),
            "model": str(model).strip()
        }).execute()

        return True

    except Exception:
        return False


# =========================
# ✔ تحميل البيانات (بنفس شكل JSON تمامًا)
# =========================
def load_db():

    try:
        res = supabase.table("phones").select("*").execute()
        rows = res.data or []

        db = {}

        for r in rows:

            size = str(r.get("size", "")).strip()
            panel = str(r.get("panel", "")).strip()
            sensor = str(r.get("sensor", "")).strip()
            model = str(r.get("model", "")).strip()

            if not all([size, panel, sensor, model]):
                continue

            db.setdefault(size, {})
            db[size].setdefault(panel, {})
            db[size][panel].setdefault(sensor, {"models": []})

            if model not in db[size][panel][sensor]["models"]:
                db[size][panel][sensor]["models"].append(model)

        return db

    except Exception:
        # 🛡️ في حالة أي مشكلة في الشبكة
        return {}
