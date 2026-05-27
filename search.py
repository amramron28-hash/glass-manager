import streamlit as st
import json
import os

# إعدادات الصفحة الاحترافية المظلمة لـ AMMAR TELECOM PRO
st.set_page_config(page_title="AMMAR TELECOM PRO", page_icon="📱", layout="centered")

# تطبيق ثيم مظلم مخصص
st.markdown("""
    <style>
    .stApp { background-color: #0b111e; color: #ffffff; }
    .stTextInput>div>div>input { background-color: #172237; color: white; border: 1px solid #2563eb; border-radius: 8px; }
    .card { background-color: #172237; border-left: 5px solid #2563eb; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .card-title { color: #3b82f6; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    .card-meta { color: #9ca3af; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 AMMAR TELECOM PRO")
st.subheader("محرك البحث الذكي للموديلات المتوافقة فيزيائياً لعام 2026")

# دالة تحميل قاعدة البيانات
def load_db():
    db_path = "models_db.json"
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

db = load_db()

# خانة البحث الذكي
search_query = st.text_input("أدخل اسم الموديل أو الحروف الأولى منه (مثال: c35 أو a15):").strip().lower()

if search_query:
    found_models = []
    group_title = ""
    
    # البحث المطور: التحقق من انتماء التوكن لأي مجموعة
    for group_id, group_data in db.items():
        models_list = group_data.get("compatible_models", [])
        # إذا تطابق البحث مع أي موديل داخل المجموعة
        if any(search_query in model.lower() for model in models_list):
            found_models = models_list
            group_title = group_data.get("group_name", "مجموعة متوافقة")
            break # جلب المجموعة كاملة فوراً دون نقصان
            
    if found_models:
        st.success(f"🔍 تم العثور على: {group_title} (تضم {len(found_models)} موديلاً متوافقاً)")
        
        # عرض الموديلات الـ 60 كاملة في بطاقات عمودية مستقلة تماماً وقابلة للتمرير طويلاً
        for model in found_models:
            st.markdown(f"""
                <div class="card">
                    <div class="card-title">📱 {model}</div>
                    <div class="card-meta">لاصق الحماية متوافق فيزيائياً بنسبة 100%</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("⚠️ عذراً، هذا الموديل غير مدرج في أي مجموعة توافق فيزيائي بمحلك حالياً.")
