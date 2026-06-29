from typing import Any, Callable, Dict, Tuple, Optional
import time
from core.logger import get_logger

log = get_logger("cache_service")


class ResultCache:
    """
    تخزين مؤقت ذكي للنتائج الثقيلة مع دعم invalidation يدوي و TTL.
    يُستخدم لتجنب إعادة حساب العمليات المكلفة مثل run_system_workflows.
    """
    
    def __init__(self):
        self._cache: Dict[Tuple, Any] = {}
        self._timestamps: Dict[Tuple, float] = {}
        self._version = 0
    
    def invalidate(self) -> None:
        """مسح الكاش بالكامل (يُستدعى عند تحديث قاعدة البيانات)"""
        old_count = len(self._cache)
        self._cache.clear()
        self._timestamps.clear()
        self._version += 1
        log.info(f"Cache invalidated: {old_count} entries cleared, new version: {self._version}")
    
    def get_or_compute(
        self, 
        key: Tuple, 
        compute_fn: Callable, 
        ttl: Optional[int] = None
    ) -> Any:
        """
        جلب من الكاش أو حساب وتخزين جديد.
        
        Args:
            key: مفتاح التخزين الفريد
            compute_fn: الدالة التي تحسب القيمة إذا لم تكن موجودة
            ttl: وقت الصلاحية بالثواني (اختياري، لا نهائي إذا لم يُحدد)
            
        Returns:
            القيمة المخزنة أو المحسوبة حديثاً
        """
        cache_key = (self._version, key)
        now = time.time()
        
        # التحقق من وجود القيمة وصلاحيتها
        if cache_key in self._cache:
            if ttl is None:
                return self._cache[cache_key]
            
            timestamp = self._timestamps.get(cache_key, 0)
            if now - timestamp < ttl:
                log.debug(f"Cache hit for key: {key}")
                return self._cache[cache_key]
            else:
                log.debug(f"Cache expired for key: {key}")
                del self._cache[cache_key]
                if cache_key in self._timestamps:
                    del self._timestamps[cache_key]
        
        # حساب القيمة الجديدة وتخزينها
        log.debug(f"Cache miss for key: {key}, computing...")
        value = compute_fn()
        self._cache[cache_key] = value
        self._timestamps[cache_key] = now
        
        log.info(f"Cached new value for key: {key}")
        return value
    
    def clear_expired(self, default_ttl: int = 300) -> int:
        """مسح القيم منتهية الصلاحية فقط"""
        now = time.time()
        expired_keys = [
            k for k, t in self._timestamps.items() 
            if now - t >= default_ttl
        ]
        
        for k in expired_keys:
            del self._cache[k]
            del self._timestamps[k]
        
        if expired_keys:
            log.info(f"Cleared {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, int]:
        """إحصائيات حالة الكاش"""
        return {
            "total_entries": len(self._cache),
            "version": self._version
        }


# Instances عامة جاهزة للاستيراد المباشر في server.py
workflow_cache = ResultCache()
coords_cache = ResultCache()
index_cache = ResultCache()


def get_cache_stats() -> Dict[str, Dict[str, int]]:
    """الحصول على إحصائيات جميع الكاشات مرة واحدة"""
    return {
        "workflow": workflow_cache.stats(),
        "coords": coords_cache.stats(),
        "index": index_cache.stats()
    }
