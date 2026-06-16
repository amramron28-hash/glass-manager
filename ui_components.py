import streamlit as st
import os
import base64


_bg_cache = None



# ==========================================
# 🎨 الخلفية والتصميم
# ==========================================

def inject_pwa_and_styles():

    global _bg_cache


    if _bg_cache is None:


        paths = [
            "phone_image.webp",
            "./phone_image.webp",
            "/app/phone_image.webp"
        ]


        img = ""


        for p in paths:

            if os.path.exists(p):

                with open(p,"rb") as f:

                    img = base64.b64encode(
                        f.read()
                    ).decode()

                break


        _bg_cache = img



    st.markdown(
    f"""
    <style>

    html,body,[data-testid="stAppViewContainer"] {{

        background-image:
        linear-gradient(
        rgba(10,14,23,.45),
        rgba(10,14,23,.45)
        ),
        url(
        'data:image/webp;base64,{_bg_cache}'
        );

        background-size:cover;
        background-attachment:fixed;

    }}



    .neon-card-text {{

        font-size:24px;
        font-weight:900;
        color:white;

    }}

    </style>
    """,
    unsafe_allow_html=True
    )





# ==========================================
# 📋 بطاقة التحليل الفني
# ==========================================

def draw_technical_coords(
    size_grp,
    panel_grp,
    sensor_grp
):


    st.markdown(
    f"""

<div style="
background:rgba(15,23,42,.85);
padding:25px;
border-radius:12px;
border:2px dashed #00bfff;
">

<h3 style="
text-align:center;
color:#00bfff;
">
📋 تحليل الإحداثيات الفنية
</h3>


<div style="
display:flex;
justify-content:space-around;
text-align:center;
direction:rtl;
">


<div>
<p>📏 المقاس</p>
<h4>{size_grp}</h4>
</div>


<div>
<p>📺 نوع الشاشة</p>
<h4>{panel_grp}</h4>
</div>


<div>
<p>👁️ المستشعر التقارب</p>
<h4>{sensor_grp}</h4>
</div>


</div>


</div>

    """,
    unsafe_allow_html=True
    )





# ==========================================
# 🟦 كروت النتائج
# ==========================================

def draw_neon_section(
    title,
    models_list,
    color_hex,
    badge_icon,
    current_search
):


    if not models_list:

        return



    st.markdown(
    f"""
    <h3 style="color:{color_hex}">
    {badge_icon} {title}
    </h3>
    """,
    unsafe_allow_html=True
    )



    cols = st.columns(4)



    for i,model in enumerate(models_list):


        with cols[i%4]:

            st.markdown(
            f"""

<div class="neon-card-text"
style="
background:{color_hex};
padding:15px;
border-radius:10px;
text-align:center;
">

🔹 {model}

</div>

            """,
            unsafe_allow_html=True
            )





# ==========================================
# 🛠️ لوحة التحكم
# ==========================================

def draw_control_panel(
    notifications=None,
    total_models=0,
    empty_groups_count=0
):


    notifications = notifications or []



    with st.sidebar:



        st.markdown(
        """
        <h2 style="
        text-align:center;
        color:#00bfff;
        ">
        🛠️ المراقب الصامت
        </h2>
        """,
        unsafe_allow_html=True
        )



        with st.expander(
            "🔔 الإشعارات"
        ):


            if notifications:


                for n in notifications:

                    st.warning(n)


            else:

                st.success(
                    "لا توجد تنبيهات"
                )



        with st.expander(
            "⚙️ الإعدادات"
        ):


            st.toggle(
                "🧠 تفعيل المراقب الذكي",
                True
            )



        with st.expander(
            "🛡️ حالة المراقب الصامت",
            expanded=True
        ):


            st.metric(
                "📱 إجمالي الهواتف",
                total_models
            )


            st.metric(
                "🧹 مجموعات للمراجعة",
                empty_groups_count
            )


            st.caption(
                "المراقب جاهز للتحليل قبل الإدراج"
            )
