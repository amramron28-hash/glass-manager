import streamlit as st
import os
import base64


# =========================
# 🟢 كاش بسيط لتسريع الخلفية
# =========================
_bg_cache = None


def inject_pwa_and_styles():
    """
    تحسين الأداء + نفس الشكل + تقليل إعادة المعالجة
    """

    global _bg_cache

    st.markdown("""
    <head>
        <link rel="manifest" href="./manifest.json">
    </head>
    """, unsafe_allow_html=True)

    # =========================
    # 🟢 تحميل الصورة مرة واحدة فقط
    # =========================
    if _bg_cache is None:

        paths_to_check = [
            "phone_image.webp",
            "./phone_image.webp",
            "app/phone_image.webp",
            "./app/phone_image.webp",
            "/app/phone_image.webp"
        ]

        bg_image_base64 = ""

        for path in paths_to_check:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    bg_image_base64 = base64.b64encode(f.read()).decode()
                break

        _bg_cache = bg_image_base64

    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(
                rgba(10,14,23,0.45),
                rgba(10,14,23,0.45)
            ),
            url('data:image/webp;base64,{_bg_cache}') !important;
        background-size: 100% 100% !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}

    .neon-card-text {{
        font-size: 28px !important;
        font-weight: 900 !important;
        line-height: 1.4 !important;
        color: #FFFFFF !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def draw_technical_coords(size_grp, panel_grp, sensor_grp):

    st.markdown(f"""
        <div style='background: rgba(15, 23, 42, 0.85); padding: 25px; border-radius: 12px; border: 2px dashed #00bfff; margin-bottom: 25px;'>
            <h3 style='text-align:center; color:#00bfff; font-size: 30px; font-weight: bold;'>
            📋 تحليل الإحداثيات الفنية
            </h3>

            <div style='display:flex; justify-content:space-around; flex-wrap:wrap; text-align:center; margin-top:15px;'>
                <div><p style='color:#a0aec0;'>📏 المقاس</p><h4>{size_grp}</h4></div>
                <div><p style='color:#a0aec0;'>📺 الشاشة</p><h4>{panel_grp}</h4></div>
                <div><p style='color:#a0aec0;'>👁️ الحساس</p><h4>{sensor_grp}</h4></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def draw_neon_section(title, models_list, color_hex, badge_icon, current_search):

    if not models_list:
        return

    st.markdown(
        f"<h3 style='color:{color_hex}; font-size:30px;'>{badge_icon} {title} ({len(models_list)})</h3>",
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    for idx, model in enumerate(models_list):
        with cols[idx % 4]:

            is_current = model.strip().lower() == current_search.strip().lower()

            st.markdown(f"""
                <div class='neon-card-text' style='
                    background:{color_hex};
                    padding:22px;
                    border-radius:10px;
                    text-align:center;
                    border:{'3px solid #fff' if is_current else '1px solid rgba(255,255,255,0.3)'};
                    box-shadow:0 0 18px {color_hex};
                '>
                    {'⭐' if is_current else '🔹'} {model}
                </div>
            """, unsafe_allow_html=True)
