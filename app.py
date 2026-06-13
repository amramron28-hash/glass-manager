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
# 🎨 الخلفية برابط مباشر ومكونات الواجهة المنبثقة
# =========================
IMAGE_URL = "https://githubusercontent.com"

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"], .stApp {{
    background-image: linear-gradient(rgba(10,14,23,0.45), rgba(10,14,23,0.45)), url('{IMAGE_URL}');
    background-size: cover;
    background-attachment: fixed;
}}

/* إجبار متصفح الهاتف على تفعيل التركيز والكتابة داخل حقول HTML */
input, select, textarea {{
    -webkit-user-select: text !important;
    user-select: text !important;
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

/* تنسيق مخصص لنافذة الإعدادات المنبثقة وجرس الإشعارات والترس والمراقب الصامت */
.app-header-popup {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(26, 31, 44, 0.9);
    padding: 10px 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    color: white;
}}
.popup-icons {{
    display: flex;
    gap: 15px;
    font-size: 20px;
    cursor: pointer;
}}
</style>
""", unsafe_allow_html=True)

# =========================
# 📦 البيانات والفهرس
# =========================
db_data = load_db()

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
# 🛠️ عرض نافذة الإعدادات المنبثقة (المراقب الصامت، الترس، الجرس)
# =========================
st.markdown("""
<div class="app-header-popup">
    <div style="font-weight: bold; font-size: 18px;">🛠️ المراقب الصامت</div>
    <div class="popup-icons">
        <span>🔔</span>
        <span>⚙️</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 🔍 البحث الذكي المنبثق التلقائي (Autocomplete) المصحح للهاتف
# =========================
js_models = json.dumps(sorted_models, ensure_ascii=False)
params = dict(st.query_params)
search = params.get("js_search_res", "")
workflow = params.get("js_show_wf", "") == "true"

# استخدام حقل ذكي مع خاصية تفعيل لوحة المفاتيح فوراً على الهاتف والدعم التلقائي للقائمة المنبثقة
st.markdown(f"""
<div style="position: relative;">
    <input id="s" type="text" autocomplete="off" placeholder="🔍 ابحث هنا عن موديل الهاتف..." 
    style="width:100%; padding:14px; font-size:18px; border-radius:8px; border:1px solid #ccc; background: white; color: black;" value="{search}">
    <div id="autocomplete-list" style="position: absolute; border: 1px solid #d4d4d4; border-bottom: none; border-top: none; z-index: 99; top: 100%; left: 0; right: 0; background: white; color: black; border-radius: 0 0 8px 8px; max-height: 200px; overflow-y: auto;"></div>
</div>

<script>
const models = {js_models};
const input = document.getElementById("s");
const list = document.getElementById("autocomplete-list");

// إجبار متصفح الهاتف على التركيز وقبول كيبورد اللمس
input.addEventListener('click', function() {{
    this.focus();
}});

input.oninput = () => {{
    let q = input.value.toLowerCase();
    list.innerHTML = "";
    if (!q) return false;
    
    let filtered = models.filter(x => x.toLowerCase().includes(q)).slice(0, 5);
    
    filtered.forEach(item => {{
        let b = document.createElement("DIV");
        b.style.padding = "10px";
        b.style.cursor = "pointer";
        b.style.borderBottom = "1px solid #d4d4d4";
        b.innerHTML = item;
        
        b.addEventListener("click", function() {{
            input.value = item;
            list.innerHTML = "";
            // تحديث الرابط برقم الموديل لتفعيل نتائج الـ Streamlit فوراً
            const url = new URL(window.location.href);
            url.searchParams.set('js_search_res', item);
            window.location.href = url.href;
        }});
        list.appendChild(b);
    }});
}};

// إغلاق القائمة عند الضغط في أي مكان آخر
document.addEventListener("click", function (e) {{
    if (e.target !== input) {{
        list.innerHTML = "";
    }}
}});
</script>
""", unsafe_allow_html=True)
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
