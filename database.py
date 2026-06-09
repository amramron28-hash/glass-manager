import json
import os
import requests
import streamlit as st

# 🔗 الرابط الصافي والصحيح بنسبة 100% لملف المقاسات الخاص بك على جيت هاب
GITHUB_URL = "https://githubusercontent.com"

@st.cache_data(ttl=600)  # حفظ البيانات بالرام لمدة 10 دقائق لتسريع التصفح الصاروخي ومنع البطء
def get_db_data():
    """جلب شجرة المقاسات والموديلات مباشرة من سحاب GitHub بأعلى سرعة مع نسخة احتياطية محلية"""
    try:
        res = requests.get(GITHUB_URL, timeout=5)
        if res.status_code == 200:
            content = res.json()
            if isinstance(content, dict) and "data" in content: 
                return content["data"]
            return content
    except: 
        pass  # في حال ضعف أو انقطاع الإنترنت، ينتقل النظام تلقائياً وبصمت للنسخة الاحتياطية أدناه
        
    if os.path.exists("models_db.json"):
        with open("models_db.json", "r", encoding="utf-8") as f:
            content = json.load(f)
            if isinstance(content, dict) and "data" in content: 
                return content["data"]
            return content
    return {}

def load_db():
    data = get_db_data()
    return {"metadata": {"version": 1}, "data": data}

def save_db(data):
    try:
        with open("models_db.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except: 
        return False

def get_all_models(data):
    """فهرسة وتجميع آلاف الموديلات مرة واحدة في الذاكرة الحية لتسريع البحث اللحظي"""
    all_models = []
    if isinstance(data, dict):
        for sz, screens in data.items():
            if sz in ["system_notifications", "metadata", "data"]: continue
            if isinstance(screens, dict):
                for scr, sensors in screens.items():
                    if isinstance(sensors, dict):
                        for sns, models in sensors.items():
                            if isinstance(models, list): 
                                all_models.extend(models)
    return sorted(list(set(all_models)))

def google_prefix_search(text, all_models):
    """البحث الذكي الصاروخي: تصفية وقراءة الحرف الأول فوراً على طريقة جوجل"""
    if not text: 
        return []
    search_term = text.lower().strip()
    starts_with_list = [m for m in all_models if m.lower().strip().startswith(search_term)]
    contains_list = [m for m in all_models if search_term in m.lower().strip() and not m.lower().strip().startswith(search_term)]
    return starts_with_list + contains_list

# 🌟 الدوال المصححة لمركز التنبيهات لكي يعمل المراقب الصامت بدون انهيار
def get_notifications():
    """جلب التنبيهات النشطة لعرضها في القائمة الجانبية للتطبيق"""
    if os.path.exists("notifications.json"):
        try:
            with open("notifications.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def add_notification(message):
    """إضافة تنبيه جديد من المراقب الصامت لحفظ سجل الأحداث"""
    notes = get_notifications()
    if message not in notes:
        notes.insert(0, message)  # وضع التنبيه الأحدث في الأعلى دائماً
        try:
            with open("notifications.json", "w", encoding="utf-8") as f:
                json.dump(notes[:20], f, ensure_ascii=False, indent=4)  # الاحتفاظ بآخر 20 تنبيه فقط للخفة
        except:
            pass

def clear_notifications():
    """مسح سجل التنبيهات"""
    try:
        if os.path.exists("notifications.json"):
            os.remove("notifications.json")
    except:
        pass
