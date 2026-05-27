import streamlit as st
import json
import os

# تحديد مسار ملف قاعدة البيانات بشكل ديناميكي ليقفل السيرفر العالمي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "models_db.json")

# دالة تحميل البيانات المؤمنة
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# محرك البحث الذكي والمترجم التلقائي للاختصارات (RM, RNI, OP)
def search_models(query_clean, db_data):
    if not query_clean:
        return []
    
    query_clean = query_clean.lower().strip().replace(" ", "")
    
    # مترجم فوري لاختصارات الشركات لضمان ظهور النتائج دائماً
    replacements = {"rm": "realme", "rni": "redmi", "op": "oppo", "hw": "huawei", "sam": "samsung", "xmi": "xiaomi"}
    for short, full in replacements.items():
        if query_clean.startswith(short) and not query_clean.startswith(full):
            query_clean = query_clean.replace(short, full, 1)
            
    target_group = None
    
    # التصفية والمطابقة لتحديد المجموعة البرمجية المتوافقة
    for model in db_data:
        if isinstance(model, dict):
            m_name = model.get("model_name", "").lower().replace(" ", "")
            if query_clean in m_name or m_name in query_clean:
                target_group = model.get("matrix_group")
                if target_group:
                    break
                    
    if target_group:
        return [model for model in db_data if isinstance(model, dict) and model.get("matrix_group") == target_group]
        
    return [
        model for model in db_data 
        if isinstance(model, dict) and query_clean in model.get("model_name", "").lower().replace(" ", "")
    ]

# إعدادات الواجهة الرسومية كاملة (UI)
st.set_page_config(page_title="AMMAR TELECOM PRO", page_icon="📱", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #ffffff; }
    .stTextInput>div>div>input { background-color: #1e293b; color: white; border-radius: 8px; border: 1px solid #38bdf8; }
    .card { background-color: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #38bdf8; }
    .model-title { color: #38bdf8; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .info-line { font-size: 15px; margin: 5px 0; color: #cbd5e1; }
    .badge { background-color: #2563eb; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 AMMAR TELECOM PRO")
st.subheader("محرك البحث الذكي للموديلات المتوافقة في الفيزيائي والبدائل")

db_data = load_data()

# خانة البحث اللحظي: بمجرد كتابة أي حرف يتم تحديث النتائج فوراً تلقائياً كـ Google
query = st.text_input("اكتب اسم الهاتف أو اختصاره (مثال: RM 12, Reno 12, OP A38):", "")

if query:
    results = search_models(query, db_data)
    if results:
        st.success(f"🔍 تم العثور على ({len(results)}) موديل متوافق تماماً في المقاس والبدائل:")
        for idx, model in enumerate(results):
            with st.container():
                st.markdown(f"""
                    <div class="card">
                        <div class="model-title">📱 {model.get('model_name', 'غير معروف')}</div>
                        <div class="info-line">🔗 <b>Matrix Group:</b> <span class="badge">{model.get('matrix_group', 'N/A')}</span></div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.error("❌ هذا الموديل غير موجود حالياً في قاعدة البيانات أو لم نجد له بدائل متوافقة.")
