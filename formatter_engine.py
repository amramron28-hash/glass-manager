import logging

logger = logging.getLogger("DataFormatter")

class DataFormatter:
    def __init__(self, max_depth=3, max_list_items=10, strict_mode=False, max_total_nodes=1000):
        self.MAX_DEPTH = max_depth
        self.MAX_LIST_ITEMS = max_list_items
        self.STRICT_MODE = strict_mode
        self.MAX_TOTAL_NODES = max_total_nodes

        self.WHITELIST = ["coords", "compatibles", "status", "type"]
        self.BLACKLIST = ["_id", "internal_meta", "debug_trace"]

    # =========================
    # Validation Layer
    # =========================
    def is_valid(self, v):
        if self.STRICT_MODE:
            if v in [None, [], {}]:
                return False
        return v is not None

    # =========================
    # Clean Layer (Pure Transform)
    # =========================
    def clean_data(self, data: dict):
        if not isinstance(data, dict):
            logger.error("clean_data: input must be dict")
            return {}

        def _clean(item):
            if isinstance(item, dict):
                return {
                    k: _clean(v)
                    for k, v in item.items()
                    if k not in self.BLACKLIST and self.is_valid(v)
                }

            if isinstance(item, list):
                return [
                    _clean(i)
                    for i in item
                    if self.is_valid(i)
                ]

            return item

        cleaned = _clean(data)

        return dict(
            sorted(
                cleaned.items(),
                key=lambda x: (x[0] not in self.WHITELIST, x[0])
            )
        )

    # =========================
    # Serialization Layer (Safe + Controlled)
    # =========================
    def serialize(self, val, depth=0, visited=None, node_count=None, path=()):
        if visited is None:
            visited = set()

        if node_count is None:
            node_count = [0]

        node_count[0] += 1

        if node_count[0] > self.MAX_TOTAL_NODES:
            return "...(node limit exceeded)"

        # Depth limit
        if depth >= self.MAX_DEPTH:
            return "...(max depth reached)"

        # Complex structures
        if isinstance(val, (dict, list)):
            obj_id = id(val)

            if obj_id in visited:
                logger.warning("Circular reference detected at path: %s", "->".join(map(str, path)))
                return "...(circular ref)"

            visited.add(obj_id)

            try:
                if isinstance(val, dict):
                    return {
                        str(k): self.serialize(
                            v,
                            depth + 1,
                            visited,
                            node_count,
                            path + (k,)
                        )
                        for k, v in val.items()
                        if self.is_valid(v)
                    }

                if isinstance(val, list):
                    truncated = val[:self.MAX_LIST_ITEMS]

                    result = [
                        self.serialize(
                            i,
                            depth + 1,
                            visited,
                            node_count,
                            path + (str(idx),)
                        )
                        for idx, i in enumerate(truncated)
                    ]

                    if len(val) > self.MAX_LIST_ITEMS:
                        result.append(f"...(+{len(val) - self.MAX_LIST_ITEMS} more)")

                    return result

            finally:
                visited.remove(obj_id)

        # Primitive values
        s = str(val)
        return (s[:200] + "...") if len(s) > 200 else s
