import json
import urllib.request
import urllib.error

# 🎯 تم تثبيت الرابط والمفتاح السري الحقيقي الفعال لجدولك في Supabase لفتح القنوات حية
URL = "https://supabase.co"
KEY = "sb_secret_z8peIW-NaKurp6_yYEJeOQ_pzcoSGhT"

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# معالج التحويلات الذكي (Redirect Handler) لمنع أخطاء التوجيه 307 في Supabase
class SupabaseRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_307(self, req, fp, code, msg, hdrs):
        new_url = hdrs.get('Location') or hdrs.get('location')
        if new_url:
            new_req = urllib.request.Request(new_url, data=req.data, headers=req.headers, method=req.get_method())
            return self.parent.open(new_req)
        return urllib.request.HTTPRedirectHandler.http_error_307(self, req, fp, code, msg, hdrs)

opener = urllib.request.build_opener(SupabaseRedirectHandler)

def _safe(v):
    if v is None or isinstance(v, float): return ""
    return str(v).strip()

def _fetch_raw_rows():
    """جلب الأسطر الخام بالكامل وكسر قيود السقف الافتراضي لرؤية كافة المخزون دفعة واحدة"""
    try:
        # 🎯 تم حقن limit=5000 لإلغاء قيود الصفحات وسحب كل أسطر السحابة بلا حظر
        req = urllib.request.Request(f"{URL}?select=*&limit=5000", headers=headers, method='GET')
        with opener.open(req, timeout=4.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print("FETCH_RAW_ROWS ERROR:", e)
        return []

def load_db():
    """
    الدالة المركزية لجلب الموديلات وبناء المصفوفة الشجرية للتوافق لفك العزل الحسابي.
    تطابق دقيق لقراءة حقل 'model_name' الفعلي من جدول Supabase وضخه في محرك الـ logic.
    """
    try:
        rows = _fetch_raw_rows()
        db = {}
        for row in rows:
            size = _safe(row.get("size"))
            
            # 🎯 القراءة الصارمة لعمود جدولك الفعلي المتأكد منه بحرف (e)
            model = _safe(row.get("model_name"))
            
            panel = _safe(row.get("panel")) or "Notch Screen"
            sensor = _safe(row.get("sensor")) or "hardware_top_sensor"
            
            if not size or not model: 
                continue
                
            # بناء التفرع الشجري وتعبئة مفتاح 'models' ليتطابق مع الـ logic والـ workflows
            db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})
            if model not in db[size][panel][sensor]["models"]:
                db[size][panel][sensor]["models"].append(model)
                
        return db
    except Exception as e:
        print("LOAD_DB ERROR:", e)
        return {}

def add_model(size, panel, sensor, model):
    """دالة الرفع التلقائي لحفظ الهواتف الجديدة بمطابقة حقول الجدول في السحابة"""
    try:
        payload = {
            "size": _safe(size),
            "panel": _safe(panel),
            "sensor": _safe(sensor),
            "model_name": _safe(model)  # 🎯 تم التثبيت والمطابقة للعمود الفعلي بجدولك
        }
        req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with opener.open(req) as response:
            print(f"SUCCESS: Server responded with {response.getcode()}")
            return True
    except urllib.error.HTTPError as e:
        print(f"!!! HTTP ERROR: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"!!! GENERAL ERROR: {str(e)}")
        return False

def save_db(data, new_phone_name=None, size=None, panel=None, sensor=None):
    if new_phone_name and size and panel and sensor:
        return add_model(size, panel, sensor, new_phone_name)
    return True

# كائن المحاكاة المتوافق مع بقية ملفات المشروع البرمجي
class SupabaseMockClient:
    def table(self, *a, **k): return self
    def select(self, *a, **k): return self
    def delete(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def insert(self, *a, **k): return self
    def execute(self):
        class R: data = _fetch_raw_rows()
        return R()

supabase = SupabaseMockClient()
