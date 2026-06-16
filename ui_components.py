import streamlit as st
import os
import base64


_bg_cache = None



# ==========================================
# 🎨 التصميم والخلفية
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

font-size:22px;
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
background:rgba(15,23,42,.90);
padding:20px;
border-radius:14px;
border:2px solid #00bfff;
margin-top:15px;
">


<h3 style="
text-align:right;
direction:rtl;
color:#00bfff;
margin-bottom:20px;
">

📋 تحليل الإحداثيات الفنية

</h3>



<div style="
direction:rtl;
text-align:right;
font-size:22px;
line-height:2;
">



<div>
📏 <b>المقاس</b>
<br>
{size_grp}
</div>


<hr>


<div>
📺 <b>نوع الشاشة</b>
<br>
{panel_grp}
</div>


<hr>


<div>
👁️ <b>المستشعر التقارب</b>
<br>
{sensor_grp}
</div>



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

<h3 style="
color:{color_hex};
text-align:right;
direction:rtl;
">

{badge_icon} {title}

</h3>

""",

    unsafe_allow_html=True

    )




    for model in models_list:


        st.markdown(

        f"""

<div style="

background:rgba(10,14,23,.85);

border:1px solid {color_hex};

border-radius:12px;

padding:15px;

margin-bottom:8px;

display:flex;

justify-content:space-between;

align-items:center;

direction:ltr;

box-shadow:0 0 12px {color_hex};

">



<div style="
text-align:left;
font-size:22px;
font-weight:900;
color:white;
">

🔹 {model}

</div>




<div style="
width:65px;
height:65px;
border:1px dashed rgba(0,191,255,.5);
border-radius:10px;
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
                "تفعيل المراقب الذكي",
                True
            )




        with st.expander(
            "🛡️ حالة المراقب",
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
                "المراقب جاهز"
            )
