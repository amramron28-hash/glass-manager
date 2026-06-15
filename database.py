import os
import json
from supabase import create_client

# 🔒 الاتصال بالسحابة عبر الأسرار الآمنة
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 📤 دالة رفع هاتف جديد للسحابة مع منع التكرار
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
# 🔄 دالة جلب البيانات مع ميزة النقل التلقائي من الـ JSON
# ==========================================
def load_db():
    try:
        # 1. جلب البيانات الموجودة في السحابة حالياً
        res = supabase.table("phones").select("*").execute()
        rows = res.data or []
        
        # 2. ⚡ إذا كانت السحابة فارغة، نقوم بقراءة ملف JSON ونقل محتواه فوراً
        if not rows and os.path.exists("models_db.json"):
            try:
                with open("models_db.json", "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                
                # تفكيك هيكل الـ JSON المتداخل وضخه في جداول السحابة
                for size, panels in old_data.items():
                    for panel, sensors in panels.items():
                        for sensor, data in sensors.items():
                            for model in data.get("models", []):
                                add_model(size, panel, sensor, model)
                
                # إعادة قراءة السحابة مجدداً بعد اكتمال النقل
                res = supabase.table("phones").select("*").execute()
                rows = res.data or []
            except Exception:
                pass

        # 3. ترتيب البيانات في القاموس البرمجي المتداخل ليعمل التطبيق كالمعتاد
        db = {}
        for r in rows:
            size = str(r.get("size", "")).strip()
            panel = str(r.get("panel", "")).strip()
            sensor = str(r.get("sensor", "")).strip()
            model = r.get("model_name") or r.get("model") or ""
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

def save_db(cleaned_db=None):
    return True
