import streamlit as st
import datetime
import os
import base64

def inject_pwa_and_styles():
    """
    حقن ملف الـ Manifest ومعالجة خلفية شاشة الهاتف بالتشفير النصي الفوري Base64 
    الأصلي الممتد بكامل تفاصيل الزجاج المتوهج ودقة نفاذ 100%.
    """
    st.markdown("""
    <head>
        <link rel="manifest" href="./manifest.json">
    </head>
    """, unsafe_allow_html=True)

    # قراءة الصورة محلياً وتحويلها لنص بايتات لفرضها داخل الحاويات العميقة للـ iframe
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

    # استعادة التصميم الأصلي الفخم الممتد والمثبت بكامل أبعاد الشاشة وبأعلى نفاذ زجاجي
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
        background-size: cover !important; /* استعادة الامتداد الكامل والأصلي للصورة */
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def draw_technical_coords(size_grp, panel_grp, sensor_grp):
    """[المرحلة ب]: إظهار الإحداثيات الفنية للمجموعة المكتشفة بالعربية أقصى اليمين"""
    st.markdown(f"""
        <div style='background: rgba(15, 23, 42, 0.7); padding: 20px; border-radius: 12px; border: 1px dashed #00bfff; margin-bottom: 25px;'>
            <h4 style='text-align:center; color:#00bfff; margin-top:0;'>📋 تحليل الإحداثيات الفنية للمجموعة التوافقية</h4>
            <div style='display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; direction: rtl;'>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>📏 مقاس الحماية</p><h5 style='color:#fff; margin-top:0;'>{size_grp}</h5></div>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>📺 بنية الشاشة</p><h5 style='color:#fff; margin-top:0;'>{panel_grp}</h5></div>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>👁️ مستشعر التقارب</p><h5 style='color:#fff; margin-top:0;'>{sensor_grp}</h5></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def draw_neon_section(title, models_list, color_hex, badge_icon, current_search):
    """[المرحلة ج]: توليد مجموعات التوافق ثنائية اللغة الفاخرة وجلب صور الهواتف آلياً بدون أخطاء روابط وبـ 0 ثانية تأخير"""
    if not models_list:
        return
    # العربية أقصى اليمين للعناوين الفئوية
    st.markdown(f"<h4 class='section-title' style='color:{color_hex};'>{badge_icon} {title} ({len(models_list)}):</h4>", unsafe_allow_html=True)
    
    for comp_model in models_list:
        model_name_clean = comp_model.strip()
        
        # 🛡️ مصفي الأكواد الذكي: إذا احتوى الاسم على كود قديم بالخطأ من الـ JSON، يتم استئصاله وتنظيف اسم الهاتف فوراً
        if "<div" in model_name_clean:
            # عزل اسم الهاتف الصافي فقط قبل بداية الكود المكتوب بالخطأ
            model_name_clean = model_name_clean.split("<div")[0].strip()
            if not model_name_clean:
                model_name_clean = "Unknown Phone"
                
        is_current = model_name_clean.lower() == current_search.lower().strip()
        card_class = "flat-warning-card" if color_hex == "#ef4444" else "ammar-flat-card"
        specific_style = f"border: 2px solid #00bfff; box-shadow: 0px 0px 12px rgba(0, 191, 255, 0.5);" if is_current else f"border: 1px solid {color_hex};"
        bg_style = "background: linear-gradient(135deg, #0f172a, #1e293b);" if is_current else ""
        
        # 🎯 محرك الاستدعاء التلقائي الفوري لصور الهواتف المباشرة
        clean_name_url = model_name_clean.replace(" ", "-").lower()
        auto_phone_image_url = f"https://phonearena.com{clean_name_url}.jpg"
        
        # هندسة بناء الكرت المفرغ: حجز مساحة الصورة في جهة اليمين والاسم بالإنجليزية ملتصق باليسار كلياً
        st.markdown(f"""
            <div class="{card_class}" style="{bg_style} {specific_style}">
                <!-- الإنجليزية أقصى اليسار لاسم الهاتف النظيف المصفى -->
                <span class="flat-phone-text">{'⭐ ' if is_current else ''}{model_name_clean}</span>
                
                <!-- 🖼️ نزول صورة الهاتف المجلوبة تلقائياً وبشكل مصحح ومحمي أقصى اليمين في المربع النيوني المحجوز مسبقاً -->
                <div class="image-placeholder-box" style="overflow: hidden; width: 55px; height: 55px;">
                    <img src="{auto_phone_image_url}" 
                         onerror="this.onerror=null; this.src='https://icons8.com'; this.style.opacity='0.4';" 
                         style="width: 100%; height: 100%; object-fit: contain;">
                </div>
            </div>
        """, unsafe_allow_html=True)
