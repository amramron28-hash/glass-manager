# services/__init__.py

from .cache_service import workflow_cache, coords_cache, index_cache, get_cache_stats
from .database_service import load_models_index, convert_database_from_raw
from .fuzzy_service import fuzzy_find
from .index_service import build_fast_index, extract_panels_sensors
from .search_service import build_autocomplete_index, find_model_coords
from .plan_engine import compute_plan_matches, is_empty_result, validate_plan_inputs, get_unique_models_from_results
from .plan_controller import process_plan
from .save_service import perform_save
from .reset_service import reset_ui
from .modal_service import build_add_panel_modal, build_add_sensor_modal
from .modal_handlers import (
    handle_show_add_panel,
    handle_show_add_sensor,
    confirm_add_panel,
    confirm_add_sensor,
    cancel_add
)

# تصحيح مسارات استدعاء الخدمات المضافة حديثاً لتطابق أسماء الملفات الفعلية بدقة
from .service_watcher import execute_refresh_logic, execute_status_logic
from .search_controller import process_search_query

__all__ = [
    "workflow_cache",
    "coords_cache",
    "index_cache",
    "get_cache_stats",
    "load_models_index",
    "convert_database_from_raw",
    "fuzzy_find",
    "build_fast_index",
    "extract_panels_sensors",
    "build_autocomplete_index",
    "find_model_coords",
    "compute_plan_matches",
    "is_empty_result",
    "validate_plan_inputs",
    "get_unique_models_from_results",
    "process_plan",
    "perform_save",
    "reset_ui",
    "build_add_panel_modal",
    "build_add_sensor_modal",
    "handle_show_add_panel",
    "handle_show_add_sensor",
    "confirm_add_panel",
    "confirm_add_sensor",
    "cancel_add",
    "execute_refresh_logic",
    "execute_status_logic",
    "process_search_query",
]
