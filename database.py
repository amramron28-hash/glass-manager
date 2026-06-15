from supabase import create_client

SUPABASE_URL = "YOUR_URL"
SUPABASE_KEY = "YOUR_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# ✔ حفظ آمن مع منع البيانات الخاطئة
# =========================
def add_model(size, panel, sensor, model):

    # 🛡️ حماية من البيانات الفارغة
    if not all([size, panel, sensor, model]):
        return False

    # 🛡️ منع التكرار
    existing = supabase.table("phones") \
        .select("*") \
        .eq("size", size) \
        .eq("panel", panel) \
        .eq("sensor", sensor) \
        .eq("model", model) \
        .execute()

    if existing.data:
        return False

    supabase.table("phones").insert({
        "size": size,
        "panel": panel,
        "sensor": sensor,
        "model": model
    }).execute()

    return True


# =========================
# ✔ تحميل البيانات بنفس بنية JSON القديمة
# =========================
def load_db():
    res = supabase.table("phones").select("*").execute()

    db = {}

    for r in res.data:
        size = r["size"]
        panel = r["panel"]
        sensor = r["sensor"]
        model = r["model"]

        db.setdefault(size, {})
        db[size].setdefault(panel, {})
        db[size][panel].setdefault(sensor, {"models": []})

        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)

    return db
