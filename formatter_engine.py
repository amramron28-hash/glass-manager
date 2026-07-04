Enterimport json

class DataFormatter:
    # يمكنك إضافة أي مفتاح لا ترغب بظهوره هنا
    BLACKLIST = ["_id", "internal_meta", "debug_trace"]
    
    @staticmethod
    def is_valid_value(v):
        # يتأكد أن القيمة ليست None أو فارغة (مع السماح بـ 0 و False)
        return v is not None and v not in [[], {}]

    @classmethod
    def clean_data(cls, data: dict):
        if not isinstance(data, dict): return {}
        # يقوم بتصفية البيانات بناءً على الـ Blacklist
        return {k: v for k, v in data.items() if k not in cls.BLACKLIST and cls.is_valid_value(v)}

    @staticmethod
    def serialize(val, max_items=10):
        # يحول أي قيمة لـ string آمن للعرض
        try:
            if isinstance(val, (dict, list)):
                if isinstance(val, list) and len(val) > max_items:
                    return f"{json.dumps(val[:max_items], ensure_ascii=False)}... (مقتطع)"
                return json.dumps(val, ensure_ascii=False, default=str)
            return str(val)
        except:
            return "بيانات غير قابلة للعرض"
