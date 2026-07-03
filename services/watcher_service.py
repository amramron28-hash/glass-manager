from core.logger import get_logger

log = get_logger("watcher_service")


def execute_refresh_logic(
    cached_stats,
    database_data,
    autocomplete_index,
    models_index,
    custom_panels,
    custom_sensors,
    last_db_size,
    show_curtain,
    current_phone,
    suggestions_list,
    refresh_fn,
    invalidate_workflow_fn,
):
    try:
        refresh_fn()
        invalidate_workflow_fn()
    except Exception as e:
        log.error(f"Refresh Logic Error: {e}")


def execute_status_logic(
    get_cached_status_data,
    last_monitor_status,
):
    try:
        status = get_cached_status_data()

        if isinstance(status, dict):
            last_monitor_status.set(
                status.get("status", "UNKNOWN")
            )
    except Exception as e:
        log.error(f"Status Logic Error: {e}")
