import streamlit as st
import datetime

from database import load_db, add_model, save_db

from logic_engine import (
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
# SESSION
# ===============================

if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

if "show_success_toast" not in st.session_state:
    st.session_state.show_success_toast = ""


# ===============================
# PAGE
# ===============================

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

inject_pwa_and_styles()



# ===============================
# LOAD DATA
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
# SILENT GUARD
# ===============================

unique_models = [
    str(x).strip()
    for x in unique_models
    if isinstance(x, str)
]

live_panels = [
    str(x).strip()
    for x in live_panels
    if x
]

live_sensors = [
    str(x).strip()
    for x in live_sensors
    if x
]



# ===============================
# HEADER
# ===============================

st.markdown(
"""
<div style="
direction:rtl;
text-align:right;
width:100%;
">

<span style="
font-size:32px;
font-weight:900;
color:#00bfff;
">
ZEGAAR AMMAR
</span>

<br>

<span style="
font-size:32px;
font-weight:900;
color:#00bfff;
">
GLASS MANAGER
</span>

</div>
""",
unsafe_allow_html=True
)



# ===============================
# TOAST
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
# SEARCH ENGINE
# ===============================

def search_models_callback(query, models):

    try:

        if not query:
            return models[:10]


        results = process.extract(
            query,
            models,
            limit=10,
            scorer=fuzz.WRatio
        )


        return [
            str(r[0])
            for r in results
        ]


    except:

        return []



selected_phone = st_searchbox(
    search_function=lambda q, **k:
    search_models_callback(q, unique_models),

    placeholder=
    "🔍 ابحث عن هاتف أو اكتب اسماً جديداً",

    key="phone_search"
)



if isinstance(selected_phone, str):

    selected_phone = selected_phone.strip()

    if selected_phone:

        st.session_state.custom_search_input = selected_phone



# ===============================
# MANUAL INPUT
# ===============================

if not selected_phone:


    manual = st.text_input(
        "اسم الهاتف الجديد"
    )


    manual = str(manual).strip()


    if manual:

        st.session_state.custom_search_input = manual



# ===============================
# PLAN 1
# ===============================

if st.session_state.custom_search_input:


    phone = st.session_state.custom_search_input


    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(
        db_data,
        phone
    )


    if size_grp:


        st.success(
            f"🎯 الهاتف موجود: {real_name}"
        )


        results = get_compatibles_strict(
            db_data,
            phone
        )


        draw_technical_coords(
            size_grp,
            panel_grp,
            sensor_grp
        )


        draw_neon_section(
            "مطابق",
            results["exact"],
            "#2ecc71",
            "🎯",
            phone
        )



# ===============================
# PLAN 2 + PLAN 3
# ===============================

    else:


        st.warning(
            "الهاتف غير موجود - أدخل المواصفات"
        )


        # 1 SIZE FREE

        final_size = st.text_input(
            "📏 أدخل مقاس الهاتف:",
            placeholder="مثال: 6.78"
        )


        final_panel = ""
        final_sensor = ""



        # 2 PANEL

        if final_size.strip():


            panel_choice = st.selectbox(
                "📺 اختر نوع الشاشة:",
                [""] +
                live_panels +
                ["➕ إضافة نوع شاشة جديد"]
            )


            if panel_choice == "➕ إضافة نوع شاشة جديد":


                final_panel = st.text_input(
                    "اكتب نوع الشاشة"
                )


            else:

                final_panel = panel_choice



        # 3 SENSOR

        if final_size.strip() and final_panel.strip():


            sensor_choice = st.selectbox(
                "👁️ اختر مستشعر التقارب:",
                [""] +
                live_sensors +
                ["➕ إضافة مستشعر جديد"]
            )


            if sensor_choice == "➕ إضافة مستشعر جديد":


                final_sensor = st.text_input(
                    "اكتب المستشعر"
                )


            else:

                final_sensor = sensor_choice



        final_size = str(final_size).strip()
        final_panel = str(final_panel).strip()
        final_sensor = str(final_sensor).strip()



        # MATCH GROUP

        if final_size and final_panel and final_sensor:


            group = (
                db_data
                .get(final_size,{})
                .get(final_panel,{})
                .get(final_sensor,{})
            )


            models = group.get(
                "models",
                []
            )


            if models:


                st.success(
                    "🤝 وجدت مجموعة مطابقة"
                )


                st.write(models)



                if st.button(
                    "إضافة الهاتف للمجموعة"
                ):


                    add_model(
                        final_size,
                        final_panel,
                        final_sensor,
                        phone
                    )


                    st.success(
                        "تمت الإضافة"
                    )


                    st.rerun()



            else:


                st.error(
                    "لا توجد مجموعة مطابقة"
                )


                if st.button(
                    "إنشاء مجموعة جديدة"
                ):


                    add_model(
                        final_size,
                        final_panel,
                        final_sensor,
                        phone
                    )


                    st.success(
                        "تم إنشاء مجموعة جديدة"
                    )


                    st.rerun()



# ===============================
# SILENT MONITOR
# ===============================

with st.sidebar:


    st.markdown(
        "## 🛠️ المراقب الصامت"
    )


    st.write(
        f"📅 {datetime.date.today()}"
    )


    st.metric(
        "📱 عدد الهواتف",
        total_models
    )


    st.metric(
        "⚠️ مجموعات فارغة",
        empty_groups_count
    )



    if st.button(
        "🧹 تشغيل الفحص والتنظيف"
    ):


        cleaned, changes = run_intelligent_inspector(
            db_data
        )


        if changes:

            st.success(
                "تم تنظيف البيانات"
            )

            st.rerun()

        else:

            st.info(
                "قاعدة البيانات سليمة"
        )
