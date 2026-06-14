import streamlit as st
from database import save_db
from logic_engine import normalize_text
from rapidfuzz import process, fuzz

def search_models_callback(search_term, unique_models):
    """البحث اللحظي الذكي عن أسماء الهواتف"""
    if not search_term or not search_term.strip():
        return []

    search_normalized = normalize_text(search_term.strip().lower())
    fuzzy_results = process.extract(
        search_normalized,
        unique_models,
        scorer=fuzz.WRatio,
        limit=8
    )
    return [match for match, score, _ in fuzzy_results if score > 60]

def process_new_model_form(db_data, current_search):
    """
    إدارة المرحلة الثانية والمرحلة الثالثة بفصل صارم يمنع ظهور النوافذ بشكل متداخل مسبقاً،
    مع تفعيل عين وأذن 'المراقب الصامت' لحماية البيانات من التكرار العشوائي.
    """
    # 👁️ تهيئة حالة المرحلة الحالية لتبدأ من المرحلة الثانية فوراً عند غياب الاسم
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = 2  

    norm_model = normalize_text(current_search)

    # -------------------------------------------------------------
    # 📌 المرحلة الثانية: البحث عن المقاس والمواصفات داخل المجموعات الحالية فقط
    # -------------------------------------------------------------
    if st.session_state.current_stage == 2:
        st.markdown("<h3 style='text-align:right; color:#e67e22;'>🔄 المرحلة الثانية: فحص الأبعاد الفنية للمجموعات القائمة</h3>", unsafe_allow_html=True)
        
        with st.form("stage_2_search_form", clear_on_submit=False):
            st.markdown("<p style='text-align:right; color:#a0aec0; font-size:18px;'>المراقب الصامت يبحث الآن... أدخل مواصفات الهاتف للبحث عن مجموعة مطابقة متوفرة بالسيستم حالياً:</p>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                input_size = st.text_input("📏 المقاس المراد فحصه")
            with col2:
                input_panel = st.text_input("📺 نوع الشاشة المراد فحصها")
            with col3:
                input_sensor = st.text_input("👁️ مستشعر التقارب المراد فحصه")
            
            submitted_stage2 = st.form_submit_button("⚡ فحص ومطابقة بالمجموعات الحالية")

            if submitted_stage2:
                if not (input_size.strip() and input_panel.strip() and input_sensor.strip()):
                    st.error("⚠️ يرجى ملء جميع الحقول الفنية للمرحلة الثانية!")
                    return

                norm_size = normalize_text(input_size)
                norm_panel = normalize_text(input_panel)
                norm_sensor = normalize_text(input_sensor)

                # 👁️ عين المراقب الصامت: فحص منطقية المقاس لمنع إدخال نصوص عشوائية
                try:
                    float(norm_size)
                except ValueError:
                    st.error("❌ تنبيه من المراقب الصامت: خانة المقاس يجب أن تحتوي على رقم (مثل: 6.67 أو 6.5) وليس نصوصاً!")
                    return

                # التحقق الفعلي من وجود هذه التوليفة الفنية في المجموعات الحالية
                structure_exists = (
                    norm_size in db_data
                    and norm_panel in db_data[norm_size]
                    and norm_sensor in db_data[norm_size][norm_panel]
                )

                if structure_exists:
                    # المجموعة موجودة -> نربط الهاتف بها فوراً وينتهي العمل بنجاح
                    target_node = db_data[norm_size][norm_panel][norm_sensor]
                    if isinstance(target_node, list):
                        db_data[norm_size][norm_panel][norm_sensor] = {"models": target_node}
                    
                    models = db_data[norm_size][norm_panel][norm_sensor]["models"]
                    if norm_model not in models:
                        models.append(norm_model)
                        save_db(db_data)
                        st.success(f"🎯 تم العثور على المجموعة بنجاح! ودمج الهاتف [{norm_model}] بداخلها كلياً.")
                        st.session_state.current_stage = 2 
                        st.rerun()
                    else:
                        st.info("📢 أذن المراقب الصامت: هذا الهاتف مسجل بالفعل داخل هذه المجموعة مسبقاً.")
                else:
                    # ❌ لم نجد المواصفات -> يتم إنهاء المرحلة الثانية تماماً والانتقال الصارم للمرحلة الثالثة بعد الضغط
                    st.session_state.temp_size = norm_size
                    st.session_state.temp_panel = norm_panel
                    st.session_state.temp_sensor = norm_sensor
                    st.session_state.current_stage = 3 
                    st.rerun()

        # زر أمان فوري للانتقال للمرحلة الثالثة مباشرة إذا كان الفني متأكداً أن الهاتف جديد كلياً
        if st.button("➕ لم أجد المواصفات، الانتقال للمرحلة الثالثة لإدراج مجموعة جديدة"):
            st.session_state.temp_size = ""
            st.session_state.temp_panel = ""
            st.session_state.temp_sensor = ""
            st.session_state.current_stage = 3
            st.rerun()

    # -------------------------------------------------------------
    # 📌 المرحلة الثالثة: إدراج كمجموعة جديدة كلياً (ممنوع ظهورها مسبقاً قبل انتهاء المرحلة الثانية)
    # -------------------------------------------------------------
    elif st.session_state.current_stage == 3:
        st.markdown("<h3 style='text-align:right; color:#ef4444;'>🆕 المرحلة الثالثة: إنشاء وإدراج مجموعة جديدة كلياً بالسيستم</h3>", unsafe_allow_html=True)
        st.warning("⚠️ المراقب الصامت أكد عدم وجود مواصفات مطابقة مسبقاً! يرجى تأكيد بيانات المجموعة الجديدة الآن لحفظها نهائياً.")
        
        # استرجاع القيم المكتوبة في المرحلة السابقة تلقائياً لتسريع العمل الفني ومنع تكرار الكتابة
        default_size = st.session_state.get("temp_size", "")
        default_panel = st.session_state.get("temp_panel", "")
        default_sensor = st.session_state.get("temp_sensor", "")

        with st.form("stage_3_creation_form", clear_on_submit=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_size = st.text_input("📏 تأكيد مقاس المجموعة الجديدة", value=default_size)
            with col2:
                new_panel = st.text_input("📺 تأكيد نوع الشاشة للمجموعة الجديدة", value=default_panel)
            with col3:
                new_sensor = st.text_input("👁️ تأكيد الحساس للمجموعة الجديدة", value=default_sensor)
            
            submitted_stage3 = st.form_submit_button("✨ إنشاء المجموعة الجديدة وحفظ الهاتف رسمياً")

            if submitted_stage3:
                if not (new_size.strip() and new_panel.strip() and new_sensor.strip()):
                    st.error("⚠️ يرجى التأكد من ملء كافة البيانات الفنية لإنشاء المجموعة الجديدة!")
                    return

                norm_size = normalize_text(new_size)
                norm_panel = normalize_text(new_panel)
                norm_sensor = normalize_text(new_sensor)

                # 👁️ عين المراقب الصامت: حماية شجرة البيانات السحابية والمحلية من التخريب البرمجي
                try:
                    float(norm_size)
                except ValueError:
                    st.error("❌ خطأ فني: لا يمكن إنشاء مجموعة بمقاس غير رقمي!")
                    return

                if norm_size not in db_data:
                    db_data[norm_size] = {}
                if norm_panel not in db_data[norm_size]:
                    db_data[norm_size][norm_panel] = {}

                db_data[norm_size][norm_panel][norm_sensor] = {"models": [norm_model]}
                
                save_db(db_data)
                st.success(f"✨ نجاح كلي! تم إنشاء شجرة المجموعة الفنية الجديدة [{norm_size}] وحفظ الهاتف بنجاح كلي تحت مراقبة النظام.")
                
                # إعادة تهيئة النظام للموديل القادم والعودة الآمنة للمرحلة 2
                st.session_state.current_stage = 2
                st.rerun()
        
        if st.button("⬅️ تراجع والعودة للمرحلة الثانية"):
            st.session_state.current_stage = 2
            st.rerun()
