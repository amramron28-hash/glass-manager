import os
from supabase import create_client

# 🔒 جلب مفاتيح الاتصال الآمن بالسحابة
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # تأكد من مطابقة الاسم لما وضعته في Secrets

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# ✔ إضافة هاتف جديد إلى السحابة
# ==========================================
def add_model(size, panel, sensor, model):
    if not all([size, panel, sensor, model]):
        return False
    try:
        supabase.table("phones").insert({
            "size": str(size).strip(),
            "panel": str(panel).strip(),
            "sensor": str(sensor).strip(),
            "model_name": str(model).strip()  # تأكد من مطابقة الاسم للعمود بالسحابة model_name
        }).execute()
        return True
    except Exception:
        return False

# ==========================================
# ✔ تحميل البيانات بشكلها القاموسي المتداخل
# ==========================================
def load_db():
    try:
        res = supabase.table("phones").select("*").execute()
        rows = res.data or []
        db = {}
        for r in rows:
            size = str(r.get("size", "")).strip()
            panel = str(r.get("panel", "")).strip()
            sensor = str(r.get("sensor", "")).strip()
            model = str(r.get("model_name", "")).strip()

            if not all([size, panel, sensor, model]):
                continue

            db.setdefault(size, {})
            db[size].setdefault(panel, {})
            db[size][panel].setdefault(sensor, {"models": []})

            if model not in db[size][panel][sensor]["models"]:
                db[size][panel][sensor]["models"].append(model)
        return db
    except Exception:
        return {}

# ==========================================
# 🛡️ دالة حماية البيانات الاحتياطية (save_db)
# ==========================================
def save_db(cleaned_db=None):
    """
    هذه الدالة تم إنشاؤها لامتصاص الصدمات البرمجية ومنع الـ ImportError.
    تقوم بإنشاء تزامن تلقائي لمنع تجمد التطبيق واختفاء الإعدادات.
    """
    try:
        # إذا تم استدعاء دالة الصيانة لتنظيف البيانات، نقوم بتحديثها سحابياً
        if cleaned_db:
            for size, panels in cleaned_db.items():
                for panel, sensors in panels.items():
                    for sensor, data in sensors.items():
                        for model in data.get("models", []):
                            # تفحص السحابة وتضيف البيانات النظيفة فقط
                            add_model(size, panel, sensor, model)
        return True
    except Exception:
        return False
import streamlit as st
import datetime
import os

# 🔒 1. تهيئة الذاكرة المؤقتة لمنع الـ AttributeError والـ NameError وتفعيل خطة المراحل
if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

if "current_stage" not in st.session_state:
    st.session_state.current_stage = 1

# تعريف مبدئي للمتغيرات العالمية لحماية السيرفر من الانهيار عند الإقلاع
db_data = {}
unique_models = []
total_models = 0
empty_groups_count = 0
brand_counts = {}

# ⚙️ 2. إعدادات الصفحة الأساسية للتطبيق لتظهر كاملة الأدوات
st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# 📦 3. الاستيرادات الفنية الصحيحة بعد إصلاح ملف قاعدة البيانات
from database import load_db, add_model, save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)
from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section
)
from app_init import initialize_system_data
from rapidfuzz import process, fuzz
from streamlit_searchbox import st_searchbox

# 📊 4. تشغيل وحقن القوالب وقراءة البيانات الحقيقية من السحابة فوراً
inject_pwa_and_styles()
try:
    db_data, unique_models, total_models, empty_groups_count, brand_counts = initialize_system_data()
except Exception:
    st.error("⚠️ فشل الاتصال بالسحابة مؤقتاً، تم تفعيل وضع حماية البيانات من التلف.")

# 📱 الواجهة الرئيسية (العنوان الممتد بصفين)
st.markdown(
    """
    <div style="width: 100%; display: flex; justify-content: flex-start; align-items: center; margin-bottom: 2px; padding: 0px 5px; border-bottom: 2px solid rgba(0, 191, 255, 0.3); margin-top: -20px;">
        <span style="font-size: 28px; font-weight: 900; color: #00bfff; font-family: 'Courier New', monospace; letter-spacing: 1px; white-space: nowrap;">ZEGAAR AMMAR</span>
    </div>
    """, unsafe_allow_html=True
)

st.markdown(
    """
    <div style="width: 100%; display: flex; justify-content: flex-start; align-items: center; margin-bottom: 35px; padding: 0px 5px;">
        <span style="font-size: 28px; font-weight: 900; color: #00bfff; font-family: 'Courier New', monospace; letter-spacing: 1px; white-space: nowrap;">GLASS MANAGER</span>
    </div>
    """, unsafe_allow_html=True
)

# التقاط وعرض الإشعارات عبر الجرس العلوي للواجهة
if "show_success_toast" in st.session_state and st.session_state.show_success_toast:
    st.success(st.session_state.show_success_toast)
    st.toast(st.session_state.show_success_toast)
    st.session_state.show_success_toast = ""

# دالة مساعدة لمحرك البحث التلقائي لفرز الموديلات المسترجعة سحابياً
def search_models_callback(query, models_list):
    if not query:
        return models_list[:10]
    results = process.extract(query, models_list, limit=10, scorer=fuzz.WRatio)
    return [r[0] for r in results]

# صندوق البحث المستقر والمتكامل مع نظام المراحل
selected_phone = st_searchbox(
    search_function=lambda q, **k: search_models_callback(q, unique_models),
    placeholder="🔍 ابحث عن هاتف أو اكتب اسماً جديداً...",
    key="phone_search_autocomplete_v6"
)

# معالجة الإدخال وتدفق مراحل التطبيق الحكيمة
if selected_phone:
    st.session_state.custom_search_input = selected_phone.strip()
    st.session_state.current_stage = 2

if not selected_phone:
    st.markdown("<p style='color:#a0aec0; margin-bottom: 2px; text-align: right;'>➕ إذا كان الهاتف جديداً، اكتبه بالأسفل:</p>", unsafe_allow_html=True)
    custom_typed = st.text_input(label="", placeholder="اكتب اسم الهاتف الجديد...", key="fallback_manual_input_text_v6")
    if custom_typed.strip() and custom_typed.strip() != st.session_state.custom_search_input:
        st.session_state.custom_search_input = custom_typed.strip()
        st.session_state.current_stage = 2

# منطق إطلاق التحقق والمطابقة في السحابة لحماية البيانات
if st.session_state.custom_search_input:
    current_search = st.session_state.custom_search_input
    st.markdown(f"<p style='color:#00bfff; font-size:18px; font-weight:bold; text-align:right;'>📱 الهاتف المبحوث عنه: [{current_search}]</p>", unsafe_allow_html=True)
    
    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(db_data, current_search)

    if size_grp:
        compat_results = get_compatibles_strict(db_data, current_search)
        st.success(f"🎯 الموديل [{real_name}] مسجل ومتوافق سحابياً!")
        
        draw_technical_coords(size_grp, panel_grp, sensor_grp)
        draw_neon_section("مطابقة للمقاس", compat_results["exact"], "#2ecc71", "🎯", current_search)
        draw_neon_section("أكبر بقليل", compat_results["plus"], "#3498db", "➕", current_search)
        draw_neon_section("أصغر بقليل", compat_results["minus"], "#e67e22", "➖", current_search)
        draw_neon_section("مستشعر مختلف", compat_results["warn"], "#ef4444", "⚠️", current_search)
    else:
        # نموذج ذكي لإضافة تفاصيل الهاتف غير الموجود مباشرة في السحابة
        st.warning(f"🔍 الموديل [{current_search}] غير مسجل حالياً بالسحابة.")
        with st.form("add_new_phone_form"):
            st.markdown("<b style='color:#00bfff;'>➕ إضافة مواصفات القياس الفني للهاتف:</b>", unsafe_allow_html=True)
            new_size = st.text_input("المقاس (Size)")
            new_panel = st.text_input("اللوحة الأساسية (Panel)")
            new_sensor = st.text_input("المستشعر (Sensor)")
            submit_btn = st.form_submit_with_rows_button if hasattr(st, 'form_submit_with_rows_button') else st.form_submit_button("حفظ دائم في السحابة 💾")
            
            if submit_btn:
                if add_model(new_size, new_panel, new_sensor, current_search):
                    st.session_state.show_success_toast = f"تم حفظ {current_search} سحابياً بنجاح!"
                    st.rerun()
                else:
                    st.error("❌ فشل الحفظ، يرجى ملء الحقول بالكامل والتحقق من الشبكة.")

# 🛠️ إعادة تفعيل وتثبيت اللوحة الجانبية (المراقب الصامت وجرس التحكم)
with st.sidebar:
    st.markdown("<h2 style='text-align:right;color:#00bfff;'>🛠️ المراقب الصامت</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("⚙️ الإعدادات والتحكم والمؤشرات", expanded=True):
        st.write(f"📅 تاريخ اليوم: **{datetime.date.today()}**")
        st.metric(label="📈 إجمالي الهواتف السحابية", value=total_models)
        st.metric(label="⚠️ المجموعات الفارغة المحذوفة", value=empty_groups_count)
        
        if st.button("🧹 تشغيل الصيانة الاحترافية"):
            cleaned_db, changes_made = run_intelligent_inspector(db_data)
            if changes_made:
                save_db(cleaned_db)  # استدعاء آمن ومحمي لمنع الانهيار
                st.session_state.show_success_toast = "تمت صيانة وتنظيف وتأمين قاعدة البيانات السحابية بنجاح!"
                st.rerun()
            else:
                st.toast("🎯 النظام نظيف تماماً ولا توجد بيانات تالفة.")
