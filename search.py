import streamlit as st
import json
import os
import re

# 1. إعدادات الصفحة الرسومية الاحترافية وتثبيت التصميم العالي
st.set_page_config(page_title="Zegaar Ammar - Glass Manager", page_icon="📱", layout="centered")

# دالة مخصصة لحقن تصميم الـ CSS لتطابق الصورة المرفقة تماماً
st.markdown("""
    <style>
    /* خلفية التطبيق العامة */
    .stApp {
        background: linear-gradient(135deg, #f4f7f6 0%, #e9eff1 100%);
    }
    /* تصميم الهيدر العلوي العصري */
    .header-title {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
        color: #2563EB;
        font-size: 42px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 5px;
    }
    .header-subtitle {
        text-align: center;
        color: #6B7280;
        font-size: 16px;
        margin-bottom: 25px;
    }
    /* تصميم بطاقات عرض الهواتف الكرتونية الملونة زاهية الحواف */
    .phone-card {
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06);
        display: flex;
        align-items: center;
        transition: transform 0.2s;
        border: 1px solid rgba(0,0,0,0.03);
    }
    .phone-card:hover {
        transform: translateY(-4px);
    }
    /* تلوين البطاقات ديناميكياً بناء على التوافق */
    .card-blue { background-color: #DBEAFE; color: #1E40AF; }
    .card-green { background-color: #D1FAE5; color: #065F46; }
    .card-orange { background-color: #FFEDD5; color: #9A3412; }
    .card-purple { background-color: #F3E8FF; color: #6B21A8; }
    
    .phone-icon {
        font-size: 45px;
        margin-left: 20px;
        background: rgba(255,255,255,0.6);
        padding: 10px;
        border-radius: 15px;
    }
    .phone-details {
        flex-grow: 1;
        text-align: right;
    }
    .model-title {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .compat-badge {
        background-color: rgba(255,255,255,0.8);
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# 2. توليد أو قراءة قاعدة البيانات
def load_database():
    db_path = "models_db.json"
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    # قاعدة بيانات افتراضية تحتوي على مجموعتك النموذجية ومجموعات فيزيائية أخرى في حال عدم وجود الملف
    default_db = {
        "Group_RM12": ["RM 12", "RM 12 5G", "RM NOTE 12R", "RM NOTE 13R", "RM 13", "RM 13 5G", "POCO M6 PRO 5G", "POCO M6 4G", "POCO M6 PLUS"],
        "Group_Redmi9": ["REDMI 9", "POCO M3", "REDMI 9 PRIME"],
        "Group_iPhone15": ["IPHONE 15 PRO MAX", "IPHONE 15 PRO MARA", "IPHONE 15 PRO"]
    }
    return default_db

db = load_database()

# دالة تنظيف صارمة لمطابقة دقيقة للاختصارات والأرقام بدون تداخل
def clean_text(text):
    if not text:
        return ""
    text = str(text).lower().strip()
    text = re.sub(r'[\s\-_,\.]', '', text)
    # توحيد صيغ الاختصارات الأكثر شيوعاً بمحلك لضمان قفل البحث
    text = re.sub(r'^(rm)(?=\d)', 'redmi', text)
    return text

# عرض شعار المحل الرئيسي الملون العلوي
st.markdown("<div class='header-title'>Zegaar ammar</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>📱 النظام الاحترافي للمطابقة والفلترة الفيزيائية الصارمة</div>", unsafe_allow_html=True)

# صندوق البحث الذكي المدمج بالمظهر العصري
search_input = st.text_input("", placeholder="🔍 ابحث عن هاتف... (مثال: RM 12 أو 9)").strip()
search_cleaned = clean_text(search_input)

if search_cleaned:
    target_group = None
    matched_model_name = ""
    
    # خطوة البحث الصارم: البحث عن المجموعة المحددة التي تحتوي على الهاتف المطلوب فقط
    for group_id, models_list in db.items():
        for model in models_list:
            if search_cleaned == clean_text(model) or (search_cleaned.isdigit() and search_cleaned in clean_text(model)):
                target_group = models_list
                matched_model_name = model
                break
        if target_group:
            break

    # خطوة عرض النتائج الاحترافية المطابقة للصورة تماماً وبألوان كرتونية منوعة
    if target_group:
        st.write(f"### 📋 الهواتف المتوافقة مع الموديل المستهدف:")
        
        # مصفوفة ألوان لتنويع أشكال البطاقات تلقائياً مثل الصورة تماماً
        colors = ["card-blue", "card-green", "card-orange", "card-purple"]
        
        for index, item in enumerate(target_group):
            # تمييز الهاتف المبحوث عنه بلون خاص أو تركه منسقاً ضمن المجموعة لبيان التوافق المتبادل كاملاً
            card_color = colors[index % len(colors)]
            
            card_html = f"""
            <div class="phone-card {card_color}">
                <div class="phone-icon">📱</div>
                <div class="phone-details">
                    <div class="model-title">{item.upper()}</div>
                    <div class="compat-badge">✅ متوافق فيزيائياً 100%</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.error("❌ عذراً، هذا الموديل غير مدرج في أي مجموعة توافق فيزيائي بمحلك حالياً.")
else:
    # عرض واجهة ترحيبية كرتونية تحتوي على عينات سريعة من الموديلات عند فتح التطبيق لأول مرة مثل لقطة شاشتك
    st.write("### 📱 عينات من مجموعات التوافق المتاحة بمحلك:")
    sample_models = ["iPhone 15 Pro Max", "Samsung Galaxy S24 Ultra", "Google Pixel 8 Pro", "RM 12 (Poco M6)"]
    colors = ["card-blue", "card-green", "card-orange", "card-purple"]
    
    for index, item in enumerate(sample_models):
        card_color = colors[index % len(colors)]
        card_html = f"""
        <div class="phone-card {card_color}">
            <div class="phone-icon">📱</div>
            <div class="phone-details">
                <div class="model-title">{item}</div>
                <div class="compat-badge">جاهز للفحص الفيزيائي والمطابقة</div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
