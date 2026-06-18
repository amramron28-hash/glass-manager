import streamlit as st
import os
import base64
from database import load_db, save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# حقن ملف الـ Manifest لتفعيل خاصية التثبيت الفوري PWA
st.markdown("""
<head>
    <link rel="manifest" href="./manifest.json">
</head>
""", unsafe_allow_html=True)

# معالجة وحقن الخلفية بنسبة تعتيم مخففة (0.45) לתكون مشرقة وواضحة جداً
bg_image_base64 = ""
if os.path.exists("phone_image.webp"):
    with open("phone_image.webp", "rb") as f:
        bg_image_base64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"], [data-testid="stAppViewMain"], .stApp, .stMain, main, [data-testid="stApp"] {{
    background-image: linear-gradient(rgba(10, 14, 23, 0.45), rgba(10, 14, 23, 0.45)), url('data:image/webp;base64,{bg_image_base64}') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    background-color: transparent !important;
}}
</style>
""", unsafe_allow_html=True)

if os.path.exists("style.css"):
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

db_data = load_db()

# دالة محلية لفحص شجرة البيانات حياً والتأكد من المجموعات مسبقاً من منطق كودك الأصلي
def local_check_existing_size_group(db, target_size, target_panel):
    matched_models = []
    if target_size in db:
        if target_panel in db[target_size]:
            for sensor, s_data in db[target_size][target_panel].items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                for m in models_list:
                    matched_models.append(m)
    return matched_models

# بناء الفهرس المسطح للهواتف المتوفرة بالسيستم من كودك القديم حرفياً
all_flat_models = []
total_models, brand_counts, empty_groups_count = 0, {}, 0

for size, panels in db_data.items():
    size_has_models = False
    for panel, sensors in panels.items():
        for sensor, s_data in sensors.items():
            models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
            if models_list:
                size_has_models = True
                total_models += len(models_list)
                for m in models_list:
                    all_flat_models.append(m)
                    first_word = m.split()[0] if m.split() else "Unknown"
                    brand_counts[first_word] = brand_counts.get(first_word, 0) + 1
    if not size_has_models:
        empty_groups_count += 1

unique_models = sorted(list(set(all_flat_models)))

# تحضير مستمع قيم حقل النص لمنع تعليق التحديث اللحظي عند تبديل الموديلات
if "current_phone_input" not in st.session_state:
    st.session_state["current_phone_input"] = ""

# --- لوحة التحكم الجانبية (المراقب الصامت الأصلي) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:right;color:#00bfff;'>🛠️ لوحة التحكم الجانبية</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("🔔 جرس الإشعارات اللحظي", expanded=False):
        st.info("💡 النظام الموحد المحدث نشط ومستقر سحابياً الآن 100% وبأعلى سرعة تصفح.")
    
    with st.expander("⚙️ إعدادات المراقب الصامت", expanded=True):
        st.markdown("<p style='text-align:right;'>المراقب الصامت يراقب شجرة البيانات ويحدث التقارير حياً.</p>", unsafe_allow_html=True)
        st.metric(label="📈 إجمالي الهواتف المراقبة بالسيستم", value=total_models)
        st.markdown("---")
        st.markdown("<h4 style='text-align:right;color:#00bfff;'>📊 حصة البراندات بالـ RAM:</h4>", unsafe_allow_html=True)
        if brand_counts:
            for b_name, b_count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:4]:
                percentage = round((b_count / total_models) * 100, 1) if total_models > 0 else 0
                st.markdown(f"<p style='text-align:right;margin-bottom:2px;'>📋 <b>{b_name}</b>: {b_count} هاتف ({percentage}%)</p>", unsafe_allow_html=True)
                st.progress(percentage / 100)
        st.markdown("---")
        if empty_groups_count > 0:
            st.warning(f"⚠️ رصد المراقب الصامت عدد ({empty_groups_count}) مجموعة مقاس فارغة.")
        else:
            st.success("🎯 فحص سليم: لا توجد مجموعات ميتة بشجرة الـ JSON.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧹 تشغيل الصيانة الفورية وتطهير الشجرة", key="sidebar_inspector_btn"):
            cleaned_db, changes_made = run_intelligent_inspector(db_data)
            final_cleaned = {k: v for k, v in cleaned_db.items() if v}
            if len(final_cleaned) != len(db_data) or changes_made:
                save_db(final_cleaned)
                st.success("✨ تم تطهير شجرة البيانات وإعادة ترتيب الموديلات سحابياً!")
                st.rerun()
            else:
                st.toast("🎯 السيستم نظيف ومطهر بالكامل كلياً.")

st.markdown("<br>", unsafe_allow_html=True)
# --- واجهة واجهة التطبيق الرئيسية الشاخصة الأصيلة ---
st.markdown("<div class='app-main-title'>ZEGAAR AMMAR GLASS MANAGER</div>", unsafe_allow_html=True)
st.markdown("<div class='app-sub-title'>النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>", unsafe_allow_html=True)

# حقل البحث النصي الحر والمرن تماماً (منع الإجبار والفرض)
phone = st.text_input(
    "البحث والمطابقة الفورية للموديلات:",
    value=st.session_state["current_phone_input"],
    placeholder="اكتب اسم الهاتف المستهدف هنا بحرية...",
    label_visibility="collapsed",
    key="free_smart_search_input"
).strip()

# الستارة المنسدلة الحية التفاعلية: تظهر بمجرد كتابة حرف واحد فقط بناءً على فحص الأجزاء المقارنة لحروف النص المدخل
if phone and len(phone) >= 1:
    search_words = phone.lower().split()
    suggestions = [m for m in unique_models if any(any(word in p_word for p_word in m.lower().split()) for word in search_words)]
    
    if suggestions:
        st.caption("🔍 هواتف مسجلة بالنظام قد تقصدها (اضغط للمساعدة والملء الفوري):")
        for s in suggestions[:3]:
            if st.button(f"📋 {s}", key=f"sug_{s}"):
                st.session_state["current_phone_input"] = s
                st.rerun()

# التحقق من المطابقة الصارمة بالاسم داخل المكتبة لمنع خلط الماركات
size_str, panel, sensor, real_name = None, None, None, None
if phone:
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone)

is_exact_match = True if real_name and phone.lower() == real_name.lower() else False

# ============================================================
# الخطة 1: عرض نتائج التوافق عند العثور الحرفي الصارم على اسم الهاتف
# ============================================================
if phone and size_str and is_exact_match:
    st.markdown(f"<div class='section-title'>📊 نتائج التوافق والمقاسات للهاتف: {real_name}</div>", unsafe_allow_html=True)
    results = get_compatibles_strict(db_data, phone)
    st.markdown(f"<div style='text-align:right;direction:rtl;margin-bottom:20px;'><span class='spec-badge'>📐 المقاس السحابي: {size_str}</span><span class='spec-badge'>🖥️ نوع الهيكل: {panel}</span><span class='spec-badge'>👁️ نوع المستشعر: {sensor}</span></div>", unsafe_allow_html=True)
    
    for cat, title, css in [
        ('exact', '🟢 هواتف مطابقة تماماً في الأبعاد والقص (Exact 0.00)', 'flat-exact'),
        ('plus', '🔵 هواتف أكبر بقليل متوافقة (Plus +0.01 إلى +0.03)', 'flat-plus'),
        ('minus', '🟤 هواتف أصغر بقليل متوافقة (Minus -0.01 إلى -0.03)', 'flat-minus')
    ]:
        if cat in results:
            models_list = [m for m in results[cat] if m not in results.get('warn', [])]
            if models_list:
                st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
                for model in models_list:
                    st.markdown(f"<div class='ammar-flat-card {css}'><span class='flat-phone-text'>{model}</span></div>", unsafe_allow_html=True)
        
    if results.get('warn'):
        st.markdown("<div class='section-title'>⚠️ تنبيه حساس: هواتف بنفس المقاس ولكن بمستشعر مختلف:</div>", unsafe_allow_html=True)
        for model in results['warn']:
            st.markdown(f"<div class='flat-warning-card'><span class='flat-warn-text'>{model} (انتبه: حساس مختلف تماماً)</span></div>", unsafe_allow_html=True)

    # وينتهي دور الخطة 1 تماماً قف

# ============================================================
# الخطة 2: تفتح فوراً وحراً عند كتابة هاتف جديد تماماً (مثل Infinix Note 60)
# ============================================================
elif phone and not is_exact_match:
    st.markdown("---")
    st.warning(f"⚠️ الهاتف ({phone}) غير مسجل بالاسم الحرفي هذا. تم فتح الخطة 2 لإدخال مواصفاته يدوياً بالتتابع:")
    
    col_s, col_p, col_se = st.columns(3)
    with col_s:
        new_size = st.text_input("📐 1. المقاس الرقمي للزبون (مثال: 6.67):", key="workflow_size")
    
    new_panel = ""
    new_sensor = ""

    # ظهور تتابعي شرطي سلس للقوائم بالتناسب مع ملء الحقول يدوياً
    if new_size.strip():
        with col_p:
            new_panel = st.selectbox("🖥️ 2. نوع الشاشة الهيكلي:", ["", "Punch-Hole Screen", "Notch Screen", "Waterdrop Notch", "Full Screen", "Flat Screen", "Curved Screen"], key="workflow_panel")

    if new_size.strip() and str(new_panel).strip():
        with col_se:
            new_sensor = st.selectbox("👁️ 3. مستشعر التقارب المكتشف والمراقب:", ["", "hardware_top_sensor", "virtual_camera_sensor", "under_display_fingerprint", "under_display_sensor", "side_sensor", "no_visible_sensor"], key="workflow_sensor")
        
    if new_size.strip() and str(new_panel).strip() and str(new_sensor).strip():
        new_size = new_size.strip()
        new_panel = str(new_panel).strip()
        new_sensor = str(new_sensor).strip()
        
        # استدعاء الفحص المحلي للمجموعات السحابية المتوفرة
