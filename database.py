import os
import traceback
from supabase import create_client, Client
from core.logger import get_logger

log = get_logger("database")

# ==========================================================
# SUPABASE CONFIGURATION
# ==========================================================

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://mgmphimlcdchtbiyhhbt.supabase.co"
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    ""
)

supabase: Client | None = None

try:

    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL is missing")

    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_KEY is missing")

    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    test = (
        supabase
        .table("phones")
        .select("*")
        .limit(1)
        .execute()
    )

    log.info(
        f"Supabase connected successfully ({len(test.data or [])} test rows)"
    )

except Exception as e:

    traceback.print_exc()

    log.error(
        f"Supabase initialization failed: {type(e).__name__}: {e}"
    )

    supabase = None


# ==========================================================
# LOAD DATABASE
# ==========================================================

def load_db():

    if supabase is None:

        log.error("Supabase client is not initialized")

        return {}

    try:

        response = (
            supabase
            .table("phones")
            .select("*")
            .execute()
        )

        rows = response.data or []

        log.info(f"Rows fetched: {len(rows)}")

        if rows:
            log.info(f"Columns: {list(rows[0].keys())}")

        database = {}

        total_models = 0

        for row in rows:

            size = str(
                row.get("size", "")
            ).strip()

            panel = str(
                row.get("panel", "Notch Screen")
            ).strip()

            sensor = str(
                row.get("sensor", "hardware_top_sensor")
            ).strip()

            model = str(

                row.get("model_name")

                or row.get("model")

                or ""

            ).strip()

            if not size or not model:
                continue

            database.setdefault(size, {})
            database[size].setdefault(panel, {})
            database[size][panel].setdefault(
                sensor,
                {"models": []}
            )

            if model not in database[size][panel][sensor]["models"]:

                database[size][panel][sensor]["models"].append(model)

                total_models += 1

        log.info(
            f"Database loaded successfully ({total_models} models)"
        )

        return database

    except Exception as e:

        traceback.print_exc()

        log.error(
            f"load_db failed: {type(e).__name__}: {e}"
        )

        return {}


# ==========================================================
# ADD MODEL
# ==========================================================

def add_model(
    size,
    panel,
    sensor,
    model
):

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

        response = (

            supabase
            .table("phones")
            .insert(payload)
            .execute()

        )

        if response.data:

            log.info(
                f"Model added: {payload['model_name']}"
            )

            return True

        return False

    except Exception as e:

        traceback.print_exc()

        log.error(
            f"add_model failed: {type(e).__name__}: {e}"
        )

        return False


# ==========================================================
# SAVE DATABASE
# ==========================================================

def save_db(

    data=None,

    new_phone_name=None,

    size=None,

    panel=None,

    sensor=None,

):

    if (

        new_phone_name

        and size

        and panel

        and sensor

    ):

        return add_model(

            size=size,

            panel=panel,

            sensor=sensor,

            model=new_phone_name,

        )

    return True


# ==========================================================
# DELETE MODEL
# ==========================================================

def delete_model(model_name):

    if supabase is None:
        return False

    try:

        (

            supabase

            .table("phones")

            .delete()

            .eq("model_name", model_name)

            .execute()

        )

        log.info(
            f"Deleted model: {model_name}"
        )

        return True

    except Exception as e:

        traceback.print_exc()

        log.error(
            f"delete_model failed: {type(e).__name__}: {e}"
        )

        return False


# ==========================================================
# NOTIFICATIONS
# ==========================================================

def add_notification(
    message,
    level="info"
):

    log.info(
        f"[{level.upper()}] {message}"
    )


# ==========================================================
# DATABASE STATUS
# ==========================================================

def database_connected():

    return supabase is not None
