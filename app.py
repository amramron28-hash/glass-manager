import streamlit as st
from app_init import initialize_system_data
from workflows import run_system_workflows

# 🖥️ إعدادات الصفحة العامة للنظام الموحد
st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# 🎨 [الحل الجذري]: تحويل الصورة إلى خلفية ثابتة 100% لا تتحرك ولا تنزل لأسفل
st.markdown(
    """
    <style>
    /* حقن الصورة كخلفية ثابتة ممتدة على كامل الشاشة خلف العناصر */
    .stApp {
        background-image: url("app/static/phone_image.webp");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed; /* هذا السطر يضمن ثبات الصورة تماماً أثناء التمرير */
        background-color: #0d1117; /* لون احتياطي في حال تأخر تحميل الصورة */
    }
    
    /* تصميم حاوية الشعار العلوي */
    .main-header-container {
        width: 100%;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 25px;
        padding: 5px;
        background: rgba(13, 17, 23, 0.6); /* خلفية ضبابية خفيفة للشعار لزيادة الوضوح */
        border-radius: 8px;
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
    
    /* جعل خانات المدخلات والبطاقات تطفو بشكل شفاف وجميل فوق الخلفية الثابتة */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.07) !important;
        color: white !important;
        border: 1px solid rgba(0, 191, 255, 0.3) !important;
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

# 📥 خانة البحث الحر الفوري في الأعلى (تطفو الآن بشكل زجاجي فوق الواجهة الثابتة)
phone = st.text_input(
    "البحث والمطابقة الفورية للموديلات:",
    placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة...",
    label_visibility="collapsed",
    key="free_smart_search_input"
).strip()

# جلب الاقتراحات المساعدة لحظياً أثناء الكتابة
suggestions = fast_phone_search(phone) if phone else []

# 🔗 الالتحام البرمجي الكامل وتمرير البيانات لملف العمليات (تظهر خططه والبطاقات فوق الخلفية بثبات)
run_system_workflows(
    phone=phone,
    db_data=db_data,
    suggestions=suggestions,
    total_models=total_models,
    empty_groups_count=empty_groups_count
)
