def load_db():
    """تحويل بيانات Supabase (flat) إلى بنية المشروع المتداخلة"""

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
            model = str(row.get("model_name", "")).strip()

            # ⚠️ لأن جدولك لا يحتوي panel/sensor
            panel = "Notch Screen"
            sensor = "hardware_top_sensor"

            if not size or not model:
                continue

            db.setdefault(size, {})
            db[size].setdefault(panel, {})
            db[size][panel].setdefault(sensor, {"models": []})

            if model not in db[size][panel][sensor]["models"]:
                db[size][panel][sensor]["models"].append(model)

        return db

    except Exception as e:
        print("LOAD_DB ERROR:", e)
        return {}
