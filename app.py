import streamlit as st, os, base64, json
from database import load_db, save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    check_existing_size_group,
    run_intelligent_inspector
)

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# =========================
# 🎨 الخلفية
# =========================
bg_image_base64 = ""

if os.path.exists("phone_image.webp"):
    with open("phone_image.webp", "rb") as f:
        bg_image_base64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"], .stApp {{
    background-image:
    linear-gradient(rgba(10,14,23,0.45), rgba(10,14,23,0.45)),
    url('data:image/webp;base64,{bg_image_base64}');
    background-size: cover;
    background-attachment: fixed;
}}

.ammar-card {{
    padding: 12px;
    border-radius: 10px;
    margin: 6px 0;
    color: white;
    font-weight: bold;
}}

.exact {{ background: #1e8e3e; }}
.plus {{ background: #1a73e8; }}
.minus {{ background: #a56a00; }}
.warn {{ background: #b3261e; }}
</style>
""", unsafe_allow_html=True)

# =========================
# 📦 البيانات
# =========================
db_data = load_db()

# =========================
# ⚡ فهرس سريع
# =========================
@st.cache_data
def build_flat(db_data):
    all_models = []
    total = 0
    brands = {}
    empty = 0

    for size, panels in db_data.items():
        has = False

        for panel, sensors in panels.items():
            for sensor, data in sensors.items():
                models = data.get("models", [])

                if models:
                    has = True
                    total += len(models)

                    for m in models:
                        all_models.append(m)

                        b = m.split()[0]
                        brands[b] = brands.get(b, 0) + 1

        if not has:
            empty += 1

    return sorted(set(all_models)), total, brands, empty

sorted_models, total_models, brand_counts, empty_groups = build_flat(db_data)

# =========================
# 🔍 البحث المصحح والمحدث للهاتف
# =========================
params = dict(st.query_params)
search_default = params.get("js_search_res", "")

# حقل إدخال نصوص أصلي يتفاعل مع شاشات اللمس وكيبورد الهاتف فوراً
search = st.text_input(
    "🔍 اكتب اسم الموديل للبحث:", 
    value=search_default
)

# تحديث معلمات الرابط عند الكتابة لتفعيل التصفية
if search:
    st.query_params["js_search_res"] = search

workflow = params.get("js_show_wf", "") == "true"
# =========================
# 🧠 عرض النتائج (A)
# =========================
if search and not workflow:

    size, panel, sensor, name = find_model_coords(
        db_data,
        search
    )

    if size:

        st.markdown(f"## 📱 {name}")

        res = get_compatibles_strict(
            db_data,
            search
        )

        st.write(
            f"📐 {res['current_model']['size']}"
        )

        # 🟢 Exact
        for m in res["exact"]:
            st.markdown(
                f"<div class='ammar-card exact'>🟢 {m}</div>",
                unsafe_allow_html=True
            )

        # 🔵 Plus
        for m in res["plus"]:
            st.markdown(
                f"<div class='ammar-card plus'>🔵 {m}</div>",
                unsafe_allow_html=True
            )

        # 🟤 Minus
        for m in res["minus"]:
            st.markdown(
                f"<div class='ammar-card minus'>🟤 {m}</div>",
                unsafe_allow_html=True
            )

        # 🔴 Warn
        for m in res["warn"]:
            st.markdown(
                f"<div class='ammar-card warn'>⚠️ {m}</div>",
                unsafe_allow_html=True
            )

