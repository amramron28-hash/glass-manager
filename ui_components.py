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
                    img = base64.b64encode(f.read()).decode()
                break
        _bg_cache = img

    st.markdown(
    f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{
    background-color:#0a0e17 !important;
    background-image: linear-gradient(rgba(10,14,23,.20), rgba(10,14,23,.20)), url('data:image/webp;base64,{_bg_cache}');
    background-size:92% auto !important;
    background-position:center center !important;
    background-repeat:no-repeat !important;
    background-attachment:fixed !important;
}}

div.stMainBlockContainer {{
    padding-top:20px !important;
}
</style>
""",
    unsafe_allow_html=True
    )

    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ==========================================
# 📋 بطاقة الإحداثيات الفنية
# ==========================================

def draw_technical_coords(size_grp, panel_grp, sensor_grp):
    st.markdown(
    f"""
<div style="
background: rgba(15, 23, 42, 0.4);
backdrop-filter: none;
-webkit-backdrop-filter: none;
padding: 12px 15px;
border-radius: 12px;
border: 1px solid rgba(0, 191, 255, 0.6);
margin-bottom: 12px;
box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
">

<div style="
direction: rtl;
text-align: right;
font-size: 16px;
line-height: 1.7;
color: #ffffff;
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
# 📱 بطاقات النتائج (تأثير الزجاج النقي الصافي)
# ==========================================

def draw_neon_section(title, models_list, color_hex, badge_icon, current_search):
    if not models_list:
        return

    st.markdown(
    f"""
<h4 style="
color: {color_hex};
direction: rtl;
text-align: right;
margin: 12px 0 8px 0;
font-weight: bold;
">
{badge_icon} {title}
</h4>
""",
    unsafe_allow_html=True
    )

    for model in models_list:
        # نقوم بتحويل اللون السداسي (Hex) إلى لون Rgb مع شفافية خفيفة ليعطي مظهر الزجاج الملون الصافي
        # مع إضافة إطار زجاجي رفيع ولطيف بنفس لون الفئة لحواف البطاقة العائمة
        st.markdown(
        f"""
<div style="
background: {color_hex}15;
border: 1.5px solid {color_hex}50;
border-radius: 12px;
padding: 14px 18px;
margin-bottom: 10px;
display: flex;
direction: ltr;
justify-content: space-between;
align-items: center;
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
">

<div style="
font-size: 19px;
font-weight: 900;
color: #ffffff;
text-align: left;
letter-spacing: 0.5px;
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

def draw_control_panel(notifications=None, total_models=0, empty_groups_count=0):
    notifications = notifications or []

    with st.sidebar:
        st.markdown(
        """
<h3 style="
text-align: center;
color: #00bfff;
font-weight: bold;
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
            st.checkbox("تفعيل المراقب الصامت", value=True)

        with st.expander("🛡️ المراقب الصامت", expanded=True):
            st.metric("📱 الهواتف", total_models)
            st.metric("🧹 مراجعة", empty_groups_count)
            st.caption("المراقب يعمل")
