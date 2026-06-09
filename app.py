import streamlit as st
import os
import re
import base64
from PIL import Image
import database as db
from streamlit_searchbox import st_searchbox

LOGO_IMAGE = None
try: 
    LOGO_IMAGE = Image.open("AMMAR.jpg")
except: 
    pass

st.set_page_config(
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon=LOGO_IMAGE if LOGO_IMAGE else "📱",
    layout="centered"
)

st.markdown("""
<link rel="manifest" href="./manifest.json">
<script>
if('serviceWorker' in navigator){
    navigator.serviceWorker.register('./service-worker.js');
}
</script>
""", unsafe_allow_html=True)

# 🚀 كاش الرام للصور لمنع الوميض والبطء والتأخير نهائياً
@st.cache_data(ttl=3600)
def get_cached_images():
    def get_image_base64(file_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, file_name)
        if os.path.exists(path):
            with open(path, "rb") as f: 
                return base64.b64encode(f.read()).decode()
        return ""
    return {
        "green": get_image_base64("zellij.png"),
        "blue": get_image_base64("zellij_blue.png"),
        "orange": get_image_base64("zellij_orange.png"),
        "bg": get_image_base64("bg.png")
    }

img_dict = get_cached_images()
green_b64, blue_b64 = img_dict["green"], img_dict["blue"]
orange_b64, bg_b64 = img_dict["orange"], img_dict["bg"]

css = f"""<style>
.stApp, [data-testid="stAppViewMain"], [data-testid="stAppViewContainer"], .stMain {{ 
    background-image: url("data:image/png;base64,{bg_b64}") !important; 
    background-repeat: no-repeat !important;
    background-size: cover !important;
    background-position: center center !important;
    background-attachment: fixed !important;
}}
[data-testid="stHeader"], [data-testid="stSidebar"], .stMainContainer {{ background-color: transparent !important; background-image: none !important; }}
.section-title {{ font-size: 20px !important; font-weight: bold !important; color: white !important; margin-top: 25px !important; text-align: right !important; direction: rtl !important; }}
.spec-badge {{ background-color: #262730 !important; padding: 6px 12px !important; border-radius: 6px !important; margin: 4px !important; display: inline-block !important; border: 1px solid #4e8bf5 !important; color: white !important; }}
.app-main-title {{ font-size: 38px !important; font-weight: 900 !important; color: #ffffff !important; text-align: center !important; margin-top: 15px !important; margin-bottom: 30px !important; }}
.box-empty {{ border: 1px dashed #3a3f50 !important; padding: 15px !important; margin-bottom: 14px !important; border-radius: 12px !important; text-align: center !important; color: #8a90a6 !important; background-color: #12151e !important; font-size: 14px !important; }}
.ammar-card-exact, .ammar-card-plus, .ammar-card-minus {{ padding: 24px 20px !important; margin: 12px 0 !important; border-radius: 12px !important; display: flex !important; justify-content: center !important; align-items: center !important; min-height: 95px !important; background-color: #000000 !important; background-size: 160px 160px !important; background-repeat: repeat !important; }}
.ammar-card-exact {{ border: 3.5px solid #2ecc71 !important; background-image: url("data:image/png;base64,{green_b64}") !important; }}
.ammar-card-plus {{ border: 3.5px solid #007bff !important; background-image: url("data:image/png;base64,{blue_b64}") !important; }}
.ammar-card-minus {{ border: 3.5px solid #ff8c00 !important; background-image: url("data:image/png;base64,{orange_b64}") !important; }}
.ammar-text {{ color: #ffffff !important; font-size: 26px !important; font-weight: 850 !important; text-align: center !important; text-shadow: 2px 2px 6px #000000 !important; }}
</style>"""
st.markdown(css, unsafe_allow_html=True)

# 🚀 كاش الرام لتخزين الموديلات ومنع اللاق أثناء ضغط الحروف
@st.cache_data
def get_cached_models_list(_db_data): 
    return db.get_all_models(_db_data)

db_data = db.get_db_data()
all_models_list = get_cached_models_list(db_data)

def search_callback(search_term):
    if not search_term: return []
    return db.google_prefix_search(search_term, all_models_list)

def parse_numeric_size(size_value):
    try:
        match = re.search(r'\d+\.?\d*', "".join(str(size_value).split()))
        return float(match.group()) if match else None
    except: return None

st.sidebar.markdown("### 📱_مركز تحكم عمار")
if st.sidebar.button("🔄_تحديث واجهة السحاب الفورية"):
    st.cache_data.clear()
    st.rerun()

if LOGO_IMAGE: 
    st.image(LOGO_IMAGE, width=170)
st.markdown('<div class="app-main-title">ZEGAAR AMMAR<br>GLASS MANAGER</div>', unsafe_allow_html=True)

selected_model = st_searchbox(
    search_callback, 
    key="online_model_search", 
    placeholder="🔍 ابحث عن موديل الهاتف هنا...", 
    debounce=30
)
if selected_model:
    t_size, t_screen, t_sensor, found_online = None, None, None, False

    for sz, screens in db_data.items():
        if sz in ["system_notifications", "metadata", "data"]: continue
        if isinstance(screens, dict):
            for scr, sensors in screens.items():
                if isinstance(sensors, dict):
                    for sns, models in sensors.items():
                        if isinstance(models, list) and selected_model in models:
                            t_size, t_screen, t_sensor, found_online = sz, scr, sns, True
                            break
                if found_online: break
            if found_online: break

    def get_compatibles(tgt_sz, tgt_scr, tgt_sns, skip_model=None):
        ex, pl, mi = [], [], []
        t_num = parse_numeric_size(tgt_sz)
        for v_sz, screens in db_data.items():
            if v_sz in ["system_notifications", "metadata", "data"]: continue
            c_num = parse_numeric_size(v_sz)
            if t_num is not None and c_num is not None:
                diff = round(c_num - t_num, 2)
                if not (-0.03 <= diff <= 0.03): continue
            else: diff = 0
            if isinstance(screens, dict) and tgt_scr in screens:
                if isinstance(screens[tgt_scr], dict) and tgt_sns in screens[tgt_scr]:
                    for m in screens[tgt_scr][tgt_sns]:
                        if skip_model and m.strip().lower() == skip_model.strip().lower(): continue
                        if diff == 0: ex.append(m)
                        elif diff > 0: pl.append(m)
                        else: mi.append(m)
        return ex, pl, mi

    if found_online:
        st.success(f"🎯 تم تحديد الهاتف: {selected_model}")
        st.markdown(
            f'<div style="text-align:center; direction:rtl; margin-bottom: 20px;">'
            f'<span class="spec-badge">📐 المقاس: {t_size}</span>'
            f'<span class="spec-badge">🖥️ الشاشة: {t_screen}</span>'
            f'<span class="spec-badge">🎯 المجموعة: {t_sensor}</span>'
            f'</div>', unsafe_allow_html=True
        )

        exact_m, plus_m, minus_m = get_compatibles(t_size, t_screen, t_sensor, selected_model)

        for title, models, cls in [
            ("🟩 هواتف مطابقة تماماًوعينات الصفر (0.00):", exact_m, "ammar-card-exact"),
            ("🟦 هواتف أكبر بقليل (+0.01 إلى +0.03):", plus_m, "ammar-card-plus"),
            ("🟧 هواتف أصغر بقليل (-0.01 إلى -0.03):", minus_m, "ammar-card-minus"),
        ]:
            st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
            if models:
                for m in models: 
                    st.markdown(f'<div class="{cls}"><div class="ammar-text">{m}</div></div>', unsafe_allow_html=True)
            else: 
                st.markdown('<div class="box-empty">لا توجد بدائل متوافقة ضمن هذه الفئة حالياً.</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ هذا الموديل ليس لديه بيانات توافق مسجلة في شجرة المقاسات.")
else:
    st.markdown('<div class="section-title">📌 ابحث عن الموديل أعلاه لتظهر لك النتائج فورا.</div>', unsafe_allow_html=True)
