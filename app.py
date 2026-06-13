import streamlit as st, os, base64, json
from database import load_db, save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    check_existing_size_group,
    run_intelligent_inspector
)

st.set_page_config(layout="wide", page_title="ZEGAAR AMMAR GLASS MANAGER", page_icon="🔍")

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
    background-image: linear-gradient(rgba(10,14,23,0.45), rgba(10,14,23,0.45)),
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
# 🔍 البحث
# =========================
js_models = json.dumps(sorted_models, ensure_ascii=False)
params = dict(st.query_params)

search = params.get("js_search_res", "")
workflow = params.get("js_show_wf", "") == "true"

st.markdown(f"""
<div>
<input id="s" style="width:100%;padding:12px;font-size:18px" value="{search}">
</div>
<script>
const models = {js_models};
const i = document.getElementById("s");

i.oninput = () => {{
    let q = i.value.toLowerCase();
    let r = models.filter(x => x.toLowerCase().includes(q)).slice(0,5);
    console.log(r);
}}
</script>
""", unsafe_allow_html=True)

# =========================
# 🧠 عرض النتائج (A)
# =========================
if search and not workflow:
    size, panel, sensor, name = find_model_coords(db_data, search)

    if size:
        st.markdown(f"## 📱 {name}")

        res = get_compatibles_strict(db_data, search)

        st.write(f"📐 {res['current_model']['size']}")

        # 🟢 Exact
        for m in res["exact"]:
            st.markdown(f"<div class='ammar-card exact'>🟢 {m}</div>", unsafe_allow_html=True)

        # 🔵 Plus
        for m in res["plus"]:
            st.markdown(f"<div class='ammar-card plus'>🔵 {m}</div>", unsafe_allow_html=True)

        # 🟤 Minus
        for m in res["minus"]:
            st.markdown(f"<div class='ammar-card minus'>🟤 {m}</div>", unsafe_allow_html=True)

        # 🔴 Warn
        for m in res["warn"]:
            st.markdown(f"<div class='ammar-card warn'>⚠️ {m}</div>", unsafe_allow_html=True)

# =========================
# 🧠 خطة B / C
# =========================
if workflow and search:
    st.markdown("## 🧠 إدخال جديد")

    name = st.text_input("الاسم", value=search)
    size = st.text_input("المقاس")
    panel = st.selectbox("الشاشة", ["Punch-Hole Screen", "Notch Screen"])
    sensor = st.selectbox("المستشعر", ["hardware_top_sensor", "virtual_camera_sensor", "under_display_fingerprint"])

    if name and size:
        matched = check_existing_size_group(db_data, size, panel)

        if matched:
            st.info("🟡 خطة B")

            if st.button("دمج"):
                db_data.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})["models"].append(name)
                save_db(db_data)
                st.query_params.clear()
                st.rerun()

        else:
            st.warning("🔴 خطة C")

            if st.button("إنشاء"):
                db_data.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})["models"].append(name)
                save_db(db_data)
                st.query_params.clear()
                st.rerun()

# =========================
# 🛠️ المراقب الصامت + الإشعارات
# =========================
with st.sidebar:
    st.markdown("## 🛠️ المراقب الصامت")

    st.metric("📱 الهواتف", total_models)
    st.metric("📦 مجموعات فارغة", empty_groups)

    st.markdown("### 📊 البراندات")
    for b, c in list(brand_counts.items())[:5]:
        st.write(f"{b}: {c}")

    if empty_groups > 0:
        st.error(f"⚠️ {empty_groups} مجموعات فارغة")
    else:
        st.success("النظام نظيف")

    if st.button("🧹 تنظيف"):
        cleaned, changed = run_intelligent_inspector(db_data)
        save_db(cleaned)
        st.rerun()