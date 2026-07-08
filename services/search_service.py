from typing import Dict, List, Optional


class TrieNode:
    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.models: List[str] = []
        self.is_end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, model: str):
        """
        إدراج موديل داخل شجرة Trie.
        """
        if not model:
            return

        node = self.root
        key = model.lower().strip()

        for ch in key:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]

        node.is_end = True
        node.models.append(model)

    def search(self, prefix: str, limit: int = 20) -> List[str]:
        """
        البحث عن الموديلات التي تبدأ بالمقدمة المحددة.
        """
        if not prefix:
            return []

        node = self.root
        prefix = prefix.lower().strip()

        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        results: List[str] = []
        self._collect(node, results, limit)
        return sorted(results)[:limit]

    def _collect(self, node: TrieNode, results: List[str], limit: int):
        if len(results) >= limit:
            return

        if node.is_end:
            results.extend(node.models)

        for child in node.children.values():
            if len(results) >= limit:
                break
            self._collect(child, results, limit)


def build_autocomplete_index(models: List[str]) -> Trie:
    """
    بناء فهرس الإكمال التلقائي.
    """
    trie = Trie()

    for model in models:
        if isinstance(model, str):
            trie.insert(model)

    return trie


def find_model_coords(database: Dict, model_name: str) -> Optional[Dict]:
    """
    البحث عن إحداثيات موديل داخل قاعدة البيانات.
    """
    if not database or not model_name:
        return None

    target = model_name.strip().lower()

    for size, panels in database.items():
        if not isinstance(panels, dict):
            continue

        for panel, sensors in panels.items():
            if not isinstance(sensors, dict):
                continue

            for sensor, data in sensors.items():
                models = data.get("models", []) if isinstance(data, dict) else []

                for model in models:
                    if model.strip().lower() == target:
                        return {
                            "model": model,
                            "size": size,
                            "panel": panel,
                            "sensor": sensor,
                        }

    return None
