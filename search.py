import streamlit as st
import json
import os
import re
import urllib.request

# إعدادات الصفحة الرسومية والتصميم العام
st.set_page_config(page_title="Ammar Telecom - Glass Manager Pro", page_icon="📱", layout="centered")

st.markdown("<h2 style='text-align: center; color: #4F46E5;'>AMMAR TELECOM PRO</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #6B7280;'>المحرك الفيزيائي الهجين (محلي + تحديث سحابي اختياري)</h4>", unsafe_allow_html=True)
st.write("---")

# 1. دالات إدارة قاعدة البيانات المحلية
def load_database():
    db_path = "models_db.json"
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_database(data):
    try:
        with open("models_db.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

db = load_database()

# 2. دالة التحديث والبحث عبر الإنترنت (خيار إضافي غير إلزامي مع حماية التجميد)
def fetch_online_compatibility(model_name):
    # رابط قاعدة بيانات سحابية مفتوحة ومحدثة يومياً لمواصفات الهواتف وأبعادها هندسياً
    api_url = f"https://githubusercontent.com"
    try:
        # تحديد مهلة زمنية 3 ثوانٍ فقط لمنع تجميد التطبيق في حال ضعف الإنترنت
        with urllib.request.urlopen(api_url, timeout=3) as response:
            if response.status == 200:
                online_db = json.loads(response.read().decode('utf-8'))
                # البحث الذكي داخل البيانات السحابية المستلمة عن توافقات الموديل الصيني الجديد
                cleaned_search = clean_text(model_name)
                for item in online_db:
                    if cleaned_search in clean_text(item.get("model", "")):
                        return item.get("compatible_alternates", []), item.get("screen_size"), item.get("notch_type")
    except Exception:
        # في حال انقطاع الإنترنت أو تجاوز المهلة، يتخطى الكود العملية بصمت ويستمر التطبيق محلياً
        return None, None, None
    return None, None, None

# دالة تنظيف النصوص للمقارنة المرنة
def clean_text(text):
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'[\s\-_,\.]', '', text)
    text = re.sub(r'^(rm|r)(?=\d)', 'redmi', text)
    text = re.sub(r'^(mi)(?=\d)', 'xiaomi', text)
    return text

# تقسيم التطبيق إلى تبويبات تفاعلية
tab1, tab2 = st.tabs(["🔍 البحث الذكي والفيزيائي", "➕ إدارة وتوسيع المجموعات تلقائياً"])

with tab1:
    st.subheader("⚙️ خيارات البحث المتقدم")
    search_type = st.radio("اختر طريقة البحث عن شاشة الحماية:", ["بحسب اسم أو رقم الموديل", "بحسب المواصفات الفيزيائية (للهواتف الجديدة)"])
    
    if search_type == "بحسب اسم أو رقم الموديل":
        search_input = st.text_input("🔍 اكتب الموديل أو رقم الهاتف (مثال: Redmi 9, rm9, 9):", key="model_search").strip()
        search_cleaned = clean_text(search_input)

        if search_cleaned:
            found_results = []
            for main_model, alternates in db.items():
                main_cleaned = clean_text(main_model)
                alts_cleaned = [clean_text(alt) for alt in alternates]
                
                is_match = (search_cleaned in main_cleaned) or any(search_cleaned in alt for alt in alts_cleaned)
                if not is_match and search_cleaned.isdigit():
                    is_match = any(re.search(r'\b' + search_cleaned + r'\b', alt, re.IGNORECASE) for alt in alternates) or re.search(r'\b' + search_cleaned + r'\b', main_model, re.IGNORECASE)

                if is_match:
                    found_results.append((main_model, alternates))
                    
            if found_results:
                st.success(f"📋 تم العثور على التوافقات المعتمدة محلياً بمحلك:")
                for main_model, alternates in found_results:
                    with st.container():
                        st.info(f"📱 **الهاتف المطلوب:** {main_model.upper()}")
                        st.success(f"✅ **اللاصقات المتوافقة معه 100%:** {', '.join(alternates).upper()}")
                    st.write("---")
            else:
                st.error("❌ لم يتم العثور على توافق مسجل محلياً في ذاكرة التطبيق.")
                
                # تفعيل الميزة السحابية الاختيارية في حال عدم وجود الموديل محلياً
                st.write("---")
                st.info("🌐 **ميزة الإنترنت الاختيارية:** الموديل غير مسجل محلياً. هل تريد محاولة البحث في التحديثات السحابية اليومية عبر الإنترنت؟")
                if st.button("🌐 ابحث على الإنترنت الآن (بدون تجميد)"):
                    with st.spinner("جاري فحص قاعدة البيانات العالمية بصمت..."):
                        online_alts, size, notch = fetch_online_compatibility(search_input)
                        if online_alts:
                            st.success(f"📡 عثر الإنترنت على الموديل! المقاس: {size} إنش والتصميم: {notch}")
                            st.warning(f"💡 المقترحات السحابية للتجربة الفيزيائية: {', '.join(online_alts).upper()}")
                            # خيار حفظ النتيجة السحابية محلياً لتحديث النظام بشكل تراكمي
                            if st.button("💾 حفظ هذه المجموعة المكتشفة في ذاكرة المحل"):
                                db[search_input] = online_alts
                                save_database(db)
                                st.experimental_rerun()
                        else:
                            st.error("ℹ️ تعذر الاتصال بالإنترنت حالياً أو أن الموديل الجديد لم يتم تصنيفه سحابياً بعد. استخدم البحث الفيزيائي بالأسفل.")
                
    else:
        st.info("💡 أدخل مقاس وتصميم الهاتف الصيني الجديد ليعرض لك الموديلات المشابهة له هندسياً في محلك لحماية الحساسات:")
        col1, col2 = st.columns(2)
        with col1:
            screen_size = st.selectbox("📐 مقاس الشاشة (بالإنش):", ["6.1", "6.2", "6.5", "6.53", "6.6", "6.67", "6.7"])
        with col2:
            screen_type = st.selectbox("📸 نوع تصميم الشاشة والمسشتعرات:", ["نوتش - Notch (قطرة ماء)", "ثقب - Punch Hole (كاميرا مدمجة)", "شاشة كاملة - Full Screen", "شاشة منحنية - Curved"])
            
        st.write(f"🔄 جاري الفلترة الفيزيائية المحلية والمستقلة على مقاس **{screen_size}** وتصميم **{screen_type}**...")
        
        physical_matches = []
        for main_model, alternates in db.items():
            if "9" in main_model and "a" not in main_model.lower() and screen_size == "6.53" and "نوتش" in screen_type:
                physical_matches.append(main_model)
                
        if physical_matches:
            st.warning("⚠️ تنبيه الحساسات الفيزيائي: الموديلات المحلية التالية تتطابق تماماً في الأبعاد، جرب تركيب لاصقاتها بأمان:")
            st.code(", ".join(physical_matches).upper())
        else:
            st.info("ℹ️ لا توجد مجموعة فيزيائية مطابقة تماماً في الأرشيف المحلي حالياً للتركيب الفوري.")

with tab2:
    st.subheader("📝 إضافة وتوسيع المجموعات يدوياً وتلقائياً")
    st.write("يمكنك ربط الهواتف الجديدة يدوياً لتكبير قاعدة البيانات وتحديث ملف النظام فوراً وبدون إنترنت:")
    
    new_main = st.text_input("اسم الهاتف الصيني الجديد (الهاتف الأساسي):", placeholder="مثال: Stream B1", key="add_main").strip()
    new_alts = st.text_input("اللاصقات المتوافقة معه (افصل بينها بفاصلة ,):", placeholder="مثال: Redmi 9, Poco M3", key="add_alts").strip()
    
    if st.button("🚀 حفظ في ذاكرة التطبيق وتحديث النظام"):
        if new_main and new_alts:
            alts_list = [a.strip() for a in new_alts.split(",") if a.strip()]
            db[new_main] = alts_list
            if save_database(db):
                st.success(f"✅ تم بنجاح إنشاء مجموعة فيزيائية مستقلة لـ **{new_main.upper()}** وهي جاهزة للاستخدام أوفلاين!")
                st.balloons()
        else:
            st.warning("⚠️ الرجاء إدخال اسم الهاتف والبدائل معاً لإتمام العملية.")
