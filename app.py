import streamlit as st
from database import load_db
from logic_engine import find_model_coords, get_compatibles_strict

st.set_page_config(layout="wide", page_title="ZEGAAR AMMAR GLASS MANAGER", page_icon="🔍")

# =========================
# 🎨 التنسيق (CSS)
# =========================
st.markdown("""
<style>
.ammar-card { padding: 12px; border-radius: 10px; margin: 6px 0; color: white; font-weight: bold; }
.exact { background: #1e8e3e; }
.plus { background: #1a73e8; }
.minus { background: #a56a00; }
.warn { background: #b3261e; }
</style>
""", unsafe_allow_html=True)

db_data = load_db()

@st.cache_data
def build_flat(data):
    all_models = []
    for size, panels in data.items():
        for panel, sensors in panels.items():
            for sensor, data_val in sensors.items():
                models = data_val.get("models", [])
                all_models.extend([m for m in models if m and m.strip()])
    return sorted(set(all_models))

sorted_models = build_flat(db_data)

# =========================
# 🛠️ الواجهة الرئيسية
# =========================
col_title, col_bell, col_gear = st.columns([6, 1, 1])
with col_title: st.subheader("🛠️ المراقب الصامت")
with col_bell: 
    if st.button("🔔"): st.toast("لا توجد إشعارات جديدة")
with col_gear: 
    if st.button("⚙️"): st.info("النظام يعمل بالوضع المستقر")

st.markdown("---")

params = st.query_params
search_query = params.get("js_search_res", "")

search = st.selectbox(
    "🔍 ابحث هنا عن موديل الهاتف:",
    options=[""] + sorted_models,
    index=sorted_models.index(search_query) + 1 if search_query in sorted_models else 0
)

if search:
    st.query_params["js_search_res"] = search
else:
    if "js_search_res" in st.query_params:
        del st.query_params["js_search_res"]
# =========================
# 🧠 عرض النتائج (الجزء التكميلي)
# =========================
if search:
    coords = find_model_coords(db_data, search)
    
    # التأكد من صحة البيانات المسترجعة
    if coords and coords[0]:
        size, panel, sensor, name = coords
        st.markdown(f"## 📱 {name}")
        
        res = get_compatibles_strict(db_data, search)
        
        if res and 'current_model' in res:
            st.write(f"📐 **المقاس:** {res['current_model'].get('size', 'غير محدد')}")
            
            # خريطة الفئات للعرض
            categories = [
                ("exact", "🟢 مطابق تماماً"), 
                ("plus", "🔵 أكبر/أطول"), 
                ("minus", "🟤 أصغر/أقصر"), 
                ("warn", "⚠️ تحذير/توافق جزئي")
            ]
            
            for key, label in categories:
                items = res.get(key, [])
                if items:
                    st.write(f"### {label}")
                    for m in items:
                        st.markdown(f"<div class='ammar-card {key}'>{m}</div>", unsafe_allow_html=True)
        else:
            st.warning("لم يتم العثور على توافقات لهذا الموديل.")
    else:
        st.error("عذراً، لم يتم العثور على بيانات لهذا الموديل في قاعدة البيانات.")
