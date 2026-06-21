import json
import urllib.request
import urllib.error

# 🎯 الرابط الصحيح والمحدث لجدولك في Supabase
URL = "https://mgmphimlcdchtbiyhhbt.supabase.co/rest/v1/phones"
# تأكد أن هذا المفتاح هو الـ (anon public key) الخاص بمشروعك
KEY = "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX"

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# معالج التحويلات الذكي
class SupabaseRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_307(self, req, fp, code, msg, hdrs):
        new_url = hdrs.get('Location') or hdrs.get('location')
        if new_url:
            new_req = urllib.request.Request(new_url, data=req.data, headers=req.headers, method=req.get_method())
            return self.parent.open(new_req)
        return urllib.request.HTTPRedirectHandler.http_error_307(self, req, fp, code, msg, hdrs)

opener = urllib.request.build_opener(SupabaseRedirectHandler)

def _safe(v):
    if v is None: return ""
    return str(v).strip()

def _fetch_raw_rows():
    """جلب البيانات من Supabase"""
    try:
        # إضافة limit لجلب عدد كافٍ من البيانات
        req = urllib.request.Request(f"{URL}?select=*", headers=headers, method='GET')
        with opener.open(req, timeout=10.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"FETCH_RAW_ROWS ERROR: {e}")
        return []

def load_db():
    """بناء الهيكلية الشجرية للبيانات"""
    try:
        rows = _fetch_raw_rows()
        db = {}
        for row in rows:
            size = _safe(row.get("size"))
            model = _safe(row.get("model_name"))
            panel = _safe(row.get("panel")) or "Notch Screen"
            sensor = _safe(row.get("sensor")) or "hardware_top_sensor"
            
            if not size or not model: 
                continue
                
            db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})
            if model not in db[size][panel][sensor]["models"]:
                db[size][panel][sensor]["models"].append(model)
        return db
    except Exception as e:
        print(f"LOAD_DB ERROR: {e}")
        return {}

def add_model(size, panel, sensor, model):
    """إضافة جهاز جديد إلى Supabase"""
    try:
        payload = {
            "size": _safe(size),
            "panel": _safe(panel),
            "sensor": _safe(sensor),
            "model_name": _safe(model)
        }
        req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with opener.open(req) as response:
            return True
    except Exception as e:
        print(f"ADD_MODEL ERROR: {e}")
        return False

def save_db(data, new_phone_name=None, size=None, panel=None, sensor=None):
    if new_phone_name and size and panel and sensor:
        return add_model(size, panel, sensor, new_phone_name)
    return True
