import json
import urllib.request

URL = "https://mgmphimlcdchtbiyhhbt.supabase.co/rest/v1/phones"
KEY = "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX"

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}


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
        return urllib.request.HTTPRedirectHandler.http_error_307(
            self, req, fp, code, msg, hdrs
        )


opener = urllib.request.build_opener(SupabaseRedirectHandler)


# =========================
# 🧠 تنظيف آمن
# =========================
def _safe(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return ""
    return str(v).strip()


# =========================
# 📥 load_db (المهم)
# =========================
def load_db():
    try:
        req = urllib.request.Request(
            f"{URL}?select=*",
            headers=headers,
            method='GET'
        )

        with opener.open(req) as response:
            rows = json.loads(response.read().decode("utf-8"))

        db = {}

        for row in rows:
            size = _safe(row.get("size"))
            model = _safe(row.get("model_name"))

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


# =========================
# ➕ add_model
# =========================
def add_model(size, panel, sensor, model):
    try:
        payload = {
            "size": _safe(size),
            "panel": panel,
            "sensor": sensor,
            "model_name": _safe(model)
        }

        req = urllib.request.Request(
            URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with opener.open(req) as response:
            return 200 <= response.getcode() < 300

    except Exception as e:
        print("ADD_MODEL ERROR:", e)
        return False


def save_db(data=None):
    return True


# =========================
# 🧩 Mock (لا يسبب مشاكل)
# =========================
class SupabaseMockClient:
    class MockTable:
        def insert(self, *a, **k): return self
        def select(self, *a, **k): return self
        def execute(self):
            class R:
                data = load_db()
            return R()

    def table(self, *a, **k):
        return self.MockTable()


supabase = SupabaseMockClient()
