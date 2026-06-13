import streamlit as st
import datetime
import os
import base64

def inject_pwa_and_styles():
    """حقن ملف الـ Manifest ومعالجة خلفية شاشة الهاتف بأعلى دقة نفاذية لطبقات السيستم العميقة"""
    st.markdown("""
    <head>
        <link rel="manifest" href="./manifest.json">
    </head>
    """, unsafe_allow_html=True)

    bg_image_base64 = ""
    if os.path.exists("phone_image.webp"):
        with open("phone_image.webp", "rb") as f:
            bg_image_base64 = base64.b64encode(f.read()).decode()

    # 🌌 التحديث السحري: استهداف كامل طبقات الحاويات الافتراضية المعتمة وتصفيرها لتبرز الخلفية الزجاجية
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], 
    [data-testid="stAppViewMain"], 
    .stApp, 
    .stMain, 
    main, 
    [data-testid="stApp"],
    [data-testid="stHeader"],
    div.stMainBlockContainer,
    .stAppDeployButton,
    [data-testid="stBlock"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    .stApp {{
        background-image:
            linear-gradient(
                rgba(10,14,23,0.55),
                rgba(10,14,23,0.55)
            ),
            url('data:image/webp;base64,{bg_image_base64}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def draw_technical_coords(size_grp, panel_grp, sensor_grp):
    """[المرحلة ب]: إظهار الإحداثيات الفنية التتابعية"""
    st.markdown(f"""
        <div style='background: rgba(15, 23, 42, 0.7); padding: 20px; border-radius: 12px; border: 1px dashed #00bfff; margin-bottom: 25px;'>
            <h4 style='text-align:center; color:#00bfff; margin-top:0;'>📋 تحليل الإحداثيات الفنية للمجموعة التوافقية</h4>
            <div style='display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center;'>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>📏 مقاس الحماية</p><h5 style='color:#fff; margin-top:0;'>{size_grp}</h5></div>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>📺 بنية الشاشة</p><h5 style='color:#fff; margin-top:0;'>{panel_grp}</h5></div>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>👁️ مستشعر التقارب</p><h5 style='color:#fff; margin-top:0;'>{sensor_grp}</h5></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def draw_neon_section(title, models_list, color_hex, badge_icon, current_search):
    """[المرحلة ج]: توليد مجموعات التوافق ببطاقات نيونية فخمة جداً"""
    if not models_list:
        return
    st.markdown(f"<h4 style='text-align:right;color:{color_hex}; margin-top:20px; margin-bottom:10px;'>{badge_icon} {title} ({len(models_list)}):</h4>", unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, comp_model in enumerate(models_list):
        with cols[idx % 4]:
            if comp_model.lower().strip() == current_search.lower().strip():
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #0f172a, #1e293b); 
                                color: #00bfff; padding: 12px; border-radius: 8px; text-align: center; 
                                font-weight: bold; border: 2px solid #00bfff; 
                                box-shadow: 0px 0px 12px rgba(0, 191, 255, 0.5); margin-bottom: 12px;'>
                        ⭐ {comp_model}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e293b, #0f172a); 
                                color: #e2e8f0; padding: 12px; border-radius: 8px; text-align: center; 
                                border: 1px solid {color_hex}; margin-bottom: 12px;'>
                        🔹 {comp_model}
                    </div>
                """, unsafe_allow_html=True)
