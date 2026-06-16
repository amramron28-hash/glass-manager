import streamlit as st
import datetime

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


# ===============================
# حماية الجلسة
# ===============================

if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

if "show_success_toast" not in st.session_state:
    st.session_state.show_success_toast = ""


# ===============================
# إعداد الصفحة
# ===============================

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

inject_pwa_and_styles()


# ===============================
# تحميل البيانات
# ===============================

(
    db_data,
    unique_models,
    total_models,
    empty_groups_count,
    brand_counts,
    live_sizes,
    live_panels,
    live_sensors
) = initialize_system_data()


# ===============================
# المراقب الصامت
# تنظيف البيانات
# ===============================

unique_models = [
    str(x).strip()
    for x in unique_models
    if isinstance(x, str) and str(x).strip()
]


live_sizes = [
    str(x).strip()
    for x in live_sizes
    if x is not None
]


live_panels = [
    str(x).strip()
    for x in live_panels
    if x is not None
]


live_sensors = [
    str(x).strip()
    for x in live_sensors
    if x is not None
]


# ===============================
# العنوان
# ===============================

st.markdown(
    """
    <div style="width:100%;text-align:right;direction:rtl;">
    <span style="font-size:32px;font-weight:900;color:#00bfff;">
    ZEGAAR AMMAR
    </span>
    <br>
    <span style="font-size:32px;font-weight:900;color:#00bfff;">
    GLASS MANAGER
    </span>
    </div>
    """,
    unsafe_allow_html=True
)


# ===============================
# إشعار النجاح
# ===============================

if st.session_state.show_success_toast:

    st.success(
        st.session_state.show_success_toast
    )

    st.toast(
        st.session_state.show_success_toast
    )

    st.session_state.show_success_toast = ""


# ===============================
# البحث الذكي
# ===============================

def search_models_callback(query, models_list):

    try:

        clean_models = [
            str(m).strip()
            for m in models_list
            if isinstance(m, str)
        ]

        if not query:
            return clean_models[:10]


        results = process.extract(
            query,
            clean_models,
            limit=10,
            scorer=fuzz.WRatio
        )


        return [
            str(r[0])
            for r in results
        ]


    except Exception:

        return []



selected_phone = st_searchbox(
    search_function=lambda q, **k:
        search_models_callback(q, unique_models),

    placeholder=
    "🔍 ابحث عن هاتف أو اكتب اسماً جديداً",

    key="phone_search_autocomplete_v9"
)



# حماية الخطأ
if isinstance(selected_phone, str):

    selected_phone = selected_phone.strip()

    if selected_phone:

        st.session_state.custom_search_input = selected_phone



# ===============================
# إدخال يدوي
# ===============================


if not selected_phone:


    custom_typed = st.text_input(
        "اسم الهاتف الجديد",
        placeholder="اكتب اسم الهاتف",
        key="manual_input_v9"
    )


    custom_typed = str(custom_typed).strip()


    if custom_typed:

        st.session_state.custom_search_input = custom_typed



# ===============================
# الخطة 1 - 2 - 3
# ===============================


if st.session_state.custom_search_input:


    current_search = (
        st.session_state.custom_search_input
    )


    st.info(
        f"📱 الهاتف الحالي: {current_search}"
    )


    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(
        db_data,
        current_search
    )



    # ===============================
    # المرحلة 1
    # ===============================


    if size_grp:


        compat_results = get_compatibles_strict(
            db_data,
            current_search
        )


        st.success(
            f"🎯 الهاتف موجود: {real_name}"
        )


        draw_technical_coords(
            size_grp,
            panel_grp,
            sensor_grp
        )


        draw_neon_section(
            "مطابق",
            compat_results["exact"],
            "#2ecc71",
            "🎯",
            current_search
        )


        draw_neon_section(
            "أكبر قليلاً",
            compat_results["plus"],
            "#3498db",
            "➕",
            current_search
        )


        draw_neon_section(
            "أصغر قليلاً",
            compat_results["minus"],
            "#e67e22",
            "➖",
            current_search
        )


        draw_neon_section(
            "تحذير مستشعر",
            compat_results["warn"],
            "#ef4444",
            "⚠️",
            current_search
        )



    # ===============================
    # المرحلة 2
    # ===============================


    else:


        st.warning(
            "الهاتف غير موجود، اختر مواصفاته"
        )


        sel_size = st.selectbox(
            "📏 المقاس",
            [""] + live_sizes
        )


        sel_panel = st.selectbox(
            "📺 نوع الشاشة",
            [""] + live_panels
        )


        sel_sensor = st.selectbox(
            "👁️ المستشعر",
            [""] + live_sensors
        )



        final_size = str(sel_size).strip()

        final_panel = str(sel_panel).strip()

        final_sensor = str(sel_sensor).strip()



        has_group = False



        if final_size and final_panel and final_sensor:


            if (
                final_size in db_data
                and final_panel in db_data[final_size]
                and final_sensor in db_data[final_size][final_panel]
            ):


                models = db_data[final_size][final_panel][final_sensor].get(
                    "models",
                    []
                )


                if models:


                    has_group = True


                    st.success(
                        "🤝 وجدنا مجموعة مطابقة"
                    )


                    if st.button(
                        "إضافة الهاتف للمجموعة"
                    ):


                        add_model(
                            final_size,
                            final_panel,
                            final_sensor,
                            current_search
                        )


                        st.success(
                            "تمت الإضافة"
                        )

                        st.rerun()



        # ===============================
        # المرحلة 3
        # ===============================


        if (
            final_size
            and final_panel
            and final_sensor
            and not has_group
        ):


            st.error(
                "لا توجد مجموعة، سيتم إنشاء مجموعة جديدة"
            )


            if st.button(
                "إنشاء مجموعة جديدة"
            ):


                add_model(
                    final_size,
                    final_panel,
                    final_sensor,
                    current_search
                )


                st.success(
                    "تم إنشاء المجموعة"
                )

                st.rerun()



# ===============================
# المراقب الصامت
# ===============================

with st.sidebar:


    st.title(
        "🛠️ المراقب الصامت"
    )


    st.write(
        f"📅 {datetime.date.today()}"
    )


    st.metric(
        "📱 الهواتف",
        total_models
    )


    st.metric(
        "⚠️ مجموعات فارغة",
        empty_groups_count
    )



    if st.button(
        "🧹 تنظيف السحابة"
    ):


        cleaned, changed = run_intelligent_inspector(
            db_data
        )


        if changed:

            st.success(
                "تم تنظيف البيانات"
            )

            st.rerun()

        else:

            st.info(
                "البيانات نظيفة"
)
