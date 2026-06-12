import json
import os
import requests
import streamlit as st

# ==============================================================================
# 🌐 إعدادات الاتصال السحابي بمستودع GitHub الخاص بك (تحديث تلقائي دائم)
# ==============================================================================
# يتم سحب الـ Token السري بشكل آمن من إعدادات Streamlit Secrets لحماية حسابك
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO_OWNER = "amramran29-hash"
REPO_NAME = "glass-manager"
FILE_PATH = "models_db.json"

# الروابط الرسمية للجلب والتحديث عبر GitHub API
RAW_URL = f"https://githubusercontent.com{REPO_OWNER}/{REPO_NAME}/main/{FILE_PATH}"
API_URL = f"https://github.com{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

# مسار الملف الاحتياطي المحلي في حال انقطاع السيرفر السحابي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'models_db.json')

def load_db():
    """ تحميل قاعدة البيانات مباشرة من سحاب GitHub الصافي كقاموس مباشر ومستقر في الـ RAM """
    try:
        # محاولة جلب النسخة الأحدث حياً من مستودع جيت هاب مباشرة
        res = requests.get(RAW_URL, timeout=4)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                # حفظ نسخة احتياطية محلياً لتأمين النظام عند الطوارئ
                with open(DB_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return data
    except Exception:
        pass  # في حال ضعف الإنترنت أو صيانة السيرفر، يسقط النظام تلقائياً للنسخة المحلية أدناه

    # القراءة من النسخة الاحتياطية المحلية
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}

def save_db(data):
    """ حفظ القاموس المتداخل محلياً + رفعه وعمل Commit تلقائي ومباشر داخل مستودع GitHub للأبد """
    # 1. حفظ الملف محلياً أولاً لتأمين العملية
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"خطأ في الحفظ المحلي الاحتياطي: {e}")

    # 2. إذا لم يتم إعداد الـ GITHUB_TOKEN في السيرفر، يكتفي بالحفظ المحلي المؤقت
    if not GITHUB_TOKEN:
        print("⚠️ تحذير: GITHUB_TOKEN غير معرف. تم الحفظ محلياً فقط وسيتلاشى عند إعادة تشغيل السيرفر.")
        return True

    # 3. دفع التحديث مباشرة إلى GitHub عبر الـ API لضمان عدم اختفاء الهواتف
    try:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # جلب الـ SHA الخاص بالملف الحالي (مطلوب من جيت هاب لتأكيد عملية التعديل)
        sha = ""
        get_res = requests.get(API_URL, headers=headers, timeout=5)
        if get_res.status_code == 200:
            sha = get_res.json().get("sha", "")

        # تجهيز البيانات والرسالة المشفرة للـ Commit السحابي
        content_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        content_base64 = base64_encode_string(content_bytes)
        
        payload = {
            "message": "🔄 تحديث تلقائي سحابي: إضافة هاتف جديد عبر السيستم",
            "content": content_base64,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha

        # إرسال طلب التحديث الفوري للسيرفر
        put_res = requests.put(API_URL, headers=headers, json=payload, timeout=5)
        if put_res.status_code in:
            add_notification("⚙️ تم رفع الموديل الجديد بنجاح ومزامنة شجرة البيانات سحابياً للأبد.")
            return True
    except Exception as e:
        print(f"فشلت المزامنة السحابية مع GitHub: {e}")
        
    return True

def base64_encode_string(bytes_data):
    """ دالة مساعدة لتشفير الملف برمجياً قبل إرساله لـ GitHub API """
    import base64
    return base64.b64encode(bytes_data).decode('utf-8')

# ==========================================
# 🌟 دمج وإصلاح مركز التنبيهات ليعمل المراقب الصامت حياً
# ==========================================
def get_notifications():
    """ جلب التنبيهات الحية المسجلة بنظام المراقب """
    if os.path.exists("notifications.json"):
        try:
            with open("notifications.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def add_notification(message):
    """ حقن تنبيه جديد في سجل الأحداث وربطه بلوحة التحكم الجانبية """
    notes = get_notifications()
    if message not in notes:
        notes.insert(0, message)
        try:
            with open("notifications.json", "w", encoding="utf-8") as f:
                json.dump(notes[:20], f, ensure_ascii=False, indent=2)
        except Exception:
            pass
