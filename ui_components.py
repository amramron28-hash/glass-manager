import streamlit as st
import datetime
import os
import base64
from database import load_db, save_db
from logic_engine import run_intelligent_inspector

def inject_pwa_and_styles():
    """
    حقن ملف الـ Manifest لمعايير الـ PWA ومعالجة خلفية شاشة الهاتف الديناميكية
    """
    st.markdown("""
    <head>
        <link rel="manifest" href="./manifest.json">
    </head>
    """, unsafe_allow_html=True)

    bg_image_base64 = ""
    if os.path.exists("phone_image.webp"):
        with open("phone_image.webp", "rb") as f:
            bg_image_base64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewMain"],
    .stApp,
    .stMain,
    main,
    [data-testid="stApp"] {{
        background-image:
            linear-gradient(
                rgba(10,14,23,0.45),
                rgba(10,14,23,0.45)
            ),
            url('data:image/webp;base64,{bg_image_base64}') !important;

        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        background-color: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_top_bar(db_data, total_models):
    """
    🎯 بناء شريط الأدوات العلوي الفاخر والمدمج:
    يحتوي على جرس الإشعارات، ترس الإعدادات، والمراقب الصامت.
    تم تحسينه ليعتمد على بيانات الـ RAM الجاهزة لضمان سرعة التصفح.
    """
    col_spacer, col_tools = st.columns([6, 2])
    
    with col_tools:
        sub_col1, sub_col2 = st.columns(2)
        
        with sub_col1:
            # 🔔 نافذة منبثقة زجاجية لجرس الإشعارات
            with st.popover("🔔 الإشعارات"):
                st.markdown("### 📌 آخر تحديثات نظام الفحص")
                st.info("💡 النظام يعمل بكفاءة قصوى والبحث الذكي اللحظي نشط الآن 100%.")
                
                if st.button("🧹 تشغيل الصيانة الفورية (المراقب الصامت)", key="btn_run_inspector_top"):
                    cleaned_data, changes = run_intelligent_inspector(db_data)
                    if changes:
                        save_db(cleaned_data)
                        st.success("✨ تم تطهير شجرة البيانات وترتيب الموديلات سحابياً بنجاح!")
                        st.rerun()
                    else:
                        st.toast("🎯 قاعدة البيانات نظيفة ومطهرة كلياً، لا توجد تكرارات.")
                        
        with sub_col2:
            # ⚙️ نافذة منبثقة لترس الإعدادات والإحصائيات الحية
            with st.popover("⚙️ الإعدادات"):
                st.markdown("### 🛠️ لوحة تحكم السيستم")
                st.write(f"📅 تاريخ اليوم الفني: **{datetime.date.today().strftime('%Y-%m-%d')}**")
                st.write("📊 حالة الذاكرة السحابية: **نشطة ومستقرة 🟢**")
                st.markdown("---")
                st.metric(label="📈 إجمالي الهواتف المراقبة بالنظام", value=total_models)

def draw_technical_coords(size_grp, panel_grp, sensor_grp):
    """
    📋 [المرحلة ب]: رسم وإظهار بطاقة تحليل الأبعاد الفنية التتابعية لهاتف الزبون
    """
    st.markdown(f"""
        <div style='background: rgba(15, 23, 42, 0.6); padding: 20px; border-radius: 12px; border: 1px dashed #00bfff; margin-bottom: 25px;'>
            <h4 style='text-align:center; color:#00bfff; margin-top:0;'>📋 تحليل الإحداثيات الفنية للمجموعة التوافقية</h4>
            <div style='display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center;'>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>📏 مقاس الحماية</p><h5 style='color:#fff; margin-top:0;'>{size_grp}</h5></div>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>📺 بنية الشاشة</p><h5 style='color:#fff; margin-top:0;'>{panel_grp}</h5></div>
                <div><p style='color:#a0aec0; margin-bottom:5px;'>👁️ مستشعر التقارب</p><h5 style='color:#fff; margin-top:0;'>{sensor_grp}</h5></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def draw_neon_section(title, models_list, color_hex, badge_icon, current_search):
    """
    📱 [المرحلة ج]: توليد مجموعات التوافق ببطاقات نيونية فاخرة مقسمة حسب دالة التوجيه الصارم
    """
    if not models_list:
        return
    st.markdown(f"<h4 style='text-align:right;color:{color_hex}; margin-top:20px; margin-bottom:10px;'>{badge_icon} {title} ({len(models_list)}):</h4>", unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, comp_model in enumerate(models_list):
        with cols[idx % 4]:
            # تنظيف ومطابقة الهاتف المختار حالياً لتمييزه بنيون سيان متوهج
            if comp_model.lower().strip() == current_search.lower().strip():
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #0f172a, #1e293b); 
                                color: #00bfff; 
                                padding: 12px; 
                                border-radius: 8px; 
                                text-align: center; 
                                font-weight: bold; 
                                border: 2px solid #00bfff; 
                                box-shadow: 0px 0px 12px rgba(0, 191, 255, 0.5); 
                                margin-bottom: 12px;'>
                        ⭐ {comp_model}
                    </div>
                """, unsafe_allow_html=True)
            else:
                # بقية الهواتف البديلة بحدود نيون متناسبة مع نوع التوافق (Exact, Plus, Minus, Warn)
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e293b, #0f172a); 
                                color: #e2e8f0; 
                                padding: 12px; 
                                border-radius: 8px; 
                                text-align: center; 
                                border: 1px solid {color_hex}; 
                                margin-bottom: 12px;'>
                        🔹 {comp_model}
                    </div>
                """, unsafe_allow_html=True)
