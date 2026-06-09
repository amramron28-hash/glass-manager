import streamlit as st
import os
import re
import json
import base64
from PIL import Image
import database as db
import subprocess
from streamlit_searchbox import st_searchbox

# --- الإعدادات العامة للمنصة والتأكد من مظهر التطبيق الصاروخي ---
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

# حقن كود الـ PWA لتشغيل التطبيق كبرنامج مستقل على الهاتف
st.markdown("""
<link rel="manifest" href="./manifest.json">
<script>
if('serviceWorker' in navigator){
    navigator.serviceWorker.register('./service-worker.js');
}
</script>
""", unsafe_allow_html=True)

# 🚀 تشفير وحفظ الصور الأربعة بالرام لمنع الوميض والبطء نهائياً وضمان سرعة التصفح
@st.cache_data(ttl=3600)
def get_cached_images():
    def get_image_base64(file_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, file_name)
        if os.path.exists(path):
            with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
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

# حقن مظهر صلب ومقاوم للشفافية والتداخل في الشاشات الضعيفة مع الخلفية الفخمة
css = f"""<style>
.stApp, [data-testid="stAppViewMain"], [data-testid="stAppViewContainer"], .stMain {{ 
    background-image: url("data:image/png;base64,{bg_b64}") !important; 
    background-repeat: no-repeat !important;
    background-size: cover !important;
    background-position: center center !important;
    background-attachment: fixed !important;
}}

/* منع الشفافية المفرطة في القائمة الجانبية وتنسيقها بشكل مريح جداً للعين */
[data-testid="stSidebar"] {{
    background-color: #111524 !important;
    background-image: none !important;
    border-right: 1px solid #23293f !important;
}}

.section-title {{ font-size: 20px !important; font-weight: bold !important; color: white !important; margin-top: 25px !important; text-align: right !important; direction: rtl !important; }}
.spec-badge {{ background-color: #1b2035 !important; padding: 8px 14px !important; border-radius: 8px !important; margin: 5px !important; display: inline-block !important; border: 1px solid #4e8bf5 !important; color: white !important; }}
.app-main-title {{ font-size: 38px !important; font-weight: 900 !important; color: #ffffff !important; text-align: center !important; margin-top: 15px !important; margin-bottom: 30px !important; }}
.box-empty {{ border: 1px dashed #3a3f50 !important; padding: 15px !important; margin-bottom: 14px !important; border-radius: 12px !important; text-align: center !important; color: #8a90a6 !important; background-color: #12151e !important; font-size: 14px !important; }}

/* بطاقات عمار الملونة والمصممة بالزليج الأصلي الثابت في الرام */
.ammar-card-exact, .ammar-card-plus, .ammar-card-minus {{ padding: 24px 20px !important; margin: 12px 0 !important; border-radius: 12px !important; display: flex !important; justify-content: center !important; align-items: center !important; min-height: 95px !important; background-color: #000000 !important; background-size: 160px 160px !important; background-repeat: repeat !important; }}
.ammar-card-exact {{ border: 3.5px solid #2ecc71 !important; background-image: url("data:image/png;base64,{green_b64}") !important; }}
.ammar-card-plus {{ border: 3.5px solid #007bff !important; background-image: url("data:image/png;base64,{blue_b64}") !important; }}
.ammar-card-minus {{ border: 3.5px solid #ff8c00 !important; background-image: url("data:image/png;base64,{orange_b64}") !important; }}
.ammar-text {{ color: #ffffff !important; font-size: 26px !important; font-weight: 850 !important; text-align: center !important; text-shadow: 2px 2px 6px #000000 !important; }}
.note-text {{ color: #a4b3e6 !important; font-size: 14px !important; text-align: right !important; direction: rtl !important; margin-bottom: 5px !important; }}
</style>"""
st.markdown(css, unsafe_allow_html=True)

# 🌟 [تم التصحيح]: قراءة شجرة البيانات الصافية من الرام والسحاب المتناسق
db_data = db.get_db_data()

@st.cache_data
def get_cached_models_list(_db_data): 
    return db.get_all_models(_db_data)

all_models_list = get_cached_models_list(db_data)

def search_callback(search_term):
    if not search_term: return []
    return db.google_prefix_search(search_term, all_models_list)

def parse_numeric_size(size_value):
    try:
        match = re.search(r'\d+\.?\d*', "".join(str(size_value).split()))
        return float(match.group()) if match else None
    except: return None
# --- مركز التحكم الجانبي الفخم وشريط الإشعارات الحي للمراقب الصامت ---
st.sidebar.markdown("### 📱 مركز تحكم عمار")

if st.sidebar.button("⚙️ تشغيل فحص السحاب والمراقب", key="run_watcher_btn"):
    with st.sidebar.spinner("جاري التحديث الصامت..."):
        try:
            # تشغيل المراقب الصامت للتأكد من سلامة النظام وتحديث الملفات
            subprocess.run(["python", "glass_watcher.py"], capture_output=True, text=True)
            st.cache_data.clear()
            st.sidebar.success("🟩 اكتمل الفحص وتحديث الكاش!")
            st.rerun()
        except: 
            st.sidebar.error("خطأ في الاتصال البرمجي.")

if LOGO_IMAGE: 
    st.sidebar.image(LOGO_IMAGE, width=150)

# 🌟 [تمت الإضافة]: شريط الإشعارات الحي الذي يجعلك ترى عمل المراقب الصامت كعينك داخل التطبيق
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔔 إشعارات المراقب الصامت")
notifications = db.get_notifications()
if notifications:
    for note in notifications:
        st.sidebar.markdown(f'<div class="note-text">{note}</div>', unsafe_allow_html=True)
    if st.sidebar.button("🗑️ مسح الإشعارات", key="clear_notes_btn"):
        db.clear_notifications()
        st.rerun()
else:
    st.sidebar.info("💤 المراقب هادئ، وكل الموديلات مستقرة.")

st.markdown('<div class="app-main-title">ZEGAAR AMMAR<br>GLASS MANAGER</div>', unsafe_allow_html=True)

# صندوق البحث والتنبؤ الفوري اللحظي المطوّر من الحرف الأول بطريقة جوجل الصاروخية
selected_model = st_searchbox(
    search_callback, 
    key="online_model_search", 
    placeholder="🔍 ابحث عن موديل الهاتف هنا...", 
    debounce=30
)

# --- منطق الفرز وعرض البدائل الحية الفوري (±0.03 ثانية) ---
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
            else: 
                diff = 0
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

        # دالة مساعدة لطباعة الموديلات داخل بطاقات عمار الملونة والمصممة بالزليج الأصلي
        def render_ammar_card(card_class, models_list):
            if models_list:
                joined_text = "  |  ".join(models_list)
                st.markdown(f'<div class="{card_class}"><div class="ammar-text">{joined_text}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="box-empty">لا توجد بدائل في هذا النطاق حالياً</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🟩 هواتف مطابقة تماماً وعينات الصفر (0.00):</div>', unsafe_allow_html=True)
        render_ammar_card("ammar-card-exact", exact_m)

        st.markdown('<div class="section-title">🟦 هواتف أكبر بقليل (+0.01 إلى +0.03):</div>', unsafe_allow_html=True)
        render_ammar_card("ammar-card-plus", plus_m)

        st.markdown('<div class="section-title">🟧 هواتف أصغر بقليل (-0.01 إلى -0.03):</div>', unsafe_allow_html=True)
        render_ammar_card("ammar-card-minus", minus_m)
    else:
        st.warning("⚠️ عذراً، لم نتمكن من العثور على هذا الموديل داخل شجرة المقاسات السحابية الحالية.")

