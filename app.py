import streamlit as st

from database import add_model

from logic_engine import (
    find_model_coords,
    get_compatibles_strict
)

from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section,
    draw_control_panel
)

from app_init import initialize_system_data



st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)



inject_pwa_and_styles()



@st.cache_data(ttl=300)
def load_system_data():
    return initialize_system_data()



if "notifications" not in st.session_state:
    st.session_state.notifications = []


if "show_success" not in st.session_state:
    st.session_state.show_success = ""





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





(
    db_data,
    unique_models,
    total_models,
    empty_groups_count,
    brand_counts,
    live_sizes,
    live_panels,
    live_sensors

) = load_system_data()





unique_models = [

    str(x).strip()

    for x in unique_models

    if x

]





st.markdown(
"""
<div style="
font-size:28px;
font-weight:900;
color:#00bfff;
text-shadow:0 0 12px rgba(0,191,255,.7);
">
ZEGAAR AMMAR<br>
GLASS MANAGER
</div>
""",
unsafe_allow_html=True
)





if st.session_state.show_success:

    st.success(
        st.session_state.show_success
    )

    st.session_state.show_success = ""





# ==========================
# البحث بحقل واحد
# ==========================

phone = st.text_input(

    "📱 اسم الهاتف",

    placeholder="مثال: Infinix Note 60"

).strip()





if phone:


    size, panel, sensor, real = find_model_coords(

        db_data,

        phone

    )


    if size:


        st.success(

            f"🎯 الهاتف موجود : {real}"

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

            "مطابق ±0.03",

            results["exact"],

            "#2ecc71",

            "🎯",

            phone

        )



        draw_neon_section(

            "أكبر بقليل ±0.03",

            results["plus"],

            "#3498db",

            "➕",

            phone

        )



        draw_neon_section(

            "أصغر بقليل ±0.03",

            results["minus"],

            "#e67e22",

            "➖",

            phone

        )



        draw_neon_section(

            "تحذير مستشعر مختلف",

            results["warn"],

            "#ef4444",

            "⚠️",

            phone

        )





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


            final_panel = st.selectbox(

                "📺 شكل الشاشة",

                [""]

                + ALL_PANELS

                + live_panels

                + ["➕ إضافة جديد"]

            )



            if final_panel == "➕ إضافة جديد":


                final_panel = st.text_input(

                    "اكتب شكل الشاشة"

                )





        if final_size.strip() and final_panel.strip():


            final_sensor = st.selectbox(

                "👁️ المستشعر التقارب",

                [""]

                + ALL_SENSORS

                + live_sensors

                + ["➕ إضافة جديد"]

            )



            if final_sensor == "➕ إضافة جديد":


                final_sensor = st.text_input(

                    "اكتب المستشعر"

                )





        if final_size and final_panel and final_sensor:



            group = (

                db_data

                .get(final_size, {})

                .get(final_panel, {})

                .get(final_sensor, {})

            )



            models = group.get(

                "models",

                []

            )





            if models:



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


                    st.session_state.show_success = "تمت الإضافة"

                    st.rerun()





            else:



                st.warning(

                    "لا توجد مجموعة"

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


                    st.session_state.show_success = "تم إنشاء المجموعة"

                    st.rerun()







draw_control_panel(

    notifications=st.session_state.notifications,

    total_models=total_models,

    empty_groups_count=empty_groups_count

            )
