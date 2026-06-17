import streamlit as st
import os
import base64

st.set_page_config(
    page_title="مراقب الهواتف الذكية",
    page_icon="📱",
    layout="centered"
)

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
rgba(10,14,23,.40),
rgba(10,14,23,.40)
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


[data-testid="stSidebar"] {{

direction:rtl;

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
# 📋 بطاقة الإحداثيات
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
padding:12px 15px;
border-radius:10px;
border:1px solid #00bfff;
margin-bottom:15px;
">

<div style="
direction:rtl;
text-align:right;
font-size:16px;
line-height:1.8;
color:#e2e8f0;
">

📏 <b>المقاس:</b> {size_grp}

<br>

📺 <b>نوع الشاشة:</b> {panel_grp}

<br>

👁️ <b>مستشعر التقارب:</b> {sensor_grp}

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


    filtered_models = [
        m for m in models_list
        if current_search.lower() in m.lower()
    ] if current_search else models_list


    if not filtered_models:
        return



    st.markdown(
    f"""
<h4 style="
color:{color_hex};
direction:rtl;
text-align:right;
margin:15px 0 8px 0;
">

{badge_icon} {title}

</h4>
""",
    unsafe_allow_html=True
    )



    for model in filtered_models:


        st.markdown(
        f"""
<div style="

background:linear-gradient(
135deg,
{color_hex}55,
{color_hex}20
);

border:1.5px solid {color_hex};

border-radius:18px;

padding:14px 18px;

margin-bottom:10px;

display:flex;

align-items:center;


box-shadow:

0 8px 24px rgba(0,0,0,.30),

0 0 14px {color_hex}55;


backdrop-filter:saturate(180%);

-webkit-backdrop-filter:saturate(180%);

">


<div style="

font-size:19px;

font-weight:900;

color:white;

width:100%;

text-align:left;


text-shadow:

0 1px 2px rgba(0,0,0,.35);

">

{model}

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


        with st.expander("🔔 الإشعارات"):

            if notifications:

                for n in notifications:
                    st.warning(n)

            else:
                st.caption("لا توجد تنبيهات")



        with st.expander("⚙️ الإعدادات"):

            silent_mode = st.checkbox(
                "تفعيل المراقب الصامت",
                value=True
            )



        with st.expander(
            "🛡️ المراقب الصامت",
            expanded=True
        ):

            st.metric(
                "📱 الهواتف المفحوصة",
                total_models
            )

            st.metric(
                "🧹 مجموعات للمراجعة",
                empty_groups_count
            )


            if silent_mode:

                st.caption(
                    "🟢 المراقب النشط يعمل في الخلفية"
                )

            else:

                st.caption(
                    "🔴 المراقب متوقف حالياً"
                )





# ==========================================
# 🚀 تشغيل التطبيق
# ==========================================

inject_pwa_and_styles()


dummy_notifications = [
    "تحديث أمان معلق لـ Galaxy S26",
    "فشل فحص مستشعر iPhone 17"
]


premium_phones = [
    "iPhone 17 Pro Max",
    "Samsung Galaxy S26 Ultra",
    "Google Pixel 11 Pro"
]


midrange_phones = [
    "Xiaomi Redmi Note 15",
    "Samsung Galaxy A57",
    "Nothing Phone (3)"
]


draw_control_panel(
    notifications=dummy_notifications,
    total_models=len(premium_phones)+len(midrange_phones),
    empty_groups_count=1
)


st.markdown(
'<h2 style="text-align:center;color:white;direction:rtl;">📱 نظام الفحص الفني للهواتف</h2>',
unsafe_allow_html=True
)


search_query = st.text_input(
    "",
    placeholder="🔍 ابحث عن موديل محدد هنا...",
    label_visibility="collapsed"
)


st.markdown(
'<p style="color:#00bfff;text-align:right;direction:rtl;">📊 المواصفات المستهدفة بالفحص:</p>',
unsafe_allow_html=True
)


draw_technical_coords(
    "6.7 - 6.9 إنش",
    "Dynamic AMOLED 2X / Super Retina XDR",
    "حقيقي (Hardware Sensor)"
)


draw_neon_section(
    "الفئة الرائدة (Premium)",
    premium_phones,
    "#00bfff",
    "💎",
    search_query
)


draw_neon_section(
    "الفئة المتوسطة (Mid-Range)",
    midrange_phones,
    "#ff007f",
    "⚡",
    search_query
                )
