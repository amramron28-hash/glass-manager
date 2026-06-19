import streamlit as st
import os
from app_init import initialize_system_data
from workflows import run_system_workflows

# 🖥️ إعدادات الصفحة العامة للنظام الموحد
st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# 🎨 تصميم الواجهة وتصحيح تموضع الشعار وتثبيت واجهة الزجاج والخلفية
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0d1117;
    }
    .main-header-container {
        width: 100%;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 20px;
        padding: 5px;
    }
    .main-logo {
        font-size: 32px; 
        font-weight: 900; 
        color: #00bfff; 
        text-shadow: 0 0 15px rgba(0,191,255,0.8);
        line-height: 1.2;
    }
    .main-subtitle {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        opacity: 0.95;
        margin-top: 8px;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
    }
    .glass-card {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    </style>
    
    <div class="main-header-container">
        <div class="main-logo">ZEGAAR AMMAR<br>GLASS MANAGER</div>
        <div class="main-subtitle">النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ⚡ استدعاء دالة التهيئة لتفكيك قاعدة البيانات وجلب القوائم الحية ديناميكياً
(
    db_data, 
    unique_models, 
    total_models, 
    empty_groups_count, 
    brand_counts, 
    all_available_sizes, 
    all_available_panels, 
    all_available_sensors
) = initialize_system_data()

# 🔍 محرك جلب الاقتراحات اللحظية الفلاشية من ملف الأسماء
def fast_phone_search(searchterm):
    if not searchterm:
        return []
    term = searchterm.lower().strip()
    starts_with = [m for m in unique_models if m.lower().startswith(term)]
    contains = [m for m in unique_models if term in m.lower() and m not in starts_with]
    return (starts_with + contains)[:10]

# 📥 خانة البحث الحر الفوري المدمج (تظهر الآن مباشرة في الأعلى تحت العنوان)
phone = st.text_input(
    "البحث والمطابقة الفورية للموديلات:",
    placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة...",
    label_visibility="collapsed",
    key="free_smart_search_input"
).strip()

# جلب الاقتراحات المساعدة لحظياً أثناء الكتابة
suggestions = fast_phone_search(phone) if phone else []

# 🔗 الالتحام البرمجي الكامل: تمرير النص والبيانات لملف العمليات المحدث لتشغيل الخطط
run_system_workflows(
    phone=phone,
    db_data=db_data,
    suggestions=suggestions,
    total_models=total_models,
    empty_groups_count=empty_groups_count
)

# 📸 [تصحيح الترتيب]: إنزال الصورة الخلفية لتظهر دائماً بالأسفل تحت خانة البحث أو تحت نتائج النيون
image_path = "phone_image.webp"
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)
