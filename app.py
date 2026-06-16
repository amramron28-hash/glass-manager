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


# ==========================
# حماية الجلسة
# ==========================

if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

if "show_success_toast" not in st.session_state:
    st.session_state.show_success_toast = ""


# ==========================
# إعداد الصفحة
# ==========================

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

inject_pwa_and_styles()


# ==========================
# تحميل البيانات
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
# المراقب الصامت
# تنظيف
# ==========================

unique_models = [
    str(x).strip()
    for x in unique_models
    if isinstance(x, str)
]


live_sizes = [
    str(x).strip()
    for x in live_sizes
]


live_panels = [
    str(x).strip()
    for x in live_panels
]


live_sensors = [
    str(x).strip()
    for x in live_sensors
]



# ==========================
# البحث
# ==========================

def search_models_callback(query, models):

    try:

        if not query:
            return models[:10]


        result = process.extract(
            query,
            models,
            limit=10,
            scorer=fuzz.WRatio
        )


        return [
            str(x[0])
            for x in result
        ]


    except:

        return []



selected_phone = st_searchbox(
    search_function=lambda q, **k:
    search_models_callback(q, unique_models),

    placeholder="🔍 ابحث عن الهاتف",

    key="phone_search"
)



if isinstance(selected_phone, str):

    selected_phone = selected_phone.strip()

    if selected_phone:

        st.session_state.custom_search_input = selected_phone



# ==========================
# إدخال يدوي
# ==========================


if not selected_phone:


    manual = st.text_input(
        "اسم هاتف جديد"
    )


    manual = str(manual).strip()


    if manual:

        st.session_state.custom_search_input = manual



# ==========================
# الخطة 1
# ==========================


if st.session_state.custom_search_input:


    phone = st.session_state.custom_search_input


    st.info(
        f"📱 الهاتف: {phone}"
    )


    size, panel, sensor, real_name = find_model_coords(
        db_data,
        phone
    )


    if size:


        st.success(
            f"🎯 الهاتف موجود: {real_name}"
        )


        results = get_compatibles_strict(
            db_data,
            phone
        )


        draw_technical_coords(
            size,
            panel,
            sensor
        )


        draw_neon_section(
            "مطابق",
            results["exact"],
            "#2ecc71",
            "🎯",
            phone
        )



# ==========================
# الخطة 2
# ==========================


    else:


        st.warning(
            "الهاتف غير موجود - أدخل المواصفات"
        )


        st.subheader(
            "⚙️ مواصفات الهاتف"
        )



        # المقاس

        size_choice = st.selectbox(
            "📏 المقاس",
            [""] + live_sizes + ["➕ مقاس جديد"]
        )


        if size_choice == "➕ مقاس جديد":

            final_size = st.text_input(
                "اكتب المقاس"
            )

        else:

            final_size = size_choice



        # الشاشة

        final_panel = ""


        if str(final_size).strip():


            panel_choice = st.selectbox(
                "📺 نوع الشاشة",
                [""] + live_panels + ["➕ نوع شاشة جديد"]
            )


            if panel_choice == "➕ نوع شاشة جديد":

                final_panel = st.text_input(
                    "اكتب نوع الشاشة"
                )

            else:

                final_panel = panel_choice



        # المستشعر

        final_sensor = ""


        if str(final_size).strip() and str(final_panel).strip():


            sensor_choice = st.selectbox(
                "👁️ المستشعر",
                [""] + live_sensors + ["➕ مستشعر جديد"]
            )


            if sensor_choice == "➕ مستشعر جديد":

                final_sensor = st.text_input(
                    "اكتب المستشعر"
                )

            else:

                final_sensor = sensor_choice



        final_size = str(final_size).strip()
        final_panel = str(final_panel).strip()
        final_sensor = str(final_sensor).strip()



        # ==========================
        # البحث عن مجموعة
        # ==========================


        if final_size and final_panel and final_sensor:


            exists = False


            try:

                group = db_data.get(final_size, {}) \
                    .get(final_panel, {}) \
                    .get(final_sensor, {})


                models = group.get(
                    "models",
                    []
                )


                if models:

                    exists = True


                    st.success(
                        "🤝 توجد مجموعة مطابقة"
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



            except:

                exists = False



            # ==========================
            # الخطة 3
            # ==========================


            if not exists:


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



# ==========================
# المراقب الصامت
# ==========================


with st.sidebar:


    st.title(
        "🛠️ المراقب الصامت"
    )


    st.write(
        datetime.date.today()
    )


    st.metric(
        "📱 عدد الهواتف",
        total_models
    )


    if st.button(
        "🧹 تنظيف"
    ):


        run_intelligent_inspector(
            db_data
        )


        st.success(
            "تم الفحص"
        )
