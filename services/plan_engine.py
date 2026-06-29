from typing import Dict, List, Optional, Tuple, Set
from services.index_service import build_fast_index
from logic_engine import extract_numeric_size
from core.logger import get_logger

log = get_logger("plan_engine")

TOLERANCE = 0.05  # حد التفاوت المسموح به في المقاسات


def compute_plan_matches(
    size_val: str,
    panel_val: str,
    sensor_val: str,
    db: Dict,
    fast_index: Optional[Dict] = None
) -> Dict[str, List[str]]:
    """
    حساب نتائج المطابقة الفنية باستخدام الفهرس السريع.
    
    Args:
        size_val: المقاس المطلوب
        panel_val: نوع الشاشة
        sensor_val: نوع المستشعر
        db: قاعدة البيانات الكاملة
        fast_index: الفهرس السريع (اختياري - سيتم بناؤه إذا لم يُمرر)
        
    Returns:
        Dict: {"exact": [...], "plus": [...], "minus": [...]}
    """
    empty = {"exact": [], "plus": [], "minus": []}
    
    if not all([size_val, panel_val, sensor_val]):
        log.warning("Plan computation attempted with missing parameters")
        return empty
    
    target_val = extract_numeric_size(str(size_val))
    if target_val is None:
        log.warning(f"Invalid size value: {size_val}")
        return empty
    
    # بناء الفهرس إذا لم يُمرر
    if fast_index is None:
        fast_index = build_fast_index(db)
    
    results = {"exact": [], "plus": [], "minus": []}
    group_key = (panel_val, sensor_val)
    
    if group_key not in fast_index:
        log.info(f"No matches found for group: {group_key}")
        return results
    
    size_map = fast_index[group_key]
    
    for s_key, models_set in size_map.items():
        s_val = extract_numeric_size(s_key)
        if s_val is None:
            continue
        
        diff = s_val - target_val
        
        # تحويل الـ set إلى list للتعامل معه
        models_list = list(models_set) if isinstance(models_set, set) else models_set
        
        for model in models_list:
            if abs(diff) < 0.001:
                if model not in results["exact"]:
                    results["exact"].append(model)
            elif 0 < diff <= TOLERANCE:
                if model not in results["plus"]:
                    results["plus"].append(model)
            elif -TOLERANCE <= diff < 0:
                if model not in results["minus"]:
                    results["minus"].append(model)
    
    total_matches = sum(len(v) for v in results.values())
    log.info(f"Plan matches computed: {total_matches} total "
             f"(exact: {len(results['exact'])}, plus: {len(results['plus'])}, minus: {len(results['minus'])})")
    
    return results


def is_empty_result(results: Dict[str, List[str]]) -> bool:
    """التحقق من أن النتائج فارغة"""
    return not any(results.values())


def get_unique_models_from_results(results: Dict[str, List[str]]) -> Set[str]:
    """
    استخراج جميع الموديلات الفريدة من نتائج المطابقة.
    مفيد لإزالة التكرارات عند الدمج.
    """
    unique = set()
    for category in results.values():
        unique.update(category)
    return unique


def validate_plan_inputs(
    size_val: str,
    panel_val: str,
    sensor_val: str
) -> Tuple[bool, Optional[str]]:
    """
    التحقق من صحة مدخلات الخطة.
    
    Returns:
        Tuple: (is_valid, error_message)
    """
    if not size_val:
        return False, "المقاس مطلوب"
    if not panel_val:
        return False, "نوع الشاشة مطلوب"
    if not sensor_val:
        return False, "المستشعر مطلوب"
    
    target_val = extract_numeric_size(str(size_val))
    if target_val is None:
        return False, f"المقاس غير صالح: {size_val}"
    
    return True, None
