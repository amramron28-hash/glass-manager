import json
import urllib.request

# 🌐 روابط الاتصال الجغرافي المباشر بمشروعك السحابي
URL = "https://supabase.co"
KEY = "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX"

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}

# 🛠️ معالج مخصص لالتقاط طلبات التوجيه الجغرافي 307 وتمرير الـ POST/GET بأمان وثبات
class SupabaseRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_307(self, req, fp, code, msg, hdrs):
        new_url = hdrs.get('Location') or hdrs.get('location')
        if new_url:
            new_req = urllib.request.Request(new_url, data=req.data, headers=req.headers, method=req.get_method())
            return self.parent.open(new_req)
        return urllib.request.HTTPRedirectHandler.http_error_307(self, req, fp, code, msg, hdrs)

opener = urllib.request.build_opener(SupabaseRedirectHandler)

def add_model(size, panel, sensor, model):
    """إضافة موديل هاتف جديد سحابياً بدقة متناهية"""
    if not all([size, panel, sensor, model]): return False
    payload = {
        "size": str(size).strip(),
        "panel": str(panel).strip(),
        "sensor": str(sensor).strip(),
        "model_name": str(model).strip()
    }
    try:
        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(URL, data=data_bytes, headers=headers, method='POST')
        with opener.open(req) as response:
            return 200 <= response.getcode() < 300
    except Exception:
        return False

def load_db():
    """جلب الأجهزة من السحابة لتعبئة واجهة Streamlit والمؤشرات الحية"""
    try:
        req = urllib.request.Request(f"{URL}?select=*", headers=headers, method='GET')
        with opener.open(req) as response:
            if response.getcode() == 200:
                rows = json.loads(response.read().decode('utf-8'))
                return rows if rows else []
    except Exception:
        pass
    return []
