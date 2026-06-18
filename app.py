import streamlit as st
import os
import requests
from database import load_db, save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)
from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section,
    draw_control_panel
)

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# تفعيل الخلفية الأصلية وتأثير الزجاج وتنسيقات الألوان من ملف الـ UI الخاص بك فوراً
inject_pwa_and_styles()

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

# دالة رادار التدقيق العالمي الخلفي (تستعلم صامتاً عبر الـ API للمواصفات الحقيقية)
def ai_background_global_verify(phone_name):
    try:
        url = f"https://vercel.app{requests.utils.quote(phone_name)}"
        res = requests.get(url, timeout=1.5).json()
        if res and "specs" in res:
            return {
                "size": str(res["specs"].get("display_size", "")),
                "panel": str(res["specs"].get("display_type", "")),
                "sensor": str(res["specs"].get("proximity_type", ""))
            }
    except:
        pass
    return None

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
                    words = m.split()
                    first_word = words[0] if words else "Unknown"
                    brand_counts[first_word] = brand_counts.get(first_word, 0) + 1
    if not size_has_models:
        empty_groups_count += 1

unique_models = sorted(list(set(all_flat_models)))

# الشعار ذو السطرين وعرض الشاشة الكامل بتوهج نيون أزرق فخم
st.markdown(
"""
<div style="
width: 100%;
font-size:28px;
font-weight:900;
color:#00bfff;
text-align: center;
text-shadow:0 0 12px rgba(0,191,255,.7);
margin-bottom: 15px;
">
ZEGAAR AMMAR<br>GLASS MANAGER
</div>
""",
unsafe_allow_html=True
)

st.markdown("<div class='app-sub-title' style='text-align:center; color:white; margin-bottom:20px;'>النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>", unsafe_allow_html=True)

# المزامنة العميقة وحفظ مدخلات البحث البرمجية اللحظية لمنع تكرار النوافذ المستقلة
if "phone_search_key" not in st.session_state:
    st.session_state["phone_search_key"] = ""

# شريط البحث الموحد: صندوق خيارات ذكي يدعم البحث اللحظي بالكتابة بمجرد كتابة حرف واحد
dropdown_options = ["-- ابحث واشحن الموديل المستهدف من هنا --"] + unique_models

selected_target = st.selectbox(
    "البحث والمطابقة الفورية للموديلات:",
    options=dropdown_options,
    label_visibility="collapsed",
    key="unified_smart_search_box"
)

# التقاط اسم الهاتف المكتوب أو المختار برمجياً بحرية كاملة ودون إجبار
final_search_term = ""
if selected_target != "-- ابحث واشحن الموديل المستهدف من هنا --":
    final_search_term = selected_target

# الفحص الصارم والمطابقة بالاسم داخل قاعدة البيانات
size_str, panel, sensor, real_name = None, None, None, None
if final_search_term:
    size_str, panel, sensor, real_name = find_model_coords(db_data, final_search_term)

# التحقق من أن المكتوب مطابق لهاتف حقيقي موجود بالسيستم
is_exact_match = True if real_name and final_search_term.lower() == real_name.lower() else False

# مصفوفة داخلية لتجميع تقارير تدقيق الرادار العالمي حياً في لوحة التحكم
global_audit_alerts = []

# ============================================================
# تنفيذ الخطة 1: إذا كان الاسم متطابقاً تماماً وموجوداً في قاعدة البيانات
# ============================================================
if final_search_term and size_str and is_exact_match:
    st.markdown(f"<div class='section-title' style='text-align:right; color:white;'>📊 نتائج التوافق والمقاسات للهاتف: {real_name}</div>", unsafe_allow_html=True)
    
    draw_technical_coords(size_str, panel, sensor)
    results = get_compatibles_strict(db_data, final_search_term)
    
    if "exact" in results:
        exact_list = [m for m in results["exact"] if m not in results.get("warn", [])]
        draw_neon_section("هواتف مطابقة تماماً في الأبعاد والقص (Exact 0.00)", exact_list, "#2ecc71", "🟢", final_search_term)
        
    if "plus" in results:
        draw_neon_section("هواتف أكبر بقليل متوافقة (Plus +0.01 إلى +0.03)", results["plus"], "#3498db", "🔵", final_search_term)
        
    if "minus" in results:
        draw_neon_section("هواتف أصغر بقليل متوافقة (Minus -0.01 إلى -0.03)", results["minus"], "#e67e22", "🟤", final_search_term)
        
    if results.get("warn"):
        draw_neon_section("تنبيه حساس: هواتف بنفس المقاس ولكن بمستشعر مختلف:", results["warn"], "#ef4444", "⚠️", final_search_term)

    # وينتهي دور الخطة 1 تماماً قف

# ============================================================
# الخطة 2: تفتح فوراً وحراً عند كتابة هاتف جديد تماماً غير مسجل بالاسم (مثل Infinix Note 60)
# ============================================================
elif final_search_term and not is_exact_match:
    st.markdown("---")
    st.warning(f"⚠️ الهاتف ({final_search_term}) غير مسجل بالاسم الحرفي هذا. تم فتح الخطة 2 لإدخال مواصفاته يدوياً بالتتابع:")
    
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
        
        # رادار التدقيق العالمي يحلل صامتاً البيانات هنا خلف الكواليس
        global_data = ai_background_global_verify(final_search_term)
        if global_data and global_data["size"]:
            if new_size not in global_data["size"]:
                global_audit_alerts.append(f"🚨 تدقيق عالمي: هاتف `{final_search_term}` تم إدخاله بـ {new_size} والموثق سحابياً هو {global_data['size']}")

        matched_list = local_check_existing_size_group(db_data, new_size, new_panel)
        st.markdown("---")
        
        if matched_list:
            st.info("💡 **[الحالة ب]**: تم رصد مجموعة مقاسات وشاشات متطابقة مسبقاً في النظام!")
            st.markdown(f"🎯 **الموديلات المتوافقة مع مواصفات هاتف الزبون حالياً:** {', '.join(matched_list)}")
            
            if st.button("🔗 موافقة: دمج الموديل الجديد مع هذه المجموعة وتحديث السحاب فوراً", key="btn_merge_model"):
                if new_size not in db_data: db_data[new_size] = {}
                if new_panel not in db_data[new_size]: db_data[new_size][new_panel] = {}
                if new_sensor not in db_data[new_size][new_panel]: db_data[new_size][new_panel][new_sensor] = {"models": []}
                if isinstance(db_data[new_size][new_panel][new_sensor], list):
                    db_data[new_size][new_panel][new_sensor] = {"models": db_data[new_size][new_panel][new_sensor]}
                if final_search_term not in db_data[new_size][new_panel][new_sensor]["models"]:
                    db_data[new_size][new_panel][new_sensor]["models"].append(final_search_term)
                save_db(db_data)
                st.success(f"✅ تم دمج الموديل {final_search_term} وتحديث السحاب بنجاح!")
                st.rerun()

            # وينتهي دور الخطة 2 تماماً قف
            
        else:
            # ============================================================
            # الخطة 3: خطة الطوارئ النهائية تفتح وتفصل تلقائياً عند غياب المجموعات المطابقة
            # ============================================================
            st.error("❌ خطة الطوارئ (الخطة 3): لا توجد مجموعة تطابق هذه المواصفات في المكتبة.")
            
            if st.button("➕ إنشاء مجموعة جديدة وإدراج الهاتف كمرجع مستقبلي", key="btn_create_group"):
                if new_size not in db_data: db_data[new_size] = {}
                if new_panel not in db_data[new_size]: db_data[new_size][new_panel] = {}
                db_data[new_size][new_panel][new_sensor] = {"models": [final_search_term]}
                save_db(db_data)
                st.success(f"✅ تم تطبيق خطة الطوارئ: تم إنشاء المجموعة وحفظ الهاتف {final_search_term} بنجاح!")
                st.rerun()

            # وينتهي دور الخطة 3 تماماً قف

# تحديث وتمرير الإشعارات وحالة التنبيهات العالمية إلى لوحة التحكم الجانبية الحية لتظهر بالكامل
if global_audit_alerts:
    st.session_state.notifications = global_audit_alerts
else:

