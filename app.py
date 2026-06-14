import streamlit as st
import datetime

from database import save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)

# استيراد الوظائف الذكية والصارمة للفصل التام بين المراحل الثلاث
from ui_logic import (
    search_models_callback,
    process_new_model_form
)

from streamlit_searchbox import st_searchbox

from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section
)

from app_init import initialize_system_data

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

inject_pwa_and_styles()

db_data, unique_models, total_models, empty_groups_count, brand_counts = initialize_system_data()

# ==========================================
# 🛠️ اللوحة الجانبية (المراقب الصامت الذكي)
# ==========================================
with st.sidebar:
    st.markdown(
        "<h2 style='text-align:right;color:#00bfff;'>🛠️ المراقب الصامت</h2>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    with st.expander("🔔 جرس الإشعارات اللحظي", expanded=True):
        st.info("💡 النظام سحابي مستقر 100% وعين المراقب الصامت نشطة حياً لحماية الشجرة.")

    with st.expander("⚙️ الإعدادات والتحكم بالـ RAM", expanded=True):
        st.write(
            f"📅 تاريخ اليوم الفني: **{datetime.date.today().strftime('%Y-%m-%d')}**"
        )
        st.metric(
            label="📈 إجمالي الهواتف بالسيستم",
            value=total_models
        )
        st.markdown("---")

        if brand_counts:
            # ترتيب وعرض البراندات التلقائي لمنع الأخطاء الفنية
            for b_name, b_count in sorted(
                brand_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:4]:
                percentage = round(
                    (b_count / total_models) * 100,
                    1
                ) if total_models else 0

                st.markdown(
                    f"📋 <b>{b_name}</b>: {b_count} ({percentage}%)",
                    unsafe_allow_html=True
                )
                st.progress(percentage / 100)

        st.markdown("---")

        if st.button(
            "🧹 تشغيل الصيانة وتطهير الشجرة",
            key="sidebar_inspector_btn"
        ):
            cleaned_db, changes_made = run_intelligent_inspector(db_data)
            if changes_made:
                save_db(cleaned_db)
                st.success("✨ تم تطهير الشجرة وترتيب الموديلات بنجاح!")
                st.rerun()
            else:
                st.toast("🎯 السيستم مطهر ونظيف بالكامل مسبقاً.")
# ==========================================
# 📱 الواجهة الرئيسية (العنوان الممتد بالكامل على طول الشاشة يمين ويسار)
# ==========================================

# 🌆 السطر الأول للعنوان بكامل عرض الشاشة الفعلي وبحجم ضخم
st.markdown(
    """
    <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; padding: 0px 5px; border-bottom: 1px solid rgba(0, 191, 255, 0.2);">
        <span style="font-size: 40px; font-weight: 900; color: #00bfff; font-family: 'Courier New', monospace; letter-spacing: 1px;">ZEGAAR AMMAR</span>
        <span style="font-size: 40px; font-weight: 900; color: #00bfff; font-family: 'Cairo', sans-serif;" dir="rtl">زغار عمار</span>
    </div>
    """, 
    unsafe_allow_html=True
)

# 🌆 السطر الثاني للعنوان متناظر وممتد تماماً وبنفس مقاس الخط الفخم
st.markdown(
    """
    <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding: 0px 5px;">
        <span style="font-size: 40px; font-weight: 900; color: #00bfff; font-family: 'Courier New', monospace; letter-spacing: 1px;">GLASS MANAGER</span>
        <span style="font-size: 40px; font-weight: 900; color: #00bfff; font-family: 'Cairo', sans-serif;" dir="rtl">مدير الشاشات والزجاج</span>
    </div>
    """, 
    unsafe_allow_html=True
)

if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

# شريط البحث المتطور والمراقب حياً
selected_phone = st_searchbox(
    search_function=lambda q, **k: search_models_callback(
        q,
        unique_models
    ),
    placeholder="🔍 ادخل اسم هاتف الزبون هنا لفحص التوافق اللحظي...",
    key="phone_search_autocomplete",
    label=""
)

# 🔒 بوابة الأمان: عند كتابة هاتف جديد أو مسح الحقل، يتم تصفير المرحلة فوراً لحماية الخطة من التداخل
if selected_phone and selected_phone.strip() != st.session_state.custom_search_input:
    st.session_state.custom_search_input = selected_phone.strip()
    st.session_state.current_stage = 2  # فرض الرجوع للمرحلة الثانية لضمان الفحص المعزول

if st.session_state.custom_search_input:
    current_search = st.session_state.custom_search_input
    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(
        db_data,
        current_search
    )

    # -------------------------------------------------------------
    # 📌 المرحلة الأولى: الهاتف مسجل وموجود بالفعل بالسيستم (تم فحص المطابقة والإنهاء)
    # -------------------------------------------------------------
    if size_grp:
        compat_results = get_compatibles_strict(
            db_data,
            current_search
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.success(
            f"🎯 الموديل [{real_name}] مسجل ومتوافق حياً في النظام!"
        )

        # رسم كروت الأبعاد الفنية للمجموعة
        draw_technical_coords(
            size_grp,
            panel_grp,
            sensor_grp
        )

        # إنتاج الأقسام الملونة بالكامل (ملء الخلفية بالألوان المحددة)
        draw_neon_section(
            "مطابقة للمقاس تماماً (Exact Matches)",
            compat_results["exact"],
            "#2ecc71", # أخضر مصمت
            "🎯",
            current_search
        )

        draw_neon_section(
            "أكبر بقليل (Plus Sizes)",
            compat_results["plus"],
            "#3498db", # أزرق مصمت
            "➕",
            current_search
        )

        draw_neon_section(
            "أصغر بقليل (Minus Sizes)",
            compat_results["minus"],
            "#e67e22", # برتقالي مصمت
            "➖",
            current_search
        )

        draw_neon_section(
            "مستشعر مختلف (Warning)",
            compat_results["warn"],
            "#ef4444", # أحمر مصمت للتحذير
            "⚠️",
            current_search
        )

    # -------------------------------------------------------------
    # 📌 المرحلة الثانية والثالثة: تدار بشكل صارم ومستقل لحظر تداخل الواجهات والنوافذ مسبقاً
    # -------------------------------------------------------------
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(
            f"⚠️ الموديل [{current_search}] غير مسجل داخل النظام حالياً."
        )

        # استدعاء دالة المنطق المعزولة لحماية وتدفق المراحل الفنية خطوة بخطوة
        process_new_model_form(
            db_data,
            current_search
        )
