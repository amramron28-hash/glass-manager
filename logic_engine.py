import re
import time
from typing import Dict, Optional, Tuple, Any

from database import supabase
from core.logger import get_logger


# ==========================================================
# STATUS
# ==========================================================

STATUS_SUCCESS = "success"
STATUS_PLAN_2 = "plan_2"
STATUS_PLAN2_SUCCESS = "plan2_success"
STATUS_PLAN_3 = "plan_3"
STATUS_ERROR = "error"


# ==========================================================
# TOLERANCE
# ==========================================================

TOLERANCE = 0.05
EXACT_TOLERANCE = 0.001


# ==========================================================
# LOGGER
# ==========================================================

log = get_logger("logic_engine")


# ==========================================================
# NORMALIZER
# ==========================================================

_clean_regex = re.compile(r"[^a-z0-9\u0621-\u064a]+")

_norm_cache: Dict[str, str] = {}

MAX_CACHE_SIZE = 50000


def normalize_text(text: Any) -> str:
    """
    تنظيف النص للبحث السريع
    يدعم العربية والإنجليزية
    """

    key = str(text or "").strip()

    if not key:
        return ""

    cached = _norm_cache.get(key)

    if cached is not None:
        return cached


    cleaned = _clean_regex.sub(
        "",
        key.lower()
    )


    # حماية الكاش من التضخم
    if len(_norm_cache) >= MAX_CACHE_SIZE:
        _norm_cache.clear()


    _norm_cache[key] = cleaned

    return cleaned


# ==========================================================
# PANEL NAME NORMALIZER
# ==========================================================
# يوحّد أسماء أنواع الشاشة المتشابهة التي قد تُدخل بصيغ مختلفة
# في قاعدة البيانات (مثال: "Punch-Hole" و "Punch-Hole Screen"
# يجب أن يُعتبرا نفس النوع عند المطابقة).

def normalize_panel(text: Any) -> str:

    cleaned = normalize_text(text)

    if cleaned.endswith("screen"):
        cleaned = cleaned[: -len("screen")]

    return cleaned



# ==========================================================
# SIZE EXTRACTOR
# ==========================================================

_size_cache: Dict[str, Optional[float]] = {}


def extract_numeric_size(size_string: Any) -> Optional[float]:
    """
    استخراج قياس الشاشة كرقم
    أمثلة:
    6.67
    6,67 inch
    6.5"
    """

    if size_string is None:
        return None


    key = str(size_string).strip()


    if key in _size_cache:
        return _size_cache[key]


    key = key.replace(",", ".")


    match = re.search(
        r"[-+]?\d*\.\d+|\d+",
        key
    )


    if not match:
        _size_cache[key] = None
        return None


    value = float(match.group())


    _size_cache[key] = value

    return value
# ==========================================================
# DATABASE STRUCTURE BUILDER
# ==========================================================

def fetch_db_structure() -> Dict:
    """
    جلب بيانات الهواتف من Supabase
    وتحويلها إلى هيكل سريع للبحث

    الشكل:
    {
        size:{
            panel:{
                sensor:{
                    models:[]
                }
            }
        }
    }
    """

    try:

        response = (
            supabase
            .table("phones")
            .select("*")
            .execute()
        )


        rows = response.data or []

        database = {}


        for row in rows:

            size = str(
                row.get("size") or ""
            ).strip()


            panel = str(
                row.get("panel") or ""
            ).strip()


            sensor = str(
                row.get("sensor") or ""
            ).strip()


            model = str(
                row.get("model_name")
                or row.get("model")
                or ""
            ).strip()


            if not all(
                [
                    size,
                    panel,
                    sensor,
                    model
                ]
            ):
                continue



            sensor_group = (
                database
                .setdefault(size, {})
                .setdefault(panel, {})
                .setdefault(
                    sensor,
                    {
                        "models": []
                    }
                )
            )


            if model not in sensor_group["models"]:
                sensor_group["models"].append(model)



        return database


    except Exception as e:

        log.exception(
            f"Database fetch error: {e}"
        )

        return {}



# ==========================================================
# MODEL SEARCH
# ==========================================================

def find_model_coords(
        db_data: Dict,
        phone: str
) -> Tuple[
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[str]
]:

    """
    البحث عن الهاتف وإرجاع:
    size, panel, sensor, real_name
    """

    if not db_data or not phone:
        return (
            None,
            None,
            None,
            None
        )


    search_norm = normalize_text(phone)

    best_match = None



    for size, panels in db_data.items():

        if not isinstance(
            panels,
            dict
        ):
            continue



        for panel, sensors in panels.items():

            if not isinstance(
                sensors,
                dict
            ):
                continue



            for sensor, data in sensors.items():


                if isinstance(data, dict):

                    models = data.get(
                        "models",
                        []
                    )

                else:

                    models = data



                if not isinstance(
                    models,
                    list
                ):
                    continue



                for model in models:


                    model_norm = normalize_text(
                        model
                    )


                    # تطابق كامل
                    if model_norm == search_norm:

                        return (
                            size,
                            panel,
                            sensor,
                            model
                        )


                    # تطابق جزئي احتياطي
                    if (
                        best_match is None
                        and
                        (
                            model_norm.startswith(
                                search_norm
                            )
                            or
                            search_norm in model_norm
                        )
                    ):

                        best_match = (
                            size,
                            panel,
                            sensor,
                            model
                        )



    if best_match:
        return best_match


    return (
        None,
        None,
        None,
        None
    )
# ==========================================================
# COMPATIBILITY ENGINE
# ==========================================================

def get_compatibles_strict(
        db_data: Dict,
        size: str,
        panel: str,
        sensor: str,
        real_name: str
) -> dict:

    """
    البحث عن الشاشات المتوافقة
    حسب الحجم مع استبعاد الهاتف الحالي
    """

    result = {
        "exact": [],
        "plus": [],
        "minus": [],
        "warn": []
    }


    current_size = extract_numeric_size(size)

    if current_size is None:
        return result


    current_model = normalize_text(real_name)



    for other_size, panels in db_data.items():

        if not isinstance(
            panels,
            dict
        ):
            continue


        other_size_num = extract_numeric_size(
            other_size
        )


        if other_size_num is None:
            continue



        diff = other_size_num - current_size



        if abs(diff) > TOLERANCE:
            continue



        current_panel_norm = normalize_panel(panel)

        panel_data = None

        for panel_key, sensors_dict in panels.items():

            if normalize_panel(panel_key) == current_panel_norm:
                panel_data = sensors_dict
                break

        if not isinstance(
            panel_data,
            dict
        ):
            continue



        for sensor_name, data in panel_data.items():


            if isinstance(data, dict):

                models = data.get(
                    "models",
                    []
                )

            else:

                models = data



            if not isinstance(
                models,
                list
            ):
                continue



            bucket = None


            if abs(diff) <= EXACT_TOLERANCE:

                if normalize_text(sensor_name) == normalize_text(sensor):
                    bucket = "exact"
                else:
                    bucket = "warn"


            elif diff > 0:

                bucket = "plus"


            elif diff < 0:

                bucket = "minus"



            if bucket:

                for model in models:

                    if normalize_text(model) == current_model:
                        continue


                    result[bucket].append(model)



    # حذف التكرار وترتيب النتائج

    for key in result:

        result[key] = sorted(
            list(
                dict.fromkeys(
                    result[key]
                )
            )
        )


    return result



# ==========================================================
# PLAN 2 GROUP FINDER
# ==========================================================

def find_group_by_specs(
        db_data: Dict,
        specs: dict,
        tol: float = TOLERANCE
) -> Optional[dict]:

    """
    البحث بواسطة:
    size + panel + sensor

    يستخدم في Plan 2
    """

    if not isinstance(
        specs,
        dict
    ):
        return None



    required_size = extract_numeric_size(
        specs.get("size")
    )


    if required_size is None:
        return None



    required_panel = normalize_panel(
        specs.get("panel")
    )


    required_sensor = normalize_text(
        specs.get("sensor")
    )



    for size_key, panels in db_data.items():


        size_value = extract_numeric_size(
            size_key
        )


        if size_value is None:
            continue



        if abs(size_value - required_size) > tol:
            continue



        if not isinstance(
            panels,
            dict
        ):
            continue



        for panel_key, sensors in panels.items():


            if normalize_panel(panel_key) != required_panel:
                continue



            if not isinstance(
                sensors,
                dict
            ):
                continue



            for sensor_key, data in sensors.items():


                if normalize_text(sensor_key) != required_sensor:
                    continue



                if isinstance(data, dict):

                    models = data.get(
                        "models",
                        []
                    )

                else:

                    models = data



                if not isinstance(
                    models,
                    list
                ):
                    models = []



                return {

                    "group_id":
                        f"{panel_key}-{sensor_key}",

                    "models":
                        sorted(
                            list(
                                dict.fromkeys(
                                    models
                                )
                            )
                        ),

                    "size":
                        size_key,

                    "panel":
                        panel_key,

                    "sensor":
                        sensor_key
                }



    return None
# ==========================================================
# INTELLIGENT INSPECTOR
# ==========================================================

def run_intelligent_inspector(
        db_data=None
):

    """
    تنظيف قاعدة البيانات:
    - حذف الصفوف الناقصة
    - إزالة التكرارات
    - بناء نسخة نظيفة
    """

    changes_made = False

    cleaned_db = {}

    seen = set()


    try:

        response = (
            supabase
            .table("phones")
            .select(
                "id,size,panel,sensor,model_name,model"
            )
            .execute()
        )


        rows = response.data or []


        delete_ids = []


        for row in rows:


            row_id = row.get("id")


            size = str(
                row.get("size") or ""
            ).strip()


            panel = str(
                row.get("panel") or ""
            ).strip()


            sensor = str(
                row.get("sensor") or ""
            ).strip()


            model = str(
                row.get("model_name")
                or row.get("model")
                or ""
            ).strip()



            # بيانات ناقصة

            if not all(
                [
                    size,
                    panel,
                    sensor,
                    model
                ]
            ):

                if row_id:
                    delete_ids.append(row_id)

                changes_made = True
                continue



            key = (
                size,
                panel,
                sensor,
                model
            )



            # تكرار

            if key in seen:

                if row_id:
                    delete_ids.append(row_id)

                changes_made = True
                continue



            seen.add(key)



            cleaned_db \
                .setdefault(size,{}) \
                .setdefault(panel,{}) \
                .setdefault(
                    sensor,
                    {
                        "models":[]
                    }
                )["models"].append(model)



        # حذف دفعة واحدة

        for item_id in delete_ids:

            try:

                supabase.table(
                    "phones"
                ).delete().eq(
                    "id",
                    item_id
                ).execute()

            except Exception:

                pass



        return cleaned_db, changes_made



    except Exception as e:

        log.exception(
            f"Inspector error: {e}"
        )


        return (
            db_data if db_data else {},
            False
        )



# ==========================================================
# MAIN WORKFLOW
# ==========================================================

def run_system_workflows(
        phone: str,
        db_data: Optional[dict] = None,
        plan2_input: Optional[dict] = None
) -> dict:


    start_time = time.time()


    try:


        phone = (
            phone or ""
        ).strip()



        if not db_data:

            db_data = fetch_db_structure()



        if not db_data:

            return {

                "status":
                    STATUS_ERROR,

                "message":
                    "DB_EMPTY_OR_ERROR"
            }



        # ==========================
        # PLAN 1
        # ==========================

        size, panel, sensor, real_name = (
            find_model_coords(
                db_data,
                phone
            )
        )



        if real_name:


            return {

                "status":
                    STATUS_SUCCESS,


                "coords":
                {

                    "size":
                        size,

                    "panel":
                        panel,

                    "sensor":
                        sensor,

                    "real_name":
                        real_name

                },


                "compatibles":
                    get_compatibles_strict(
                        db_data,
                        size,
                        panel,
                        sensor,
                        real_name
                    )
            }



        # ==========================
        # PLAN 2
        # ==========================

        if isinstance(
            plan2_input,
            dict
        ):


            matched = find_group_by_specs(
                db_data,
                plan2_input
            )


            if matched:

                return {

                    "status":
                        STATUS_PLAN2_SUCCESS,

                    **matched
                }



        # ==========================
        # PLAN 3
        # ==========================

        return {

            "status":
                STATUS_PLAN_3,


            "input_data":
                plan2_input or
                {
                    "size": None,
                    "panel": None,
                    "sensor": None
                }

        }



    except Exception as e:


        log.exception(
            f"Workflow error: {e}"
        )


        return {

            "status":
                STATUS_ERROR,

            "message":
                "INTERNAL_ERROR"
        }



    finally:


        log.info(
            "Execution time %.4f sec",
            time.time() - start_time
    )
