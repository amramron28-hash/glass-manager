import json
import os
import requests
import streamlit as st

# =========================
# 🌐 مصادر البيانات (HF + GitHub)
# =========================

HUGGINGFACE_URL = "https://huggingface.co/datasets/YOUR_USERNAME/YOUR_REPO/resolve/main/models_db.json"

GITHUB_RAW_URL = "https://raw.githubusercontent.com/amramron28-hash/glass-manager/main/models_db.json"

# =========================
# 💾 ملف النسخة المحلية
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "models_db.json")

# =========================
# 🔧 تحميل من رابط
# =========================

def load_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

# =========================
# 📥 تحميل قاعدة البيانات
# =========================

def load_db():
    """
    تحميل قاعدة البيانات بترتيب ذكي:
    1. Hugging Face (أساسي)
    2. GitHub (احتياطي)
    3. Local (إنقاذ)
    """

    # 🔵 1. Hugging Face
    data = load_from_url(HUGGINGFACE_URL)
    if isinstance(data, dict):
        _save_local_backup(data)
        return data

    # 🟡 2. GitHub
    data = load_from_url(GITHUB_RAW_URL)
    if isinstance(data, dict):
        _save_local_backup(data)
        return data

    # 🔴 3. Local fallback
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass

    return {}

# =========================
# 💾 حفظ نسخة محلية
# =========================

def _save_local_backup(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# =========================
# 💾 حفظ التعديلات محلياً
# =========================

def save_db(data):
    try:
        _save_local_backup(data)
        return True
    except Exception:
        return False

# =========================
# 🔔 نظام الإشعارات (Streamlit)
# =========================

def add_notification(message, level="info"):
    if "notifications" not in st.session_state:
        st.session_state["notifications"] = []

    st.session_state["notifications"].append({
        "message": message,
        "level": level
    })