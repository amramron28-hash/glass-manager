import os
from supabase import create_client, Client
from core.logger import get_logger

log = get_logger("database")

# ==========================================
# SUPABASE CONFIGURATION
# ==========================================

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://mgmphimlcdchtbiyhhbt.supabase.co"
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX"
)

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    log.info("Supabase connected successfully.")
except Exception as e:
    log.error(f"Failed to initialize Supabase client: {e}")
    supabase = None


# ==========================================
# DATABASE LOADING
# ==========================================

def load_db():
    """
    تحميل قاعدة البيانات وتحويلها إلى:

    size
        └── panel
                └── sensor
                        └── models[]
    """

    if supabase is None:
        log.warning("Supabase client not available.")
        return {}

    try:

        result = (
            supabase
            .table("phones")
            .select("*")
            .execute()
        )

        rows = result.data or []

        database = {}

        total = 0

        for row in rows:

            size = str(row.get("size", "")).strip()

            panel = str(
                row.get("panel", "Notch Screen")
            ).strip()

            sensor = str(
                row.get("sensor", "hardware_top_sensor")
            ).strip()

            model = str(
                row.get("model_name")
                or row.get("model", "")
            ).strip()

            if not size or not model:
                continue

            database.setdefault(size, {})
            database[size].setdefault(panel, {})
            database[size][panel].setdefault(
                sensor,
                {"models": []}
            )

            models = database[size][panel][sensor]["models"]

            if model not in models:
                models.append(model)
                total += 1

        for size in database:
            for panel in database[size]:
                for sensor in database[size][panel]:
                    database[size][panel][sensor]["models"].sort()

        log.info(f"Loaded {total} models successfully.")

        return database

    except Exception as e:

        log.error(f"Error loading database: {e}")

        return {}


# ==========================================
# ADD MODEL
# ==========================================

def add_model(size, panel, sensor, model):

    if supabase is None:
        return False

    try:

        payload = {
            "size": str(size).strip(),
            "panel": str(panel).strip(),
            "sensor": str(sensor).strip(),
            "model_name": str(model).strip()
        }

        if not all(payload.values()):
            return False

        exists = (
            supabase
            .table("phones")
            .select("id")
            .eq("size", payload["size"])
            .eq("panel", payload["panel"])
            .eq("sensor", payload["sensor"])
            .eq("model_name", payload["model_name"])
            .execute()
        )

        if exists.data:
            log.info("Model already exists.")
            return True

        result = (
            supabase
            .table("phones")
            .insert(payload)
            .execute()
        )

        if result.data:
            log.info(f"Added model: {payload['model_name']}")
            return True

        return False

    except Exception as e:

        log.error(f"Error adding model: {e}")

        return False


# ==========================================
# DELETE MODEL
# ==========================================

def delete_model(model, size, panel, sensor):

    if supabase is None:
        return False

    try:

        (
            supabase
            .table("phones")
            .delete()
            .eq("model_name", str(model).strip())
            .eq("size", str(size).strip())
            .eq("panel", str(panel).strip())
            .eq("sensor", str(sensor).strip())
            .execute()
        )

        log.info(f"Deleted model: {model}")

        return True

    except Exception as e:

        log.error(f"Delete failed: {e}")

        return False


# ==========================================
# SAVE DATABASE
# ==========================================

def save_db(
    data=None,
    new_phone_name=None,
    size=None,
    panel=None,
    sensor=None
):

    if (
        new_phone_name
        and size
        and panel
        and sensor
    ):

        return add_model(
            size,
            panel,
            sensor,
            new_phone_name
        )

    return True


# ==========================================
# NOTIFICATIONS
# ==========================================

def add_notification(message, level="info"):
    """
    Placeholder.
    """
    log.info(f"[{level.upper()}] {message}")


# ==========================================
# EXTRA UTILITIES
# ==========================================

def reload_db():
    """
    إعادة تحميل قاعدة البيانات.
    """
    return load_db()


def ping_database():
    """
    اختبار الاتصال بقاعدة البيانات.
    """

    if supabase is None:
        return False

    try:

        supabase.table("phones").select("id").limit(1).execute()

        return True

    except Exception as e:

        log.error(f"Database ping failed: {e}")

        return False


def get_total_models():
    """
    عدد الموديلات الموجودة.
    """

    if supabase is None:
        return 0

    try:

        result = (
            supabase
            .table("phones")
            .select("id")
            .execute()
        )

        return len(result.data or [])

    except Exception:

        return 0
