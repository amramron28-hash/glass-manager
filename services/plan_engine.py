from typing import Dict, List, Set, Tuple


def compute_plan_matches(
    fast_index: Dict[Tuple[str, str], Dict[str, Set[str]]],
    panel: str,
    sensor: str,
    source_size: str,
    target_size: str,
) -> List[str]:
    """
    حساب الموديلات المشتركة بين مقاسين لنفس نوع الـ Panel والـ Sensor.

    Parameters
    ----------
    fast_index : dict
        الفهرس السريع الناتج عن build_fast_index().
    panel : str
        نوع الشاشة.
    sensor : str
        نوع الحساس.
    source_size : str
        المقاس الأول.
    target_size : str
        المقاس الثاني.

    Returns
    -------
    list[str]
        قائمة الموديلات المشتركة مرتبة أبجديًا.
    """

    key = (panel, sensor)

    if key not in fast_index:
        return []

    size_map = fast_index[key]

    source_models = size_map.get(source_size, set())
    target_models = size_map.get(target_size, set())

    return sorted(source_models & target_models)


def is_empty_result(result: List[str]) -> bool:
    """
    التحقق مما إذا كانت نتيجة البحث فارغة.
    """
    return len(result) == 0
