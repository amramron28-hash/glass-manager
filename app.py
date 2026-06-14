import streamlit as st
import datetime

# 🔒 تأمين وإصلاح الذاكرة المؤقتة فوراً في أول السطر قبل قراءتها لمنع الانهيار
if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

if "current_stage" not in st.session_state:
    st.session_state.current_stage = 2

from database import save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)

from streamlit_searchbox import st_searchbox

from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section
)

from app_init import initialize_system_data
from rapidfuzz import process, fuzz

# ==========================================
# 🧠 منطق التحكم وفصل المراحل حياً داخل الملف
# ==========================================

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
    norm_model = normalize_text(current_search)

    # 📌 المرحلة الثانية: البحث عن المقاس والمواصفات داخل المجموعات الحالية فقط
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
                        st.success(f"🎯 تم العثور على المجموعة بنجاح! ودمج الهاتف [{norm_model}] بداخلها كلياً.")
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

    # 📌 المرحلة الثالثة: إدراج كمجموعة جديدة كلياً (ممنوع ظهورها مسبقاً)
    elif st.session_state.current_stage == 3:
        st.markdown("<h3 style='text-align:right; color:#ef4444;'>🆕 المرحلة الثالثة: إنشاء وإدراج مجموعة جديدة كلياً بالسيستم</h3>", unsafe_allow_html=True)
        st.warning("⚠️ المراقب الصامت أكد عدم وجود مواصفات مطابقة مسبقاً! يرجى تأكيد بيانات المجموعة الجديدة الآن لحفظها نهائياً.")
        
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
                st.session_state.current_stage = 2
                st.rerun()
        
        if st.button("⬅️ تراجع والعودة للمرحلة الثانية"):
            st.session_state.current_stage = 2
            st.rerun()

# ==========================================
# ⚙️ بدء تهيئة الواجهة والبيانات
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

inject_pwa_and_styles()
db_data, unique_models, total_models, empty_groups_count, brand_counts = initialize_system_data()

# ==========================================
# 🛠️ اللوحة الجانبية (المراقب الصامت الذكي)
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


