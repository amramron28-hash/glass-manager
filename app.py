import streamlit as st
import datetime

# 🔒 1. التأمين البرمجي وتأكيد تهيئة الذاكرة المؤقتة لمنع الـ AttributeError والـ NameError
if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

if "current_stage" not in st.session_state:
    st.session_state.current_stage = 2

# تعريف مبدئي للمتغيرات العالمية لصد أي انهيار فني أثناء إقلاع وقراءة السيرفر
db_data = {}
unique_models = []
total_models = 0
empty_groups_count = 0
brand_counts = {}

# ⚙️ 2. إعدادات الصفحة الأساسية للتطبيق
st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# 📦 3. الاستيرادات البرمجية من الملفات والمحركات الفنية للمشروع
from database import save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)
from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section
)
from app_init import initialize_system_data
from rapidfuzz import process, fuzz
from streamlit_searchbox import st_searchbox

# 📊 4. تشغيل وحقن الخلفيات وقراءة قاعدة البيانات الحقيقية وتعبئة المتغيرات فوراً
inject_pwa_and_styles()
db_data, unique_models, total_models, empty_groups_count, brand_counts = initialize_system_data()

# ==========================================
# 🧠 5. الدوال المنطقية المدمجة بالأعلى لفرز وإدارة المراحل حياً كلياً
# ==========================================

def search_models_callback(search_term, unique_models):
    """البحث اللحظي الذكي والاقتراحات التلقائية لأسماء الهواتف"""
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
    محرك الفرز الصارم والذكي للمراحل: تم ترقيته بالكامل ليحتوي على قوائم خيارات منسدلة 
    تمنع الفني من الأخطاء الإملائية مع تثبيت إشعارات النجاح والتأكيد اللحظي.
    """
    norm_model = normalize_text(current_search)

    # 📋 تجهيز الخيارات الثابتة والمصطلحات الدقيقة للتطبيق لتوحيد شجرة البيانات
    screen_options = [
        "Flat Screen (شاشة مسطحة عادية)",
        "Punch-Hole (شاشة بثقب كاميرا)",
        "Notch Screen (شاشة بنوتش)",
        "Curved Screen (شاشة منحنية)"
    ]
    
    sensor_options = [
        "Virtual Proximity Sensor (مستشعر افتراضي)",
        "Hardware Sensor (مستشعر حقيقي مدمج)",
        "Top Bezel Sensor (مستشعر في الإطار العلوي)"
    ]

    # 📌 المرحلة الثانية: البحث عن المواصفات الفنية داخل المجموعات القائمة حالياً فقط
    if st.session_state.current_stage == 2:
        st.markdown("<h3 style='text-align:right; color:#e67e22;'>🔄 المرحلة الثانية: فحص الأبعاد الفنية للمجموعات القائمة</h3>", unsafe_allow_html=True)
        
        with st.form("stage_2_search_form", clear_on_submit=False):
            st.markdown("<p style='text-align:right; color:#a0aec0; font-size:18px;'>المراقب الصامت يحلل الآن حياً... اختر مواصفات هاتف الزبون بلمسة واحدة دون كتابة:</p>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                input_size = st.text_input("📏 المقاس المراد فحصه (مثال: 6.67)")
            with col2:
                selected_panel = st.selectbox("📺 نوع وبنية الشاشة", options=screen_options)
            with col3:
                selected_sensor = st.selectbox("👁️ مستشعر التقارب المخصص", options=sensor_options)
            
            submitted_stage2 = st.form_submit_button("⚡ تشغيل الفحص والمطابقة الحية")

            if submitted_stage2:
                if not input_size.strip():
                    st.error("⚠️ يرجى إدخال مقاس الهاتف الفعلي للمرحلة الثانية!")
                    return

                norm_size = normalize_text(input_size)
                
                # 🛠️ الإصلاح الجذري الفوري: التقاط [0] لمنع الـ AttributeError وقراءة النصوص كلياً كسرير نظيف
                norm_panel = normalize_text(selected_panel.split(" (")[0])
                norm_sensor = normalize_text(selected_sensor.split(" (")[0])

                try:
                    float(norm_size)
                except ValueError:
                    st.error("❌ تنبيه من المراقب الصامت: خانة المقاس يجب أن تحتوي على رقم (مثل: 6.67) وليس نصوصاً!")
                    return

                structure_exists = (
                    norm_size in db_data
                    and norm_panel in db_data[norm_size]
                    and norm_sensor in db_data[norm_size][norm_panel]
                )

                if structure_exists:
                    target_node = db_data[norm_size][norm_panel][norm_sensor]
                    if isinstance(target_node, list):
                        db_data[norm_size][norm_panel][norm_sensor] = {"models": target_node}
                    
                    models = db_data[norm_size][norm_panel][norm_sensor]["models"]
                    if norm_model not in models:
                        models.append(norm_model)
                        save_db(db_data)
                        st.toast(f"🎯 تم ربط [{norm_model}] بالمجموعة بنجاح!")
                        st.session_state.custom_search_input = "" # تصفير الحقل للعودة
                        st.session_state.current_stage = 2 
                        st.rerun()
                    else:
                        st.info("📢 أذن المراقب الصامت: هذا الهاتف مسجل بالفعل داخل هذه المجموعة مسبقاً.")
                else:
                    st.session_state.temp_size = norm_size
                    st.session_state.temp_panel = norm_panel
                    st.session_state.temp_sensor = norm_sensor
                    st.session_state.current_stage = 3 
                    st.rerun()

        if st.button("➕ لم أجد المواصفات، الانتقال للمرحلة الثالثة لإدراج مجموعة جديدة"):
            st.session_state.temp_size = ""
            st.session_state.temp_panel = ""
            st.session_state.temp_sensor = ""
            st.session_state.current_stage = 3
            st.rerun()

    # 📌 المرحلة الثالثة: إنشاء وإدراج الهاتف كمجموعة جديدة كلياً (ممنوع ظهورها مسبقاً قبل فشل الثانية)
    elif st.session_state.current_stage == 3:
        st.markdown("<h3 style='text-align:right; color:#ef4444;'>🆕 المرحلة الثالثة: إنشاء وإدراج مجموعة جديدة كلياً بالسيستم</h3>", unsafe_allow_html=True)
        st.warning("⚠️ المراقب الصامت أكد عدم وجود مواصفات مطابقة مسبقاً! يرجى تأكيد الخيارات لإنشاء المجموعة الجديدة نهائياً.")
        
        default_size = st.session_state.get("temp_size", "")

        with st.form("stage_3_creation_form", clear_on_submit=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_size = st.text_input("📏 تأكيد مقاس المجموعة الجديدة", value=default_size)
            with col2:
                new_panel = st.selectbox("📺 تأكيد نوع وبنية الشاشة الجديدة", options=screen_options)
            with col3:
                new_sensor = st.selectbox("👁️ تأكيد مستشعر التقارب المخصص الجديد", options=sensor_options)
            
            submitted_stage3 = st.form_submit_button("✨ إنشاء المجموعة الجديدة وحفظ الهاتف رسمياً")

            if submitted_stage3:
                if not new_size.strip():
                    st.error("⚠️ يرجى التأكد من إدخال مقاس المجموعة الجديدة!")
                    return

                norm_size = normalize_text(new_size)
                
                # 🛠️ دمج وتطهير أمان مصفوفات السلسلة للمرحلة الثالثة لمنع أخطاء التوجيه
                norm_panel = normalize_text(new_panel.split(" (")[0])
                norm_sensor = normalize_text(new_sensor.split(" (")[0])

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
                
                # تثبيت إشعار الحفظ بنجاح كلي أمام عين الفني
                st.session_state.show_success_toast = f"✨ تم إنشاء مجموعة جديدة [{new_size}] وحفظ الهاتف [{current_search}] بنجاح كلي!"
                st.session_state.custom_search_input = "" 
                st.session_state.current_stage = 2
                st.rerun()
        
        if st.button("⬅️ تراجع والعودة للمرحلة الثانية"):
            st.session_state.current_stage = 2
            st.rerun()
# ==========================================
# 📱 الواجهة الرئيسية (العنوان الممتد بصفين فقط باللون الأزرق السماوي)
# ==========================================

# 🌆 الصف الأول: الاسم ممتد بالكامل باللون الأزرق السماوي المضيء في الأعلى تماماً مقاس متوافق للهاتف
st.markdown(
    """
    <div style="width: 100%; display: flex; justify-content: flex-start; align-items: center; margin-bottom: 2px; padding: 0px 5px; border-bottom: 2px solid rgba(0, 191, 255, 0.3); margin-top: -20px;">
        <span style="font-size: 28px; font-weight: 900; color: #00bfff; font-family: 'Courier New', monospace; letter-spacing: 1px; white-space: nowrap;">ZEGAAR AMMAR</span>
    </div>
    """, 
    unsafe_allow_html=True
)

# 🌆 الصف الثاني: الوظيفة ممتدة بالكامل أسفله مباشرة بنفس التناسب البرمجي الصافي دون تكرار
st.markdown(
    """
    <div style="width: 100%; display: flex; justify-content: flex-start; align-items: center; margin-bottom: 35px; padding: 0px 5px;">
        <span style="font-size: 28px; font-weight: 900; color: #00bfff; font-family: 'Courier New', monospace; letter-spacing: 1px; white-space: nowrap;">GLASS MANAGER</span>
    </div>
    """, 
    unsafe_allow_html=True
)

# 📢 التقاط وعرض إشعار النجاح المكتمل والمثبت للمرحلة الثالثة أمام الفني بوضوح خارق
if "show_success_toast" in st.session_state and st.session_state.show_success_toast:
    st.success(st.session_state.show_success_toast)
    st.toast(st.session_state.show_success_toast)
    st.session_state.show_success_toast = ""

# 🔍 صندوق البحث الذكي بالمقترحات الفورية اللحظية
selected_phone = st_searchbox(
    search_function=lambda q, **k: search_models_callback(
        q,
        unique_models
    ),
    placeholder="🔍 ابحث عن هاتف أو اكتب اسماً جديداً واضغط تأكيد بالأسفل...",
    key="phone_search_autocomplete_v4",
    label=""
)

# 🔒 المعالجة الهجينة الخارقة: حقل نصي مساعد يظهر فقط ليرى الفني ما يكتبه ويثبته داخل المراحل لمنع اختفاء الخطة
if selected_phone:
    st.session_state.custom_search_input = selected_phone.strip()
    st.session_state.current_stage = 2

# إذا كتب الفني اسماً جديداً تماماً وظهرت "No options"، نتيح له هنا زر تأكيد الاسم المكتوب لتنشيط الخطة حياً
if not selected_phone:
    st.markdown("<p style='color:#a0aec0; margin-bottom: 2px; text-align: right;'>➕ إذا كان الهاتف جديداً كلياً، اكتبه بالأسفل لفتح المرحلة الثانية مباشرة:</p>", unsafe_allow_html=True)
    custom_typed = st.text_input(label="", placeholder="اكتب اسم الهاتف الجديد هنا لتأكيده الفوري...", key="fallback_manual_input_text_v4")
    if custom_typed.strip() and custom_typed.strip() != st.session_state.custom_search_input:
        st.session_state.custom_search_input = custom_typed.strip()
        st.session_state.current_stage = 2

# تفعيل وعرض تدفق المراحل بناءً على الاسم المعتمد في الذاكرة
if st.session_state.custom_search_input:
    current_search = st.session_state.custom_search_input
    
    st.markdown(f"<p style='color:#00bfff; font-size:18px; font-weight:bold; text-align:right;'>📱 الهاتف المبحوث عنه حالياً: [{current_search}]</p>", unsafe_allow_html=True)
    
    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(
        db_data,
        current_search
    )

    # -------------------------------------------------------------
    # 📌 المرحلة الأولى: الهاتف مسجل وموجود بالفعل بالسيستم (تم فحص المطابقة والإنهاء)
    # -------------------------------------------------------------
    if size_grp:
        compat_results = get_compatibles_strict(
            db_data,
            current_search
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.success(
            f"🎯 الموديل [{real_name}] مسجل ومتوافق حياً في النظام!"
        )

        # رسم كروت الأبعاد الفنية للمجموعة
        draw_technical_coords(
            size_grp,
            panel_grp,
            sensor_grp
        )

        # إنتاج الأقسام الملونة بالكامل (ملء الخلفية بالألوان المحددة مصمتة)
        draw_neon_section(
            "مطابقة للمقاس تماماً (Exact Matches)",
            compat_results["exact"],
            "#2ecc71", # أخضر مصمت بالكامل
            "🎯",
            current_search
        )

        draw_neon_section(
            "أكبر بقليل (Plus Sizes)",
            compat_results["plus"],
            "#3498db", # أزرق مصمت بالكامل
            "➕",
            current_search
        )

        draw_neon_section(
            "أصغر بقليل (Minus Sizes)",
            compat_results["minus"],
            "#e67e22", # برتقالي مصمت بالكامل
            "➖",
            current_search
        )

        draw_neon_section(
            "مستشعر مختلف (Warning)",
            compat_results["warn"],
            "#ef4444", # أحمر مصمت بالكامل للتحذير
            "⚠️",
            current_search
        )

    # -------------------------------------------------------------
    # 📌 المرحلة الثانية والثالثة بشكل مستقل وصارم كلياً (التحويل التلقائي الذكي)
    # -------------------------------------------------------------
    else:
        # استدعاء دالة المنطق المعزولة بالأعلى لضمان التتابع وعزل النوافذ تماماً
        process_new_model_form(
            db_data,
            current_search
        )

# ==========================================
# 🛠️ اللوحة الجانبية (محمية ومؤمنة تماماً ضد أخطاء التعريف)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:right;color:#00bfff;'>🛠️ المراقب الصامت</h2>", unsafe_allow_html=True)
    st.markdown("---")

    with st.expander("🔔 جرس الإشعارات اللحظي", expanded=True):
        st.info("💡 النظام سحابي مستقر 100% وعين المراقب الصامت نشطة حياً لحماية الشجرة.")

    with st.expander("⚙️ الإعدادات والتحكم بالـ RAM", expanded=True):
        st.write(f"📅 تاريخ اليوم الفني: **{datetime.date.today().strftime('%Y-%m-%d')}**")
        st.metric(label="📈 إجمالي الهواتف بالسيستم", value=total_models)
        st.markdown("---")

        if brand_counts:
            for b_name, b_count in sorted(brand_counts.items(), key=lambda x: x, reverse=True)[:4]:
                percentage = round((b_count / total_models) * 100, 1) if total_models else 0
                st.markdown(f"📋 <b>{b_name}</b>: {b_count} ({percentage}%)", unsafe_allow_html=True)
                st.progress(percentage / 100)

        st.markdown("---")
        if st.button("🧹 تشغيل الصيانة وتطهير الشجرة", key="sidebar_inspector_btn"):
            cleaned_db, changes_made = run_intelligent_inspector(db_data)
            if changes_made:
                save_db(cleaned_db)
                st.success("✨ تم تطهير الشجرة وترتيب الموديلات بنجاح!")
                st.rerun()
            else:
                st.toast("🎯 السيستم مطهر ونظيف بالكامل مسبقاً.")
