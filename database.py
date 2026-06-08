import json
import os
import requests
import streamlit as st

# الرابط المباشر لملف قاعدة البيانات في مستودعك لضمان توفير مساحة السيرفر والهاتف
GITHUB_URL = "https://githubusercontent.com"

@st.cache_data(ttl=600)  # تخزين مؤقت لمدة 10 دقائق في الرام لمنع تكرار طلبات الإنترنت الثقيلة
def get_db_data():
    """جلب شجرة المقاسات والموديلات مباشرة من سحاب GitHub بأعلى سرعة"""
    try:
        res = requests.get(GITHUB_URL, timeout=5)
        if res.status_code == 200:
            content = res.json()
            if isinstance(content, dict) and "data" in content:
                return content["data"]
            return content
    except:
        pass
    
    # حل احتياطي سريع في حال انقطاع اتصال المتصفح المؤقت
    if os.path.exists("models_db.json"):
        with open("models_db.json", "r", encoding="utf-8") as f:
            content = json.load(f)
            if isinstance(content, dict) and "data" in content:
                return content["data"]
            return content
    return {}

def get_all_models(data):
    """فهرسة وتجميع آلاف الموديلات مرة واحدة في الذاكرة الحية لتسريع البحث"""
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
