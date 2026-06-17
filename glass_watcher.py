import threading
import time
import json
import os
from datetime import datetime

from database import supabase


# ==========================
# ملف ذاكرة التنبيهات
# ==========================

ALERT_FILE = "watcher_alerts.json"


def load_alerts():

    try:

        if os.path.exists(ALERT_FILE):

            with open(
                ALERT_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

    except:

        pass


    return []



def save_alerts(alerts):

    try:

        with open(
            ALERT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                alerts,
                f,
                ensure_ascii=False,
                indent=2
            )

    except:

        pass




# ==========================
# قراءة البيانات الحية
# ==========================

def fetch_phones():

    try:

        result = (
            supabase
            .table("phones")
            .select("*")
            .execute()
        )


        return result.data or []


    except Exception as e:

        return []





# ==========================
# تنظيف النص
# ==========================

def clean_text(v):

    if not v:

        return ""


    return (
        str(v)
        .lower()
        .strip()
    )





# ==========================
# 🧠 فحص التكرار والتداخل
# ==========================

def run_silent_check():


    rows = fetch_phones()


    alerts = []

    seen = {}



    for row in rows:


        model = clean_text(
            row.get("model_name")
        )


        size = clean_text(
            row.get("size")
        )


        panel = clean_text(
            row.get("panel")
        )


        sensor = clean_text(
            row.get("sensor")
        )



        if not model:


            alerts.append(
                {
                    "type":
                    "missing_model",

                    "time":
                    str(datetime.now()),

                    "message":
                    "سجل بدون اسم هاتف",

                    "id":
                    row.get("id")
                }
            )


            continue





        key = (

            model,

            size,

            panel,

            sensor

        )



        if key in seen:


            alerts.append(

                {

                "type":
                "duplicate",

                "time":
                str(datetime.now()),

                "message":
                f"تكرار الهاتف: {row.get('model_name')}",

                "id":
                row.get("id")

                }

            )


        else:

            seen[key] = row





    save_alerts(alerts)


    return alerts
# ==========================
# 🔎 كشف نفس الهاتف بمواصفات مختلفة
# ==========================

def detect_conflicts():

    rows = fetch_phones()


    conflicts = []

    models_map = {}



    for row in rows:


        model = clean_text(
            row.get("model_name")
        )


        if not model:

            continue



        data = {

            "size":
            clean_text(row.get("size")),

            "panel":
            clean_text(row.get("panel")),

            "sensor":
            clean_text(row.get("sensor"))

        }



        if model not in models_map:


            models_map[model] = []


        models_map[model].append(data)





    for model, items in models_map.items():


        unique = []


        for item in items:


            if item not in unique:

                unique.append(item)




        if len(unique) > 1:


            conflicts.append(

                {

                "type":
                "conflict",

                "time":
                str(datetime.now()),

                "message":
                f"اختلاف بيانات للهاتف: {model}",

                "details":
                unique

                }

            )



    return conflicts





# ==========================
# 🧠 تشغيل الفحص الكامل
# ==========================

def watcher_cycle():


    alerts = []


    alerts.extend(
        run_silent_check()
    )


    alerts.extend(
        detect_conflicts()
    )



    save_alerts(alerts)



# ==========================
# 🔁 الخيط الخلفي
# ==========================

def start_watcher(
    interval=300
):


    def loop():


        while True:


            try:

                watcher_cycle()


            except Exception:


                pass



            time.sleep(
                interval
            )



    thread = threading.Thread(

        target=loop,

        daemon=True

    )


    thread.start()



    return thread





# ==========================
# 📤 قراءة التنبيهات للواجهة
# ==========================

def get_watcher_alerts():


    return load_alerts()
