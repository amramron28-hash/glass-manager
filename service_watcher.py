from core.logger import get_logger
from services.database_service import load_models_index
from services.index_service import extract_panels_sensors
from services.search_service import build_autocomplete_index

log = get_logger("service_watcher")


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
    """تحديث البيانات والفهارس"""

    try:
        stats = cached_stats()
        db_size = stats.get("phones", 0) if isinstance(stats, dict) else 0

        if db_size == 0:
            autocomplete_index.set(None)
            models_index.set([])
            custom_panels.set([])
            custom_sensors.set([])
            suggestions_list.set([])
            last_db_size.set(0)
            return

        if last_db_size() == db_size and autocomplete_index() is not None:
            if show_curtain():
                trie = autocomplete_index()
                query = current_phone()
                if trie and query:
                    suggestions_list.set(trie.search_prefix(query, 10))
            return

        last_db_size.set(db_size)

        refresh_fn()

        new_models = load_models_index()

        if autocomplete_index() is None or new_models != models_index():
            models_index.set(new_models)
            autocomplete_index.set(build_autocomplete_index(new_models))

            invalidate_workflow_fn()

            panels, sensors = extract_panels_sensors(database_data())
            custom_panels.set(panels)
            custom_sensors.set(sensors)

        if show_curtain():
            trie = autocomplete_index()
            query = current_phone()

            if trie and query:
                suggestions_list.set(trie.search_prefix(query, 10))

    except Exception as error:
        log.error(f"Refresh Logic Error: {error}", exc_info=True)


def execute_status_logic(
    get_cached_status_data,
    last_monitor_status,
):
    """مراقبة الحالة"""

    try:
        status = get_cached_status_data()

        current_status = (
            status.get("status", "UNKNOWN")
            if isinstance(status, dict)
            else "UNKNOWN"
        )

        if current_status != last_monitor_status():
            last_monitor_status.set(current_status)

            if current_status == "ONLINE":
                log.info("Monitor: ONLINE")
            else:
                log.warning(f"Monitor: {current_status}")

    except Exception as error:
        log.error(f"Status Logic Error: {error}", exc_info=True)
