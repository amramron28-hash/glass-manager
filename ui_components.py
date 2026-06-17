import streamlit as st
import os
import base64


_bg_cache = None


# ==========================================
# 🎨 الخلفية + التنسيق
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

                with open(p, "rb") as f:

                    img = base64.b64encode(
                        f.read()
                    ).decode()

                break


        _bg_cache = img



    st.markdown(
    f"""
<style>

html,body,[data-testid="stAppViewContainer"] {{

background-color:#0a0e17 !important;


background-image:

linear-gradient(
rgba(10,14,23,.20),
rgba(10,14,23,.20)
),

url(
'data:image/webp;base64,{_bg_cache}'
);


background-size:92% auto !important;
background-position:center center !important;
background-repeat:no-repeat !important;
background-attachment:fixed !important;


}}



div.stMainBlockContainer {{

padding-top:20px !important;

}}



</style>
""",
    unsafe_allow_html=True
    )



    if os.path.exists("style.css"):

        with open(
            "style.css",
            "r",
            encoding="utf-8"
        ) as f:

            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )





# ==========================================
# 📋 بطاقة الإحداثيات الفنية
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
padding:8px 15px;
border-radius:10px;
border:1px solid #00bfff;
margin-bottom:10px;
">


<div style="
direction:rtl;
text-align:right;
font-size:16px;
line-height:1.7;
">


📏 <b>المقاس:</b> {size_grp}

<br>

📺 <b>نوع الشاشة:</b> {panel_grp}

<br>

👁️ <b>المستشعر التقارب:</b> {sensor_grp}


</div>


</div>
""",
    unsafe_allow_html=True
    )





# ==========================================
# 📱 بطاقات النتائج
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
<h4 style="
color:{color_hex};
direction:rtl;
text-align:right;
margin:8px 0;
">

{badge_icon} {title}

</h4>
""",
    unsafe_allow_html=True
    )



    for model in models_list:


        st.markdown(
        f"""
<div style="
background:rgba(10,14,23,.90);
border:1px solid {color_hex};
border-radius:10px;
padding:10px;
margin-bottom:8px;
display:flex;
direction:ltr;
justify-content:space-between;
align-items:center;
">


<div style="
font-size:18px;
font-weight:800;
color:white;
text-align:left;
">

{model}

</div>



<div style="
width:45px;
height:45px;
border-radius:8px;
border:1px dashed #00bfff;
">

</div>



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
<h3 style="
text-align:center;
color:#00bfff;
">
🛠️ لوحة التحكم
</h3>
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

                st.caption(
                    "لا توجد تنبيهات"
                )




        with st.expander(
            "⚙️ الإعدادات"
        ):


            st.checkbox(
                "تفعيل المراقب الصامت",
                value=True
            )




        with st.expander(
            "🛡️ المراقب الصامت",
            expanded=True
        ):


            st.metric(
                "📱 الهواتف",
                total_models
            )


            st.metric(
                "🧹 مراجعة",
                empty_groups_count
            )


            st.caption(
                "المراقب يعمل"
            )
