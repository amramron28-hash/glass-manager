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

from smart_guard import (
    check_before_save,
    clean_database
)

from rapidfuzz import process, fuzz
from streamlit_searchbox import st_searchbox



# ==========================
# PAGE
# ==========================

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

inject_pwa_and_styles()



# ==========================
# SESSION
# ==========================

if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

if "show_success" not in st.session_state:
    st.session_state.show_success = ""

if "notifications" not in st.session_state:
    st.session_state.notifications = []



# ==========================
# OPTIONS
# ==========================

ALL_PANELS = [

    "Notch Screen",
    "Punch-Hole Screen",
    "Waterdrop Notch",
    "Full Screen",
    "Flat Screen",
    "Curved Screen"

]


ALL_SENSORS = [

    "hardware_top_sensor",
    "virtual_camera_sensor",
    "under_display_sensor",
    "side_sensor",
    "no_visible_sensor"

]



# ==========================
# LOAD DATABASE
# ==========================

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



# ==========================
# HEADER
# ==========================

st.markdown(
"""
<div style="
direction:ltr;
text-align:right;
margin-top:-25px;
">

<div style="
font-size:34px;
font-weight:900;
color:#00bfff;
">
ZEGAAR AMMAR
</div>

<div style="
font-size:34px;
font-weight:900;
color:#00bfff;
border-bottom:2px solid rgba(0,191,255,.3);
">
GLASS MANAGER
</div>

</div>
""",
unsafe_allow_html=True
)



# ==========================
# MESSAGE
# ==========================

if st.session_state.show_success:

    st.success(
        st.session_state.show_success
    )

    st.toast(
        st.session_state.show_success
    )

    st.session_state.show_success = ""



# ==========================
# SEARCH
# ==========================

def search_models(query):

    if not query:
        return unique_models[:10]


    try:

        result = process.extract(
            query,
            unique_models,
            limit=10,
            scorer=fuzz.WRatio
        )

        return [
            x[0]
            for x in result
        ]

    except:

        return []



selected = st_searchbox(

    search_function=lambda q, **k:
    search_models(q),

    placeholder="🔍 ابحث عن هاتف",

    key="phone_search"

)



if isinstance(selected,str):

    selected = selected.strip()

    if selected:

        st.session_state.custom_search_input = selected



manual = st.text_input(
    "اسم الهاتف الجديد"
)


if manual.strip():

    st.session_state.custom_search_input = manual.strip()



phone = st.session_state.custom_search_input



# ==========================
# PLAN 1
# ==========================

if phone:


    size, panel, sensor, real = find_model_coords(
        db_data,
        phone
    )


    if size:


        st.success(
            f"🎯 الهاتف موجود: {real}"
        )


        draw_technical_coords(
            size,
            panel,
            sensor
        )


        results = get_compatibles_strict(
            db_data,
            phone
        )


        draw_neon_section(
            "مطابق",
            results["exact"],
            "#2ecc71",
            "🎯",
            phone
        )



# ==========================
# PLAN 2 + 3
# ==========================


    else:


        st.warning(
            "الهاتف غير موجود"
        )


        final_size = st.text_input(
            "📏 المقاس",
            placeholder="مثال 6.78"
        )


        final_panel = ""
        final_sensor = ""



        if final_size.strip():


            panel = st.selectbox(

                "📺 نوع الشاشة",

                [""] +
                ALL_PANELS +
                live_panels +
                ["➕ إضافة جديد"]

            )


            if panel == "➕ إضافة جديد":

                final_panel = st.text_input(
                    "اكتب نوع الشاشة"
                )

            else:

                final_panel = panel



        if final_size.strip() and final_panel.strip():


            sensor = st.selectbox(

                "👁️ المستشعر التقارب",

                [""] +
                ALL_SENSORS +
                live_sensors +
                ["➕ إضافة جديد"]

            )


            if sensor == "➕ إضافة جديد":

                final_sensor = st.text_input(
                    "اكتب المستشعر"
                )

            else:

                final_sensor = sensor




        if (
            final_size.strip()
            and
            final_panel.strip()
            and
            final_sensor.strip()
        ):


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
                    "🤝 توجد مجموعة مطابقة"
                )


                if st.button(
                    "إضافة الهاتف للمجموعة"
                ):


                    ok, msg = check_before_save(

                        db_data,
                        final_size,
                        final_panel,
                        final_sensor,
                        phone

                    )


                    if ok:


                        add_model(
                            final_size,
                            final_panel,
                            final_sensor,
                            phone
                        )


                        st.session_state.show_success = (
                            "تمت الإضافة"
                        )

                        st.rerun()


                    else:

                        st.warning(msg)



            else:


                st.error(
                    "لا توجد مجموعة"
                )


                if st.button(
                    "إنشاء مجموعة جديدة"
                ):


                    ok, msg = check_before_save(

                        db_data,
                        final_size,
                        final_panel,
                        final_sensor,
                        phone

                    )


                    if ok:


                        add_model(
                            final_size,
                            final_panel,
                            final_sensor,
                            phone
                        )


                        st.session_state.show_success = (
                            "تم إنشاء المجموعة"
                        )

                        st.rerun()


                    else:

                        st.warning(msg)




# ==========================
# SIDEBAR
# ==========================

with st.sidebar:


    st.markdown(
        "## 🛠️ المراقب الصامت"
    )


    st.metric(
        "📱 الهواتف",
        total_models
    )


    st.metric(
        "⚠️ المجموعات الفارغة",
        empty_groups_count
    )


    st.write(
        datetime.date.today()
    )



    if st.button(
        "🧹 تنظيف وتصحيح"
    ):


        cleaned, count = clean_database(
            db_data
        )


        st.success(
            f"تم تنظيف {count} عنصر"
        )



    st.divider()


    st.write(
        "🔔 الإشعارات"
    )


    if st.session_state.notifications:

        for item in st.session_state.notifications:

            st.info(item)

    else:

        st.caption(
            "لا توجد إشعارات"
        )


    st.write(
        "⚙️ الإعدادات"
            )
