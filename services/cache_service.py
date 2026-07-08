from __future__ import annotations

import time
from typing import Any, Dict, Optional


class ResultCache:
    """
    ذاكرة تخزين مؤقت بسيطة (TTL Cache) لنتائج العمليات المتكررة.
    """

    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        استرجاع قيمة من الكاش إذا كانت لا تزال صالحة.
        """
        item = self._cache.get(key)

        if item is None:
            return None

        if time.time() - item["timestamp"] > self.ttl_seconds:
            del self._cache[key]
            return None

        return item["value"]

    def set(self, key: str, value: Any) -> None:
        """
        حفظ قيمة داخل الكاش.
        """
        self._cache[key] = {
            "value": value,
            "timestamp": time.time(),
        }

    def invalidate(self, key: str) -> None:
        """
        حذف عنصر محدد من الكاش.
        """
        self._cache.pop(key, None)

    def clear(self) -> None:
        """
        حذف جميع العناصر.
        """
        self._cache.clear()

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __len__(self) -> int:
        return len(self._cache)


# كاش عام للاستخدام في التطبيق
workflow_cache = ResultCache(ttl_seconds=300)
coords_cache = ResultCache(ttl_seconds=300)
