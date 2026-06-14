import streamlit as st
import datetime
import os
import base64

def inject_pwa_and_styles():
    """
    حقن ملف الـ Manifest ومعالجة خلفية شاشة الهاتف بالتشفير النصي الفوري Base64 
    مع تفعيل المرونة الكاملة والتجاوب التلقائي (Responsive) مع جميع أحجام الشاشات.
    """
    st.markdown("""
    <head>
        <link rel="manifest" href="./manifest.json">
    </head>
    """, unsafe_allow_html=True)

    bg_image_base64 = ""
    paths_to_check = [
        "phone_image.webp", 
        "./phone_image.webp", 
        "app/phone_image.webp", 
        "./app/phone_image.webp", 
        "/app/phone_image.webp"
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            with open(path, "rb") as f:
                bg_image_base64 = base64.b64encode(f.read()).decode()
            break

    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewMain"], .stApp, .stMain, main, [data-testid="stApp"], [data-testid="stHeader"], div.stMainBlockContainer, .stAppDeployButton, [data-testid="stBlock"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(
                rgba(10,14,23,0.45),
                rgba(10,14,23,0.45)
            ),
            url('data:image/webp;base64,{bg_image_base64}') !important;
        background-size: 100% 100% !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}

    /* 📈 تكبير خطوط بطاقات النتائج النيونية بشكل ضخم وواضح داخل السيستم */
    .neon-card-text {{
        font-size: 26px !important;
        font-weight: bold !important;
        line-height: 1.4 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def draw_technical_coords(size_grp, panel_grp, sensor_grp):
    """إظهار كرت الأبعاد الفنية التوافقية لهاتف الزبون في المنتصف بخطوط كبيرة وواضحة"""
    st.markdown(f"""
        <div style='background: rgba(15, 23, 42, 0.85); padding: 25px; border-radius: 12px; border: 2px dashed #00bfff; margin-bottom: 25px;'>
            <h3 style='text-align:center; color:#00bfff; margin-top:0; font-size: 28px; font-weight: bold;'>📋 تحليل الإحداثيات الفنية للمجموعة التوافقية</h3>
            <div style='display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; margin-top: 15px;'>
                <div><p style='color:#a0aec0; margin-bottom:5px; font-size: 20px;'>📏 مقاس الحماية</p><h4 style='color:#fff; margin-top:0; font-size: 25px; font-weight: bold;'>{size_grp}</h4></div>
                <div><p style='color:#a0aec0; margin-bottom:5px; font-size: 20px;'>📺 بنية الشاشة</p><h4 style='color:#fff; margin-top:0; font-size: 25px; font-weight: bold;'>{panel_grp}</h4></div>
                <div><p style='color:#a0aec0; margin-bottom:5px; font-size: 20px;'>👁️ مستشعر التقارب</p><h4 style='color:#fff; margin-top:0; font-size: 25px; font-weight: bold;'>{sensor_grp}</h4></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def draw_neon_section(title, models_list, color_hex, badge_icon, current_search):
    """توليد نتائج التوافق بالبطاقات الملونة النيونية العريضة مع خطوط مكبرة جداً لقراءة أسهل"""
    if not models_list:
        return
    st.markdown(f"<h3 style='text-align:right; color:{color_hex}; margin-top:25px; margin-bottom:15px; font-size: 28px; font-weight: bold;'>{badge_icon} {title} ({len(models_list)}):</h3>", unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, comp_model in enumerate(models_list):
        with cols[idx % 4]:
            if comp_model.lower().strip() == current_search.lower().strip():
                st.markdown(f"""
                    <div class='neon-card-text' style='background: linear-gradient(135deg, #0f172a, #1e293b); 
                                color: #00bfff; padding: 20px; border-radius: 8px; text-align: center; 
                                border: 2.5px solid #00bfff; 
                                box-shadow: 0px 0px 15px rgba(0, 191, 255, 0.6); margin-bottom: 12px;'>
                        ⭐ {comp_model}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='neon-card-text' style='background: linear-gradient(135deg, #1e293b, #0f172a); 
                                color: #e2e8f0; padding: 20px; border-radius: 8px; text-align: center; 
                                border: 1.5px solid {color_hex}; margin-bottom: 12px;'>
                        🔹 {comp_model}
                    </div>
                """, unsafe_allow_html=True)
