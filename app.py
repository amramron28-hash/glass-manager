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

# حقن ملف الـ Manifest لتفعيل خاصية PWA والتثبيت على شاشة الهاتف
st.markdown("""
<head>
    <link rel="manifest" href="./manifest.json">
</head>
""", unsafe_allow_html=True)

# معالجة وحقن الخلفية بنسبة تعتيم مخففة (0.45) لتكون واضحة ومشرقة
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

# دالة محلية بديلة ومصححة لفحص وجود المجموعات مسبقاً لمنع أي تعارض برميجي
def local_check_existing_size_group(db, target_size, target_panel):
    matched_models = []
    if target_size in db:
        if target_panel in db[target_size]:
            for sensor, s_data in db[target_size][target_panel].items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                for m in models_list:
                    matched_models.append(m)
    return matched_models

# بناء الفهرس المسطح للهواتف المتوفرة بالسيستم من شجرة البيانات الكلية
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

# --- لوحة التحكم الجانبية المطورة (المراقب الصامت النشط) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:right;color:#00bfff;'>🛠️ لوحة التحكم الجانبية</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.expander("🔔 جرس الإشعارات اللحظي", expanded=False):
        st.info("💡 النظام الموحد المحدث نشط ومستقر سحابياً الآن 100% وبأعلى سرعة تصفح.")
    
    with st.expander("⚙️ إعدادات المراقب الصامت النشط", expanded=True):
        st.markdown("<p style='text-align:right;'>المراقب الصامت يمسح المجموعات برمجياً ويصطاد الأخطاء حياً.</p>", unsafe_allow_html=True)
        st.metric(label="📈 إجمالي الهواتف المراقبة بالسيستم", value=total_models)
        st.markdown("---")
        
        # خوارزمية الفحص الدوري الذكي كاشف الأخطاء والتشوهات البنائية داخل المجموعات حياً
        suspicious_models = []
        for size, panels in db_data.items():
            try:
                size_float = float(size)
                if size_float < 4.0 or size_float > 8.0:
                    suspicious_models.append(f"⚠️ مقاس مشكوك فيه: `{size}`")
            except ValueError:
                suspicious_models.append(f"❌ خطأ في تنسيق رقم المقاس: `{size}`")
                
            for panel, sensors in panels.items():
                for sensor, s_data in sensors.items():
                    models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                    for m in models_list:
                        m_lower = m.lower()
                        if "curved" in panel.lower() and "flat" in m_lower:
                            suspicious_models.append(f"🔍 تعارض هيكلي: هاتف `{m}` مسجل كـ Curved وهو Flat")
                        if "flat" in panel.lower() and "curved" in m_lower:
                            suspicious_models.append(f"🔍 تعارض هيكلي: هاتف `{m}` مسجل كـ Flat وهو Curved")
                        if "notch" in panel.lower() and "hole" in m_lower:
                            suspicious_models.append(f"🔍 تعارض شاشات: هاتف `{m}` مسجل كـ Notch وهو Punch-Hole")

        st.markdown("<h4 style='text-align:right;color:#ef4444;'>🚨 تقرير المراقبة الدوري الحالي:</h4>", unsafe_allow_html=True)
        if suspicious_models:
            st.error(f"⚠️ رصد المراقب الصامت عدد ({len(suspicious_models)}) أخطاء في المجموعات!")
            for issue in suspicious_models[:5]:
                st.markdown(f"<p style='text-align:right;font-size:13px;'>{issue}</p>", unsafe_allow_html=True)
        else:
            st.success("🎯 فحص سليم: جميع الهواتف والمقاسات متناسقة منطقياً 100% داخل المجموعات.")
            
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
            st.success("🎯 شجرة الـ JSON خالية تماماً من المجموعات الميتة.")
            
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
st.markdown("<div class='app-main-title'>ZEGAAR AMMAR GLASS MANAGER</div>", unsafe_allow_html=True)
st.markdown("<div class='app-sub-title'>النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>", unsafe_allow_html=True)

# حقل البحث النصي الحر (الخطة 1) مع الستارة المرنة والذكية غير الإلزامية
phone = st.text_input("📱 الباب الرئيسي: اكتب اسم الهاتف المستهدف هنا للبحث الفوري:", placeholder="مثال: Infinix Note 60").strip()

# الستارة التفاعلية الحية: تظهر اقتراحات مساعدة لتوجيه المستخدم ولا تعيق إضافة هاتف جديد نهائياً
if phone:
    suggestions = [m for m in unique_models if all(w in m.lower() for w in phone.lower().split())]
    if suggestions:
        st.caption("🔍 هواتف شبيهة مسجلة بالنظام (إذا كان هاتفك اضغط عليه ليشحن فوراً):")
        for s in suggestions[:3]:
            if st.button(f"📋 {s}", key=f"sug_{s}"):
                st.session_state["phone_input_val"] = s
                st.rerun()

# التحقق والمطابقة بالاسم بشكل صارم وحرفي (لمنع الخلط والتشابه بين براندات الهواتف المختلفة)
size_str, panel, sensor, real_name = None, None, None, None
if phone:
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone)

is_exact_match = True if real_name and phone.lower() == real_name.lower() else False

# ============================================================
# تنفيذ الخطة 1: إذا كان الاسم متطابقاً تماماً وموجوداً في قاعدة البيانات
# ============================================================
if phone and size_str and is_exact_match:
    st.markdown(f"<div class='section-title'>📊 نتائج التوافق والمقاسات للهاتف: {real_name}</div>", unsafe_allow_html=True)
    results = get_compatibles_strict(db_data, phone)
    
    if 'current_model' in results:
        st.markdown(f"<div style='text-align:right;direction:rtl;margin-bottom:20px;'><span class='spec-badge'>📐 المقاس السحابي: {results['current_model'].get('size', size_str)}</span><span class='spec-badge'>🖥️ نوع الهيكل: {results['current_model'].get('panel', panel)}</span><span class='spec-badge'>👁️ نوع المستشعر: {results['current_model'].get('sensor', sensor)}</span></div>", unsafe_allow_html=True)
    else:
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
