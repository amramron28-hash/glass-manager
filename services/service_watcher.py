# services/service_watcher.py

from core.logger import get_logger
from .database_service import load_models_index
from .index_service import extract_panels_sensors
from .search_service import build_autocomplete_index

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
    """منطق تحديث الفهارس المعتمد على models_db.json"""
    try:
        # تحميل البيانات المحدثة مباشرة من ملف JSON عبر database_service
        new_models_list = load_models_index() or []
        
        # إذا كانت القائمة فارغة، قم بتصفير الفهارس
        if not new_models_list:
            autocomplete_index.set(None)
            models_index.set([])
            return

        # تحقق مما إذا كانت البيانات قد تغيرت فعلياً قبل إعادة بناء الفهارس (لتحسين الأداء)
        if autocomplete_index() is None or len(new_models_list) != len(models_index()):
            models_index.set(new_models_list)
            
            # بناء الفهرس الذكي (AutoComplete) بناءً على القائمة المسطحة
            autocomplete_index.set(build_autocomplete_index(new_models_list))

            # استخراج الخيارات (Panels/Sensors) من البيانات الخام
            raw_db = database_data()
            panels, sensors = extract_panels_sensors(raw_db)
            custom_panels.set(panels)
            custom_sensors.set(sensors)

            # إعادة تعيين سير العمل
            invalidate_workflow_fn()

        # تحديث الاقتراحات إذا كان مربع البحث مفتوحاً
        if show_curtain():
            trie = autocomplete_index()
            query = current_phone()
            if trie and query:
                suggestions_list.set(trie.search_prefix(query, 10))

    except Exception as error:
        log.error(f"Refresh Logic Error: {error}", exc_info=True)


def execute_status_logic(get_cached_status_data, last_monitor_status):
    """التحقق من حالة النظام"""
    try:
        # هنا سنعتمد على أن الخدمة تعمل طالما أن الملفات متاحة
        import os
        is_online = os.path.exists("models_db.json")
        current_status = "ONLINE" if is_online else "OFFLINE"

        if current_status != last_monitor_status():
            last_monitor_status.set(current_status)
            log.info(f"Monitor Status: {current_status}")
    except Exception as error:
        log.error(f"Status Logic Error: {error}", exc_info=True)
