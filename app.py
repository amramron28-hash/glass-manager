import streamlit as st
import datetime

from database import add_model

from logic_engine import (
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

from app_init import initialize_system_data

from rapidfuzz import process, fuzz
from streamlit_searchbox import st_searchbox



st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)



inject_pwa_and_styles()



@st.cache_data(ttl=300)
def load_system_data():

    return initialize_system_data()



if "custom_search_input" not in st.session_state:

    st.session_state.custom_search_input = ""



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





# ==========================
# الشعار
# ==========================

st.markdown(
"""
<div style="
width:100%;
direction:ltr;
text-align:left;
margin-top:-55px;
padding:0;
white-space:nowrap;
overflow:hidden;
">

<div style="
font-size:28px;
font-weight:900;
letter-spacing:1px;
color:#00bfff;
font-family:Arial,sans-serif;
text-shadow:0 0 12px rgba(0,191,255,.7);
line-height:1;
">
ZEGAAR AMMAR
</div>

<div style="
font-size:28px;
font-weight:900;
letter-spacing:1px;
color:#00bfff;
font-family:Arial,sans-serif;
text-shadow:0 0 12px rgba(0,191,255,.7);
border-bottom:1px solid rgba(0,191,255,.35);
padding-bottom:3px;
line-height:1;
">
GLASS MANAGER
</div>

</div>
""",
unsafe_allow_html=True
)




# ==========================
# رسالة النجاح
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
# البحث الحقيقي للستارة
# ==========================

def search_models(q):


    if not q:

        return []



    q_clean = q.lower().strip()



    try:


        matches = []



        for model in unique_models:


            name = model.lower().strip()


            words = q_clean.split()



            if all(

                word in name

                for word in words

            ):


                matches.append(model)




        if matches:


            return matches[:10]





        fuzzy_results = process.extract(

            q,

            unique_models,

            limit=10,

            scorer=fuzz.WRatio

        )



        suggestions = []



        for item in fuzzy_results:


            name = item[0]

            score = item[1]



            if score >= 92:


                suggestions.append(name)




        return suggestions




    except:


        return []





selected = st_searchbox(

    search_function=lambda q, **k:

    search_models(q),

    placeholder="🔍 ابحث عن هاتف",

    key="phone_search"

)



if isinstance(selected, str):


    selected = selected.strip()



    if selected:


        st.session_state.custom_search_input = selected



phone = st.session_state.custom_search_input
# ==========================
# البحث والنتائج
# ==========================

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

                "📺 نوع الشاشة",

                [""]

                + ALL_PANELS

                + live_panels

                + ["➕ إضافة جديد"]

            )



            if final_panel == "➕ إضافة جديد":


                final_panel = st.text_input(

                    "اكتب نوع الشاشة"

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






        final_size = str(final_size).strip()

        final_panel = str(final_panel).strip()

        final_sensor = str(final_sensor).strip()





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



                    st.session_state.custom_search_input = ""

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



                    st.session_state.custom_search_input = ""

                    st.session_state.show_success = "تم إنشاء المجموعة"

                    st.rerun()







# ==========================
# لوحة التحكم
# ==========================

draw_control_panel(

    notifications=st.session_state.notifications,

    total_models=total_models,

    empty_groups_count=empty_groups_count

    )
