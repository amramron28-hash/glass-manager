import json
import urllib.request
import urllib.error
from core.logger import get_logger

log = get_logger("database")

#  الرابط والمفتاح
URL = "https://mgmphimlcdchtbiyhhbt.supabase.co/rest/v1/phones"
KEY = "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX"

def _fetch_raw_rows():
    try:
        req = urllib.request.Request(f"{URL}?select=*", method="GET")
        req.add_header("apikey", KEY)
        req.add_header("Authorization", f"Bearer {KEY}")
        req.add_header("Content-Type", "application/json")
        
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                log.warning(f"HTTP Error fetching rows: {response.status}")
                return []
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        log.error(f"DATABASE_HTTP_ERROR: {e.code} - {e.reason}")
        return []
    except urllib.error.URLError as e:
        log.error(f"DATABASE_CONNECTION_ERROR: {e.reason}")
        return []
    except Exception as e:
        log.error(f"DATABASE_FETCH_ERROR: {e}")
        return []

def load_db():
    """تحميل قاعدة البيانات وتحويلها لهيكلية شجرية نظيفة"""
    rows = _fetch_raw_rows()
    db = {}
    
    for row in rows:
        # ✅ إزالة المسافات الزائدة من القيم والمفاتيح عند القراءة
        size = str(row.get("size") or "").strip()
        model = str(row.get("model_name") or "").strip()
        panel = str(row.get("panel") or "Notch Screen").strip()
        sensor = str(row.get("sensor") or "hardware_top_sensor").strip()

        if not size or not model:
            continue

        # بناء الهيكلية بمفاتيح نظيفة تماماً
        db.setdefault(size, {}) \
          .setdefault(panel, {}) \
          .setdefault(sensor, {"models": []})

        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)

    log.info(f"Loaded database with {sum(len(s['models']) for p in db.values() for s in p.values())} models")
    return db

def add_model(size, panel, sensor, model):
    """إضافة موديل جديد إلى Supabase"""
    try:
        payload = {
            "size": size.strip(),
            "panel": panel.strip(),
            "sensor": sensor.strip(),
            "model_name": model.strip()
        }
        
        req = urllib.request.Request(
            URL,
            data=json.dumps(payload).encode("utf-8"),
            method="POST"
        )

        req.add_header("apikey", KEY)
        req.add_header("Authorization", f"Bearer {KEY}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "return=minimal")

        with urllib.request.urlopen(req, timeout=15) as response:
            success = response.status in (200, 201, 204)
            if success:
                log.info(f"Model added successfully: {model}")
            else:
                log.warning(f"Add model returned status: {response.status}")
            return success

    except urllib.error.HTTPError as e:
        log.error(f"ADD_MODEL_HTTP_ERROR: {e.code} - {e.reason}")
        return False
    except urllib.error.URLError as e:
        log.error(f"ADD_MODEL_CONNECTION_ERROR: {e.reason}")
        return False
    except Exception as e:
        log.error(f"ADD_MODEL_ERROR: {e}")
        return False

def save_db(data, new_phone_name=None, size=None, panel=None, sensor=None):
    """دالة مساعدة للتوافق مع الكود القديم"""
    if new_phone_name and size and panel and sensor:
        return add_model(size, panel, sensor, new_phone_name)
    return True
