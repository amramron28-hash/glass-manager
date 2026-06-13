import streamlit as st
from database import load_db
from logic_engine import (
    normalize_text, find_model_coords, get_compatibles_strict,
    check_existing_size_group, run_intelligent_inspector
)

st.set_page_config(layout="wide", page_title="ZEGAAR AMMAR GLASS MANAGER", page_icon="🔍")

# 🎨 التنسيق (CSS)
st.markdown("""
<style>
[data-testid="stAppViewContainer"], .stApp { background-color: #0a0e17; }
.ammar-card { padding: 12px; border-radius: 10px; margin: 6px 0; color: white; font-weight: bold; }
.exact { background: #1e8e3e; }
.plus { background: #1a73e8; }
.minus { background: #a56a00; }
.warn { background: #b3261e; }
</style>
""", unsafe_allow_html=True)

db_data = load_db()

@st.cache_data
def build_flat(db_data):
    all_models = []
    for size, panels in db_data.items():
        for panel, sensors in panels.items():
            for sensor, data in sensors.items():
                models = data.get("models", [])
                all_models.extend([m for m in models if m and m.strip()])
    return sorted(set(all_models))

sorted_models = build_flat(db_data)

# 🛠️ الواجهة العلوية
col_title, col_bell, col_gear = st.columns([6, 1, 1])
with col_title: st.subheader("🛠️ المراقب الصامت")
with col_bell:
    if st.button("🔔"): st.toast("لا توجد إشعارات جديدة حالياً 📩")
with col_gear:
    if st.button("⚙️"): st.info("إعدادات النظام: التطبيق مهيأ للعمل بالوضع الافتراضي المستقر.")
st.markdown("---")

# 🔍 حقل البحث التفاعلي (Google Style)
params = st.query_params
search_query = params.get("js_search_res", "")

# استخدام multiselect لتحقيق تجربة Auto-complete
selected = st.multiselect(
    "🔍 ابحث هنا عن موديل الهاتف:",
    options=sorted_models,
    default=[search_query] if search_query in sorted_models else [],
    placeholder="ابدأ بالكتابة للبحث...",
    max_selections=1
)

search = selected[0] if selected else None

# تحديث الرابط فوراً
if search:
    st.query_params["js_search_res"] = search
else:
    if "js_search_res" in st.query_params:
        del st.query_params["js_search_res"]

workflow = params.get("js_show_wf", "") == "true"
# 🧠 عرض النتائج التفاعلية الحية
if search and not workflow:
    coords = find_model_coords(db_data, search)
    
    if coords and coords[0]:
        size, panel, sensor, name = coords
        st.markdown(f"## 📱 {name}")
        
        res = get_compatibles_strict(db_data, search)
        
        if res and 'current_model' in res:
            st.write(f"📐 {res['current_model'].get('size', '')}")
            
            # عرض الكروت المصنفة
            mapping = [("exact", "🟢 مطابق"), ("plus", "🔵 زائد"), 
                       ("minus", "🟤 ناقص"), ("warn", "⚠️ تحذير")]
            
            for key, label in mapping:
                for m in res.get(key, []):
                    st.markdown(f"<div class='ammar-card {key}'>{m}</div>", unsafe_allow_html=True)
        else:
            st.warning("لم يتم العثور على توافقات.")
    else:
        st.error("الموديل غير موجود في قاعدة البيانات.")

# تنفيذ الـ Workflow إذا كان مفعلاً
elif search and workflow:
    st.info("تشغيل وضع الفحص الذكي...")
    results = run_intelligent_inspector(db_data, search)
    st.write(results)

