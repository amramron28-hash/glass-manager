import streamlit as st

def inject_slate_navy_css():
    """حقن الـ CSS التبايني الصارم لتكبير الهيدر وترشيق البطاقات العريضة بالكامل"""
    st.markdown("""
        <style>
            .stApp { background-color: #0d1117 !important; color: #c9d1d9 !important; }
            
            /* الهيدر الأزرق السماوي الفخم والكبير */
            .sky-header {
                text-align: center;
                color: #00bfff !important;
                font-size: 28px !important;
                font-weight: 900 !important;
                font-family: 'Impact', 'Segoe UI', sans-serif;
                margin-bottom: 25px !important;
                text-shadow: 0px 0px 8px rgba(0, 191, 255, 0.4);
            }
            
            .group-header {
                font-size: 16px;
                font-weight: bold;
                margin-top: 15px;
                margin-bottom: 8px;
                color: #f0f6fc;
            }
            
            /* بطاقات عريضة مرشقة (Full Width) مريحة جداً للمس على الهاتف */
            .full-width-card {
                display: block;
                width: 100%;
                text-align: center;
                padding: 12px 5px;
                margin-bottom: 8px;
                border-radius: 8px;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
                background-color: #161b22;
            }
            
            .exact-card { border: 1.5px solid #238636 !important; color: #58a6ff !important; }
            .plus-card { border: 1.5px solid #1f6feb !important; color: #58a6ff !important; }
            .minus-card { border: 1.5px solid #d29922 !important; color: #f08c2d !important; }
            .warning-card { border: 1.5px solid #f85149 !important; color: #ff7b72 !important; background-color: #2d1919; }
            
            .suggestion-box {
                background-color: #161b22;
                border: 1.5px solid #30363d;
                border-radius: 6px;
                padding: 8px;
                margin-top: -10px;
                margin-bottom: 15px;
            }
            
            [data-testid="stSidebar"] { background-color: #0b0e14 !important; border-right: 1.5px solid #21262d !important; }
        </style>
    """, unsafe_allow_html=True)

def render_app_header():
    """عرض الهيدر السماوي العريض المطور"""
    st.markdown("<div class='sky-header'>ZEGAAR AMMAR<br>GLASS MANAGER</div>", unsafe_allow_html=True)

def render_sidebar(db_data, save_db, total_models, fix_callback=None):
    """رندرة السايدبار مع جرس الإشعارات الحية والمراقب الصامت"""
    with st.sidebar:
        st.markdown("### 🔔 جرس الإشعارات الحية")
        notifications = db_data.get("notifications", [])
        if notifications:
            for note in reversed(notifications[-5:]):
                st.caption(f"⏱️ {note}")
            if st.button("🗑️ مسح الإشعارات"):
                db_data["notifications"] = []
                save_db(db_data)
                st.rerun()
        else:
            st.info("لا توجد إشعارات جديدة.")
            
        st.markdown("---")
        st.markdown("### ⚙️ المراقب الذكي ومصحح الأخطاء")
        st.metric(label="💾 إجمالي الهواتف الحية", value=total_models)
        
        if st.button("🔧 تشغيل فحص وتصحيح المجموعات"):
            if fix_callback:
                fix_callback()

def display_full_width_cards(results):
    """عرض المجموعات ببطاقات عريضة مع عزل تام للتحذيرات لحماية الألوان من الاختلاط"""
    exact_clean = [m for m in results['exact'] if m not in results['warn']]
    if exact_clean:
        st.markdown("<div class='group-header'>🟢 نفس المقاس والخصائص تماماً (Exact):</div>", unsafe_allow_html=True)
        for model in exact_clean:
            st.markdown(f"<div class='full-width-card exact-card'>{model}</div>", unsafe_allow_html=True)
            
    plus_clean = [m for m in results['plus'] if m not in results['warn']]
    if plus_clean:
        st.markdown("<div class='group-header'>🔵 مقاس أكبر بقليل (Plus):</div>", unsafe_allow_html=True)
        for model in plus_clean:
            st.markdown(f"<div class='full-width-card plus-card'>{model}</div>", unsafe_allow_html=True)
            
    minus_clean = [m for m in results['minus'] if m not in results['warn']]
    if minus_clean:
        st.markdown("<div class='group-header'>🟤 مقاس أصغر بقليل (Minus):</div>", unsafe_allow_html=True)
        for model in minus_clean:
            st.markdown(f"<div class='full-width-card minus-card'>{model}</div>", unsafe_allow_html=True)
            
    if results['warn']:
        st.markdown("<div class='group-header'>⚠️ تنبيه: هواتف بنفس المقاس ولكن بحساس مختلف:</div>", unsafe_allow_html=True)
        for model in results['warn']:
            st.markdown(f"<div class='full-width-card warning-card'>{model}</div>", unsafe_allow_html=True)
