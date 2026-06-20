import streamlit as st
import base64
import os
from app_init import initialize_system_data
from workflows import run_system_workflows
from ui_components import draw_control_panel, inject_pwa_and_styles

# 🖥️ إعدادات الصفحة العامة للنظام الموحد
st.set_page_config(
    layout="wide", 
    page_title="ZEGAAR AMMAR GLASS MANAGER", 
    page_icon="🔍"
)

# حقن أنماط الـ PWA والملفات الأساسية
inject_pwa_and_styles()

def get_base64_image(image_path):
    """تحويل الصورة برمجياً لترميز آمن ومضمون للتثبيت كخلفية ويب حقيقية"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# 🎨 حقن الخلفية الثابتة مع ستايل أزرار الستارة التفاعلية العائمة فوق الواجهة
st.markdown(
    f"""
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
        width: 100%;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 25px;
        padding: 5px;
        background: rgba(13, 17, 23, 0.7);
        border-radius: 8px;
    }}
    .main-logo {{
        font-size: 32px; 
        font-weight: 900; 
        color: #00bfff; 
        text-shadow: 0 0 15px rgba(0,191,255,0.8);
        line-height: 1.2;
    }}
    .main-subtitle {{
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        opacity: 0.95;
        margin-top: 8px;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
    }}
    .stTextInput>div>div>input {{
        background: rgba(255, 255, 255, 0.07) !important;
        color: white !important;
        border: 1px solid rgba(0, 191, 255, 0.3) !important;
    }}
    /* تصميم الصندوق العائم للاقتراحات المساعدة */
    .floating-suggestions-box-title {{
        padding: 10px 15px 5px 15px; 
        background: rgba(13, 17, 23, 0.95) !important; 
        border-top: 1px solid #00bfff !important;
        border-left: 1px solid #00bfff !important;
        border-right: 1px solid #00bfff !important;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-top: 5px;
        box-shadow: 0 -5px 15px rgba(0,191,255,0.2);
        position: relative !important;
        z-index: 999999 !important;
    }}
    .floating-suggestions-box-end {{
        background: rgba(13, 17, 23, 0.95) !important; 
        border-bottom: 1px solid #00bfff !important;
        border-left: 1px solid #00bfff !important;
        border-right: 1px solid #00bfff !important;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
        margin-bottom: 15px;
        padding-bottom: 5px;
        box-shadow: 0 10px 15px rgba(0,191,255,0.2);
        position: relative !important;
        z-index: 999999 !important;
    }}
    .neon-section {{
        margin-top: 25px !important;
        margin-bottom: 25px !important;
        padding: 20px !important;
        border-radius: 12px !important;
        display: block !important;
    }}
    .neon-icon {{
        font-size: 26px !important;
        margin-left: 12px !important;
        display: inline-block !important;
    }}
    /* تحسين أزرار الاقتراحات الحية لتطفو وتتفاعل مع اللمس بصرياً */
    div.stButton > button.suggestion-live-btn {{
        background-color: transparent !important;
        color: #ffffff !important;
        border: none !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 0px !important;
        width: 100% !important;
        text-align: right !important;
        padding: 6px 15px !important;
        font-size: 16px !important;
        transition: all 0.2s ease !important;
    }}
    div.stButton > button.suggestion-live-btn:hover {{
        background-color: rgba(0, 191, 255, 0.15) !important;
        color: #00bfff !important;
        padding-right: 25px !important;
    }}
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

# 🔗 قفل قراءة الـ Auto-complete المباشرة الصارمة من ملف الأسماء النصي المحكم الخاص بك
INDEX_FILE = "models_index.txt"
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        unique_models = sorted(list(set([line.strip() for line in f if line.strip()])))

# 🔍 محرك جلب الاقتراحات اللحظية الفلاشية من ملف الأسماء
def fast_phone_search(searchterm):
    if not searchterm:
        return []
    term = searchterm.lower().strip()
    starts_with = [m for m in unique_models if m.lower().startswith(term)]
    contains = [m for m in unique_models if term in m.lower() and m not in starts_with]
    return (starts_with + contains)[:10]

# إدارة جلسة حقل الإدخال لتمكين الأزرار من ملء صندوق البحث فورياً
if "search_field_val" not in st.session_state:
    st.session_state.search_field_val = ""

# خانة البحث الحر الفوري المدمج المرتبطة بذاكرة الجلسة التفاعلية
phone_input = st.text_input(
    "البحث والمطابقة الفورية للموديلات:",
    value=st.session_state.search_field_val,
    placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة...",
    label_visibility="collapsed",
    key="free_smart_search_input_field"
).strip()

# تحديث المتغير الأساسي
phone = phone_input

# جلب الاقتراحات المساعدة لحظياً أثناء الكتابة من مصفوفة الملف
suggestions = fast_phone_search(phone) if phone else []

# ⚡ [إعادة إحياء الستارة التفاعلية]: تحويل الأسطر الميتة إلى أزرار حية تتقلص مع الحروف وتملأ الحقل باللمس
if phone and suggestions:
    is_fully_matched = any(phone.lower() == s.lower() for s in suggestions)
    if not is_fully_matched:
        st.markdown(
            """
            <div class='floating-suggestions-box-title'>
                <span style='color:#00bfff; font-weight:bold; font-size:16px;'>💡 اقتراحات البحث المساعدة لتسريع الكتابة:</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        # فتح حاوية الأزرار الحية
        with st.container():
            st.markdown("<div class='floating-suggestions-box-end'>", unsafe_allow_html=True)
            for idx, item in enumerate(suggestions):
                # زر تفاعلي حقيقي مفرود يملأ الحقل فور اللمس وينعش الواجهة
                if st.button(f"🔍 {item}", key=f"sug_btn_{idx}", help=item, type="secondary"):
                    st.session_state.search_field_val = item
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# 🔗 الالتحام البرمجي الكامل وتمرير البيانات لملف العمليات المستقر دون تداخل
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

