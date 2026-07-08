from core.logger import get_logger
from services.plan_engine import compute_plan_matches, is_empty_result

log = get_logger("plan_controller")


def fuzzy_find(value, available):
    if not value or not available:
        return None

    if value in available:
        return value

    value_norm = (
        str(value)
        .lower()
        .strip()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
    )

    for item in available:
        item_norm = (
            str(item)
            .lower()
            .strip()
            .replace("_", " ")
            .replace("-", " ")
            .replace("/", " ")
        )

        if value_norm == item_norm:
            return item

        if value_norm in item_norm or item_norm in value_norm:
            return item

        v_words = set(value_norm.split())
        i_words = set(item_norm.split())

        if v_words and len(v_words & i_words) >= max(
            1, min(len(v_words), len(i_words)) * 0.5
        ):
            return item

    return None


def process_plan(
    size,
    panel,
    sensor,
    db,
    fast_index,
):
    if not all([size, panel, sensor]):
        return None

    size = str(size).strip()

    matched_size = fuzzy_find(size, list(db.keys()))
    if not matched_size:
        log.warning(f"Size not found: {size}")
        return None

    matched_panel = fuzzy_find(
        panel,
        list(db[matched_size].keys()),
    )
    if not matched_panel:
        log.warning(f"Panel not found: {panel}")
        return None

    sensors = list(db[matched_size][matched_panel].keys())

    matched_sensor = fuzzy_find(sensor, sensors)

    if matched_sensor is None:
        if not sensors:
            return None
        matched_sensor = sensors[0]

    results = compute_plan_matches(
        matched_size,
        matched_panel,
        matched_sensor,
        db,
        fast_index,
    )

    if is_empty_result(results):
        return None

    return {
        "results": results,
        "size": matched_size,
        "panel": matched_panel,
        "sensor": matched_sensor
