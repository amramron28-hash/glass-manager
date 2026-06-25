import json
import urllib.request
import urllib.error

# 🎯 الرابط والمفتاح
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
                return []
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        print(f"DATABASE_HTTP_ERROR: {e.code} - {e.reason}")
        return []

    except urllib.error.URLError as e:
        print(f"DATABASE_CONNECTION_ERROR: {e.reason}")
        return []

    except Exception as e:
        print(f"DATABASE_ERROR: {e}")
        return []


def load_db():
    rows = _fetch_raw_rows()
    db = {}

    for row in rows:
        size = str(row.get("size", "")).strip()
        model = str(row.get("model_name", "")).strip()
        panel = str(row.get("panel", "Notch Screen")).strip()
        sensor = str(row.get("sensor", "hardware_top_sensor")).strip()

        if not size or not model:
            continue

        db.setdefault(size, {}) \
          .setdefault(panel, {}) \
          .setdefault(sensor, {"models": []})

        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)

    return db


def add_model(size, panel, sensor, model):
    try:
        payload = {
            "size": size,
            "panel": panel,
            "sensor": sensor,
            "model_name": model
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
            return response.status in (200, 201, 204)

    except urllib.error.HTTPError as e:
        print(f"ADD_MODEL_HTTP_ERROR: {e.code} - {e.reason}")
        return False

    except urllib.error.URLError as e:
        print(f"ADD_MODEL_CONNECTION_ERROR: {e.reason}")
        return False

    except Exception as e:
        print(f"ADD_MODEL_ERROR: {e}")
        return False


def save_db(data, new_phone_name=None, size=None, panel=None, sensor=None):
    if new_phone_name and size and panel and sensor:
        return add_model(size, panel, sensor, new_phone_name)
    return True
