import streamlit as st
import base64
import os
from app_init import initialize_system_data
from workflows import run_system_workflows
from ui_components import draw_control_panel

st.set_page_config(layout="wide", page_title="ZEGAAR AMMAR GLASS MANAGER", page_icon="🔍")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

st.markdown(f"""
<style>
.stApp {{
    background-image: url("{bg_img_base64}");
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-color: #0d1117;
}}
.main-header-container {{
    width: 100%; text-align: center; margin-top: -20px; margin-bottom: 25px; padding: 5px; background: rgba(13, 17, 23, 0.7); border-radius: 8px;
}}
.main-logo {{
    font-size: 32px; font-weight: 900; color: #00bfff; text-shadow: 0 0 15px rgba(0,191,255,0.8); line-height: 1.2;
}}
.main-subtitle {{
    font-size: 18px; font-weight: 600; color: #ffffff; opacity: 0.95; margin-top: 8px; text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
}}
.stTextInput>div>div>input {{
    background: rgba(255, 255, 255, 0.07) !important; color: white !important; border: 1px solid rgba(0, 191, 255, 0.3) !important;
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header-container">
    <div class="main-logo">ZEGAAR AMMAR<br>GLASS MANAGER</div>
    <div class="main-subtitle">النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>
</div>
""", unsafe_allow_html=True)

(db_data, unique_models, total_models, empty_groups_count, brand_counts, all_available_sizes, all_available_panels, all_available_sensors) = initialize_system_data()

def fast_phone_search(searchterm):
    if not searchterm: return []
    term = searchterm.lower().strip()
    starts_with = [m for m in unique_models if m.lower().startswith(term)]
    contains = [m for m in unique_models if term in m.lower() and m not in starts_with]
    return (starts_with + contains)[:10]

phone = st.text_input("البحث والمطابقة الفورية للموديلات:", placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة...", label_visibility="collapsed", key="free_smart_search_input").strip()

suggestions = fast_phone_search(phone) if phone else []

# ⚡ [التعديل الموحد]: استدعاء نظيف ومتطابق بالكامل مع دالة workflows.py الحالية
run_system_workflows(
    phone=phone,
    db_data=db_data,
    suggestions=suggestions
)

# دمج مركزي لوحة التحكم بأسفل التطبيق
draw_control_panel(
    notifications=st.session_state.get('notifications', []),
    total_models=total_models,
    empty_groups_count=empty_groups_count
)
