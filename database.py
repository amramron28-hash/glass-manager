import json
import urllib.request

# 🌐 Supabase
URL = "https://mgmphimlcdchtbiyhhbt.supabase.co/rest/v1/phones"
KEY = "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX"

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}

# 🔁 دعم التوجيهات
class SupabaseRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_307(self, req, fp, code, msg, hdrs):
        new_url = hdrs.get('Location') or hdrs.get('location')
        if new_url:
            new_req = urllib.request.Request(
                new_url,
                data=req.data,
                headers=req.headers,
                method=req.get_method()
            )
            return self.parent.open(new_req)
        return urllib.request.HTTPRedirectHandler.http_error_307(self, req, fp, code, msg, hdrs)

opener = urllib.request.build_opener(SupabaseRedirectHandler)


# 🧠 تنظيف أسماء الموديلات
def clean_model_name(name: str) -> str:
    if not name:
        return ""

    name = name.strip()
    name = " ".join(name.split())

    fixes = {
        "45G": "4G",
        "64G": "4G",
        "6G": "5G",
        "SG": "5G",
        "SZ": "5G",
        "Lita": "Lite",
        "&": "5G"
    }

    for wrong, correct in fixes.items():
        name = name.replace(wrong, correct)

    return name


# 📥 تحميل البيانات وتحويلها لشكل المشروع
def load_db():
    try:
        req = urllib.request.Request(
            f"{URL}?select=*",
            headers=headers,
            method='GET'
        )

        with opener.open(req) as response:
            if response.getcode() != 200:
                return {}

            rows = json.loads(response.read().decode("utf-8"))

        db = {}

        for row in rows:
            size = str(row.get("size", "")).strip()
            model = clean_model_name(str(row.get("model_name", "")))

            if not size or not model:
                continue

            panel = "Notch Screen"
            sensor = "hardware_top_sensor"

            db.setdefault(size, {})
            db[size].setdefault(panel, {})
            db[size][panel].setdefault(sensor, {"models": []})

            if model not in db[size][panel][sensor]["models"]:
                db[size][panel][sensor]["models"].append(model)

        return db

    except Exception as e:
        print("LOAD_DB ERROR:", e)
        return {}


# ➕ إضافة موديل جديد
def add_model(size, panel, sensor, model):
    if not all([size, model]):
        return False

    model = clean_model_name(model)

    payload = {
        "size": str(size).strip(),
        "panel": panel or "Notch Screen",
        "sensor": sensor or "hardware_top_sensor",
        "model_name": model
    }

    try:
        data_bytes = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            URL,
            data=data_bytes,
            headers=headers,
            method='POST'
        )

        with opener.open(req) as response:
            return 200 <= response.getcode() < 300

    except Exception as e:
        print("ADD_MODEL ERROR:", e)
        return False


# 💾 دالة وهمية لحماية المشروع
def save_db(data=None):
    return True


# 🧩 Mock Supabase (لتجنب الأخطاء في باقي الملفات)
class SupabaseMockClient:
    class MockTable:
        def insert(self, *args, **kwargs):
            return self

        def select(self, *args, **kwargs):
            return self

        def execute(self, *args, **kwargs):
            class MockResponse:
                data = load_db()
            return MockResponse()

    def table(self, *args, **kwargs):
        return self.MockTable()


# 🔌 كائن جاهز للاستخدام
supabase = SupabaseMockClient()
