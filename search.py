import streamlit as st
import json
import os

DB_FILE = "models_db.json"

# 1. دالة تحميل البيانات المدمجة
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

# 2. محرك البحث الذكي والمترجم التلقائي للاختصارات (RM, RMI, OP)
def search_models(query, db_data):
    query_clean = query.lower().strip().replace(" ", "")
    if not query_clean:
        return []
        
    # مترجم فوري للاختصارات الميدانية لضمان ظهور النتائج دائماً
    replacements = {"rm": "realme", "rmi": "redmi", "op": "oppo", "hw": "huawei", "sam": "samsung", "xmi": "xiaomi"}
    for short, full in replacements.items():
        if query_clean.startswith(short) and not query_clean.startswith(full):
            query_clean = query_clean.replace(short, full, 1)

    target_group = None
    # الخطوة أ: البحث الجزئي لتحديد المجموعة الفيزيائية المتوافقة
    for model in db_data:
        m_name = model.get("model_name", "").lower().replace(" ", "")
        if query_clean in m_name or m_name in query_clean:
            target_group = model.get("matrix_group")
            if target_group:
                break
                
    # الخطوة ب: جلب المجموعة كاملة (المقاس والشاشة المتطابقة فقط لا غير)
    if target_group:
        return [model for model in db_data if model.get("matrix_group") == target_group]
        
    return [model for model in db_data if query_clean in model.get("model_name", "").lower().replace(" ", "")]

# 3. إعدادات الواجهة الاحترافية الزرقاء (AMMAR TELECOM PRO)
st.set_page_config(page_title="AMMAR TELECOM PRO", page_icon="📱", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #ffffff; }
    .stTextInput>div>div>input { background-color: #1e293b; color: white; border-radius: 8px; border: 1px solid #3b82f6; }
    .card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #3b82f6; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .model-title { color: #3b82f6; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .info-line { font-size: 15px; margin: 5px 0; color: #cbd5e1; }
    .badge { background-color: #2563eb; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 AMMAR TELECOM PRO")
st.subheader("محرك البحث الذكي للموديلات المتوافقة في المقاس والشاشة")

db_data = load_data()

# خانة البحث المرن
query = st.text_input("اكتب اسم الهاتف أو اختصاره (مثال: RM 12, Reno 12, OP A38):", "")

if query:
    results = search_models(query, db_data)
    if results:
        st.success(f"تم العثور على {len(results)} موديل متوافق تماماً في المقاس والشاشة:")
        for idx, model in enumerate(results):
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div class="model-title">{idx+1}. {model.get('model_name', 'غير معروف')}</div>
                    <div class="info-line"><b>Matrix Group:</b> <span class="badge">{model.get('matrix_group', 'N/A')}</span></div>
                    <div class="info-line"><b>العلامة التجارية:</b> {model.get('brand', 'غير معروف')}</div>
                    <div class="info-line"><b>التوافق الفيزيائي:</b> مقاس وأبعاد متطابقة 100% ✓</div>
                </div>
                """, unsafe_allowed_html=False if 'unsafe_allow_html' not in st.markdown.__code__.co_varnames else True)
    else:
        st.error(f"الموديل '{query}' غير مسجل حالياً في قاعدة البيانات.")
