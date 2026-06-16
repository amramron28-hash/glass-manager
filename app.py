import streamlit as st
import datetime
import os
import sys


# ==================================
# تثبيت مسار المشروع
# ==================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:
    sys.path.insert(
        0,
        BASE_DIR
    )


# ==================================
# قواعد البيانات
# ==================================

from database import (
    load_db,
    add_model,
    save_db
)



# ==================================
# محرك البحث
# ==================================

from logic_engine import (
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)



# ==================================
# الواجهة
# ==================================

from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section
)



# ==================================
# تهيئة البيانات
# ==================================

from app_init import (
    initialize_system_data
)



# ==================================
# المراقب الصامت
# ==================================

try:

    from smart_guard import (
        check_before_save,
        clean_database
    )

    SMART_GUARD_ACTIVE = True


except Exception as error:


    SMART_GUARD_ACTIVE = False


    def check_before_save(
        db,
        size,
        panel,
        sensor,
        model
    ):

        return True, "المراقب غير مفعل"



    def clean_database(db):

        return db,0



# ==================================
# مكتبات البحث
# ==================================

from rapidfuzz import (
    process,
    fuzz
)

from streamlit_searchbox import (
    st_searchbox
)



# ==================================
# إعداد الصفحة
# ==================================

st.set_page_config(

    layout="wide",

    page_title="ZEGAAR AMMAR GLASS MANAGER",

    page_icon="🔍"

)



inject_pwa_and_styles()



# ==================================
# جلسة التطبيق
# ==================================

if "custom_search_input" not in st.session_state:

    st.session_state.custom_search_input = ""


if "show_success" not in st.session_state:

    st.session_state.show_success = ""



# ==================================
# تحميل البيانات
# ==================================

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



# ==================================
# عنوان التطبيق
# ==================================

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



# ==================================
# حالة المراقب
# ==================================

if SMART_GUARD_ACTIVE:

    st.sidebar.success(
        "🛡️ المراقب الصامت يعمل"
    )

else:

    st.sidebar.warning(
        "⚠️ المراقب الصامت غير محمل"
    )
