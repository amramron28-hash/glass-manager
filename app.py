import streamlit as st
import datetime
from database import load_db, add_model, save_db
from logic_engine import (
    normalize_text, find_model_coords, get_compatibles_strict, run_intelligent_inspector
)
from ui_components import (
    inject_pwa_and_styles, draw_technical_coords, draw_neon_section
)
from app_init import initialize_system_data
from rapidfuzz import process, fuzz
from streamlit_searchbox import st_searchbox

# 🔒 1. تهيئة الذاكرة المؤقتة والحالة الفنية لخطة المراحل
if "custom_search_input" not in st.session_state:
    st.session_state.custom_search_input = ""

# ⚙️ 2. إعدادات الصفحة الأساسية للتطبيق
st.set_page_config(layout="wide", page_title="ZEGAAR AMMAR GLASS MANAGER", page_icon="🔍")
inject_pwa_and_styles()

# 📊 3. قراءة البيانات الحية من السحابة وتعبئة المؤشرات
db_data, unique_models, total_models, empty_groups_count, brand_counts, live_sizes, live_panels, live_sensors = initialize_system_data()

# العنوان الرئيسي الممتد بصفين نيون
st.markdown("<div style='width: 100%; border-bottom: 2px solid rgba(0, 191, 255, 0.3);'><span style='font-size: 28px; font-weight: 900; color: #00bfff;'>ZEGAAR AMMAR GLASS MANAGER</span></div>", unsafe_allow_html=True)

# التقاط وعرض الإشعارات السحابية الحية
if "show_success_toast" in st.session_state and st.session_state.show_success_toast:
    st.success(st.session_state.show_success_toast)
    st.toast(st.session_state.show_success_toast)
    st.session_state.show_success_toast = ""

# دالة الفرز السريع والذكي لمحرك البحث التجاري تلقائياً
def search_models_callback(query, models_list):
    if not query: return models_list[:10]
    results = process.extract(query, models_list, limit=10, scorer=fuzz.WRatio)
    return [r[0] for r in results]

# صندوق البحث المستقر والمتفاعل مع الأصابع يدوياً
selected_phone = st_searchbox(search_function=lambda q, **k: search_models_callback(q, unique_models), placeholder="🔍 ابحث عن هاتف أو اكتب اسماً جديداً...", key="phone_search_autocomplete_v8")

if selected_phone:
    st.session_state.custom_search_input = selected_phone.strip()

if not selected_phone:
    st.markdown("<p style='color:#a0aec0; margin-bottom: 2px; text-align: right;'>➕ إذا كان الهاتف جديداً، اكتب اسمه بالأسفل للتحقق:</p>", unsafe_allow_html=True)
    
    # 🛠️ تصحيح وتأمين حقل المدخلات النصية بالـ label_visibility لمنع الـ BodyStreamBuffer والانهيار الصامت
    custom_typed = st.text_input(
        label="اسم الهاتف الجديد المكتوب يدوياً", 
        placeholder="اكتب اسم الهاتف الجديد هنا...", 
        key="manual_input_v8",
        label_visibility="collapsed"
    )
    if custom_typed.strip():
        st.session_state.custom_search_input = custom_typed.strip()

# ==========================================
# 🛑 تفعيل وتطبيق تتابع خطة المراحل 1، 2، 3 الصارم
# ==========================================
if st.session_state.custom_search_input:
    current_search = st.session_state.custom_search_input
    st.markdown(f"<p style='color:#00bfff; font-size:18px; font-weight:bold; text-align:right;'>📱 الهاتف الحالي: [{current_search}]</p>", unsafe_allow_html=True)
    
    # 🟢 [المرحلة 1]: فحص وجود الهاتف في السحابة
    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(db_data, current_search)
    
    if size_grp:
        # وجد الهاتف ⬅️ يعرض النيون بالفارق الحسابي الدقيق المقترح (±0.03) وينتهي التتابع تماماً
        compat_results = get_compatibles_strict(db_data, current_search)
        st.success(f"🎯 [المرحلة 1] الموديل [{real_name}] مسجل ومتوافق سحابياً!")
        draw_technical_coords(size_grp, panel_grp, sensor_grp)
        draw_neon_section("مطابقة للمقاس تماماً", compat_results["exact"], "#2ecc71", "🎯", current_search)
        draw_neon_section("أكبر بقليل (فارق دقيق ±0.03)", compat_results["plus"], "#3498db", "➕", current_search)
        draw_neon_section("أصغر بقليل (فارق دقيق ±0.03)", compat_results["minus"], "#e67e22", "➖", current_search)
        draw_neon_section("مستشعر مختلف يحتاج حذر", compat_results["warn"], "#ef4444", "⚠️", current_search)
    
    else:
        # 🟡 [المرحلة 2]: لم يجد الاسم ⬅️ فتح نافذة خيارات النقر المنسدلة الحية للبحث عن عضوية
        st.warning(f"🔍 الموديل [{current_search}] غير مسجل حالياً بالسحابة.")
        st.markdown("<h4 style='color:#e67e22; text-align:right;'>⚙️ [المرحلة 2] تفعيل أزرار خيارات النقر الحية</h4>", unsafe_allow_html=True)
        
        # خيارات حية قابلة للنقر مسحوبة تلقائياً من مخزون السحابة الفعلي
        sel_size = st.selectbox("📏 1. اختر مقاس الهاتف المتوفر (Size):", [""] + live_sizes + ["➕ إضافة مقاس جديد يدوي"])
        final_size = st.text_input("✍️ اكتب المقاس الجديد يدويًا:", key="custom_size_text") if sel_size == "➕ إضافة مقاس جديد يدوي" else sel_size

        final_panel = ""
        if final_size:
            sel_panel = st.selectbox("📺 2. اختر نوع الشاشة المتوفرة (Panel):", [""] + live_panels + ["➕ إضافة نوع شاشة جديد"])
            final_panel = st.text_input("✍️ اكتب نوع الشاشة الجديد:", key="custom_panel_text") if sel_panel == "➕ إضافة نوع شاشة جديد" else sel_panel

        final_sensor = ""
        if final_size and final_panel:
            sel_sensor = st.selectbox("👁️ 3. اختر مستشعر التقارب المتوفر (Sensor):", [""] + live_sensors + ["➕ إضافة مستشعر جديد"])
            final_sensor = st.text_input("✍️ اكتب المستشعر الجديد:", key="custom_sensor_text") if sel_sensor == "➕ إضافة مستشعر جديد" else sel_sensor

        # تشغيل فحص العضوية الحقيقية والمطابقة الفورية بعد الضغط واكتمال الخيارات الثلاثة
        has_matched_group = False
        if final_size.strip() and final_panel.strip() and final_sensor.strip():
            
            if final_size in db_data and final_panel in db_data[final_size] and final_sensor in db_data[final_size][final_panel]:
                matched_models_in_grp = db_data[final_size][final_panel][final_sensor].get("models", [])
                if matched_models_in_grp:
                    has_matched_group = True
                    st.success(f"🤝 وجد ما يطابقه! هذا الهاتف ينتمي لمجموعة الهواتف الحية التالية: {matched_models_in_grp}")
                    
                    with st.form("join_group_form_v8"):
                        st.markdown(f"<p style='color:#2ecc71; text-align:right;'>✍️ هل ترغب في إدراج [{current_search}] ليصبح عضواً جديداً في هذه المجموعة الحية القائمة؟</p>", unsafe_allow_html=True)
                        if st.form_submit_button("نعم، إدراج الهاتف كعضو في المجموعة القائمة 🔗"):
                            if add_model(final_size, final_panel, final_sensor, current_search):
                                st.session_state.show_success_toast = f"تم إدراج {current_search} كعضو في المجموعة السحابية بنجاح!"
                                st.session_state.custom_search_input = ""
                                st.rerun()

        # 🔴 [المرحلة 3]: نفذنا كل ما سبق ولم يظهر شيء ⬅️ توليفة فنية جديدة بالكامل وحجز مجموعة جديدة
        if final_size.strip() and final_panel.strip() and final_sensor.strip() and not has_matched_group:
            st.error("⚠️ [المرحلة 3] لا توجد مجموعة حية تطابق هذه المواصفات في السحابة.")
            with st.form("create_new_group_form_v8"):
                st.markdown(f"<b style='color:#ef4444;'>📂 إدراج الهاتف وتأسيس وحجز مجموعة جديدة بالكامل في السحابة:</b>", unsafe_allow_html=True)
                st.info(f"المواصفات المحجوزة للمجموعة الجديدة: المقاس ({final_size}) | الشاشة ({final_panel}) | المستشعر ({final_sensor})")
                if st.form_submit_button("تأكيد حجز وإنشاء المجموعة الجديدة في السحابة 💾"):
                    if add_model(final_size, final_panel, final_sensor, current_search):
                        st.session_state.show_success_toast = f"تم تأسيس مجموعة فنية جديدة بنجاح وإدراج {current_search} كأول عضو ومؤسس لها!"
                        st.session_state.custom_search_input = ""
                        st.rerun()

# 🛠️ اللوحة الجانبية (المراقب الصامت وعين الحراسة الحية للمؤشرات)
with st.sidebar:
    st.markdown("<h2 style='text-align:right;color:#00bfff;'>🛠️ المراقب الصامت</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("⚙️ الإعدادات والمؤشرات الحية للسحابة", expanded=True):
        st.write(f"📅 تاريخ اليوم الفعلي: **{datetime.date.today()}**")
        st.metric(label="📈 إجمالي الهواتف السحابية الحية", value=total_models)
        st.metric(label="⚠️ المجموعات الفارغة المحذوفة", value=empty_groups_count)
        
        if st.button("🧹 تشغيل الصيانة وتطهير السحابة"):
            cleaned_db, changes_made = run_intelligent_inspector(db_data)
            if changes_made:
                st.session_state.show_success_toast = "قام المراقب الصامت بمسح التكرارات وتطهير السحابة بنجاح حاسم! 🧹"
                st.rerun()
            else:
                st.toast("🎯 فحص المراقب الصامت: قاعدة البيانات السحابية نظيفة ومؤمنة تماماً ولا توجد بيانات تالفة.")

