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
    def __init__(self):
        self.root = TrieNode()
        self.size = 0
    
    def insert(self, model: str) -> None:
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
        node = self.root
        key = prefix.lower()
        for char in key:
            if char not in node.children:
                return []
            node = node.children[char]
        
        results: List[str] = []
        self._collect(node, results, limit)
        return results
    
    def _collect(self, node: TrieNode, results: List[str], limit: int) -> None:
        if len(results) >= limit: return
        if node.is_end:
            for m in node.models:
                if m not in results:
                    results.append(m)
                    if len(results) >= limit: break
        for child in node.children.values():
            self._collect(child, results, limit)
            if len(results) >= limit: break

def build_autocomplete_index(models_list: List) -> AutoCompleteIndex:
    """بناء الفهرس: تم التصحيح ليتعامل مع قائمة القواميس."""
    index = AutoCompleteIndex()
    for item in models_list:
        # استخراج اسم الموديل بدقة
        model_name = item.get("model") if isinstance(item, dict) else item
        if isinstance(model_name, str) and model_name.strip():
            index.insert(model_name.strip())
    
    log.info(f"Built Trie index with {index.size} models")
    return index

def find_model_coords(db: Dict, phone_name: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """البحث عن الإحداثيات (يعمل مع الهيكل الشجري السابق)"""
    if not phone_name or not db: return None, None, None, None
    search = phone_name.strip().lower()
    
    # محاولة التطابق
    for size, panels in db.items():
        if not isinstance(panels, dict): continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict): continue
            for sensor, data in sensors.items():
                models = data.get("models", []) if isinstance(data, dict) else []
                for model in models:
                    if isinstance(model, str) and model.strip().lower() == search:
                        return size, panel, sensor, model
    return None, None, None, None

