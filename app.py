import streamlit as st
import os
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

# الشعار ذو السطرين وعرض الشاشة الكامل بتوهج نيون أزرق فخم كما أمرت حرفياً
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

# الستارة المنسدلة الاحترافية الحقيقية (صندوق خيارات واحد يدعم البحث اللحظي بالكتابة)
dropdown_options = ["-- ابحث واشحن الموديل المستهدف من هنا --", "[ ➕ إضافة هاتف جديد غير مدرج بالنظام ]"] + unique_models

selected_target = st.selectbox(
    "البحث والمطابقة الفورية للموديلات:",
    options=dropdown_options,
    label_visibility="collapsed",
    key="unified_smart_search_box"
)

final_search_term = ""
show_workflow_box = False

if selected_target == "[ ➕ إضافة هاتف جديد غير مدرج بالنظام ]":
    show_workflow_box = True
elif selected_target != "-- ابحث واشحن الموديل المستهدف من هنا --":
    final_search_term = selected_target

# ============================================================
# الخطة 1: عرض نتائج التوافق والمطابقة الذكية للهاتف المختار من الستارة
# ============================================================
if final_search_term:
    size_str, panel, sensor, real_name = find_model_coords(db_data, final_search_term)
    
    if size_str:
        st.markdown(f"<div class='section-title' style='text-align:right; color:white;'>📊 نتائج التوافق والمقاسات للهاتف: {real_name}</div>", unsafe_allow_html=True)
        
        # استدعاء بطاقة الإحداثيات الفنية الزجاجية الأصلية الخاصة بك
        draw_technical_coords(size_str, panel, sensor)
        
        results = get_compatibles_strict(db_data, final_search_term)
        
        # استدعاء بطاقات النتائج النيون الملونة والزجاجية لتوزيع الهواتف المتوافقة بألوانها الأصلية المشرقة
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
# الخطة 2: تظهر تفاعلياً عند اختيار خيار إضافة هاتف جديد من القائمة
# ============================================================
elif show_workflow_box:
    st.markdown("---")
    st.markdown("<div class='section-title' style='text-align:right; color:white;'>📝 إدخال مواصفات هاتف جديد للفحص والمطابقة الحية:</div>", unsafe_allow_html=True)
    
    new_model_name = st.text_input("✍️ اسم الهاتف الجديد بالكامل (مثال: Infinix Hot 50 Pro):", key="workflow_new_name")
    
    col_s, col_p, col_se = st.columns(3)
    with col_s:
        new_size = st.text_input("📐 1. المقاس الرقمي للزبون (مثال: 6.67):", key="workflow_size")
    
    new_panel = ""
    new_sensor = ""

    # تتابع تفاعلي مشروط لظهور القوائم تدريجياً تالياً للخطوات اليدوية لمنع الازدحام البصري
    if new_size.strip():
        with col_p:
            new_panel = st.selectbox("🖥️ 2. نوع الشاشة الهيكلي:", ["", "Punch-Hole Screen", "Notch Screen", "Waterdrop Notch", "Full Screen", "Flat Screen", "Curved Screen"], key="workflow_panel")

    if new_size.strip() and str(new_panel).strip():
        with col_se:
            new_sensor = st.selectbox("👁️ 3. مستشعر التقارب المكتشف والمراقب:", ["", "hardware_top_sensor", "virtual_camera_sensor", "under_display_fingerprint", "under_display_sensor", "side_sensor", "no_visible_sensor"], key="workflow_sensor")
        
    if new_model_name and new_size.strip() and str(new_panel).strip() and str(new_sensor).strip():
        new_model_name = new_model_name.strip()
        new_size = new_size.strip()
        new_panel = str(new_panel).strip()
        new_sensor = str(new_sensor).strip()
        
        # استدعاء الدالة المحلية المتوافقة لفحص وجود المجموعة بالمكتبة
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
                if new_model_name not in db_data[new_size][new_panel][new_sensor]["models"]:
                    db_data[new_size][new_panel][new_sensor]["models"].append(new_model_name)
                save_db(db_data)
                st.success(f"✅ تم دمج الموديل {new_model_name} وتحديث شجرة الـ JSON بنجاح!")
                st.rerun()

            # وينتهي دور الخطة 2 تماماً قف
            
        else:
            # ============================================================
            # الخطة 3: خطة الطوارئ النهائية تبدأ مباشرة عند انعدام المجموعات المطابقة
            # ============================================================
            st.warning("🟡 لا توجد مجموعة مطابقة مسبقاً لهذا المقاس/نوع الشاشة في قاعدة البيانات.")
            
            if st.button("➕ إنشاء مجموعة جديدة وإدراج الهاتف كمرجع مستقبلي", key="btn_create_group"):
                if new_size not in db_data: db_data[new_size] = {}
                if new_panel not in db_data[new_size]: db_data[new_size][new_panel] = {}
                db_data[new_size][new_panel][new_sensor] = {"models": [new_model_name]}
                save_db(db_data)
                st.success(f"✅ تم إنشاء المجموعة الهيكلية الجديدة وحفظ الهاتف {new_model_name} بنجاح!")
                st.rerun()

            # وينتهي دور الخطة 3 تماماً قف

# تشغيل العدادات والمراقب الصامت في الشريط الجانبي من ملف الـ UI الخاص بك
draw_control_panel(total_models=total_models, empty_groups_count=empty_groups_count)
