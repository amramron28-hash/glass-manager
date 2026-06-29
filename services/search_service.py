from typing import List, Dict, Optional, Tuple
from core.logger import get_logger

log = get_logger("search_service")


class TrieNode:
    """عقدة في شجرة Trie للبحث السريع"""
    __slots__ = ("children", "is_end", "models")
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end: bool = False
        self.models: List[str] = []


class AutoCompleteIndex:
    """
    فهرس الإكمال التلقائي باستخدام Trie.
    يوفر بحث سريع O(k) حيث k طول الاستعلام.
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.size = 0
    
    def insert(self, model: str) -> None:
        """إدخال موديل جديد في الشجرة"""
        node = self.root
        key = model.lower()
        
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end = True
        if model not in node.models:
            node.models.append(model)
            self.size += 1
    
    def search_prefix(self, prefix: str, limit: int = 10) -> List[str]:
        """
        البحث عن كل الموديلات التي تبدأ بالبادئة المعطاة.
        يُرجع قائمة بحد أقصى limit من النتائج.
        """
        node = self.root
        key = prefix.lower()
        
        # الوصول إلى عقدة نهاية البادئة
        for char in key:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # جمع كل الموديلات تحت هذه العقدة (DFS)
        results: List[str] = []
        self._collect(node, results, limit)
        return results
    
    def _collect(self, node: TrieNode, results: List[str], limit: int) -> None:
        """جمع الموديلات بشكل متكرر من الشجرة"""
        if len(results) >= limit:
            return
        
        if node.is_end:
            results.extend(m for m in node.models if m not in results)
            if len(results) >= limit:
                return
        
        for child in node.children.values():
            self._collect(child, results, limit)
            if len(results) >= limit:
                return
    
    def contains_exact(self, query: str) -> bool:
        """التحقق من وجود تطابق تام (case-insensitive)"""
        node = self.root
        
        for char in query.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        
        return node.is_end


def build_autocomplete_index(models_list: List[str]) -> AutoCompleteIndex:
    """
    بناء فهرس Trie من قائمة الموديلات.
    
    Args:
        models_list: قائمة من أسماء الموديلات
        
    Returns:
        AutoCompleteIndex جاهز للاستخدام
    """
    index = AutoCompleteIndex()
    
    for model in models_list:
        if isinstance(model, str) and model.strip():
            index.insert(model.strip())
    
    log.info(f"Built Trie index with {index.size} models")
    return index


def find_model_coords(db: Dict, phone_name: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    البحث عن إحداثيات الموديل في قاعدة البيانات.
    
    Args:
        db: قاعدة البيانات (هيكلية شجرية)
        phone_name: اسم الهاتف للبحث عنه
        
    Returns:
        Tuple: (size, panel, sensor, real_name) أو (None, None, None, None) إذا لم يُعثر عليه
    """
    if not phone_name or not db:
        return None, None, None, None
    
    search = phone_name.strip().lower()
    
    # البحث عن تطابق تام أولاً
    for size, panels in db.items():
        if not isinstance(panels, dict):
            continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict):
                continue
            for sensor, data in sensors.items():
                models = data.get("models", []) if isinstance(data, dict) else []
                for model in models:
                    if isinstance(model, str) and model.strip().lower() == search:
                        return size, panel, sensor, model
    
    # البحث عن تطابق جزئي كاحتياط
    for size, panels in db.items():
        if not isinstance(panels, dict):
            continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict):
                continue
            for sensor, data in sensors.items():
                models = data.get("models", []) if isinstance(data, dict) else []
                for model in models:
                    if isinstance(model, str) and search in model.strip().lower():
                        return size, panel, sensor, model
    
    return None, None, None, None
