"""
خدمة الحفظ والتحقق الموحدة
"""
from core.logger import get_logger
from services.cache_service import workflow_cache, coords_cache
from database import add_model
from silent_monitor import refresh

log = get_logger("save_service")

def perform_save(phone: str, size: str, panel: str, sensor: str, action_name: str) -> bool:
    """
    التحقق من البيانات، منع التكرار، الحفظ، وتحديث الكاش.
    
    Returns:
        True إذا نجحت العملية
    """
    if not all([phone, size, panel, sensor]):
        log.warning(f"[SAVE] {action_name} aborted: Missing data")
        return False

    try:
        # TODO: إضافة تحقق من التكرار هنا إذا لزم الأمر
        # from silent_monitor import get_database
        # db = get_database() ... check duplicate
        
        log.info(f"[SAVE] Starting {action_name} for: {phone}")
        
        if add_model(size, panel, sensor, phone):
            refresh()
            workflow_cache.invalidate()
            coords_cache.invalidate()
            log.info(f"[SAVE] {action_name} succeeded: {phone}")
            return True
        else:
            log.error(f"[SAVE] {action_name} failed: {phone}")
            return False
            
    except Exception as e:
        log.error(f"[SAVE] {action_name} exception: {e}")
        return False
