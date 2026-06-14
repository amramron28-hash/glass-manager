import streamlit as st
import datetime
from database import load_db, save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)
from streamlit_searchbox import st_searchbox
from rapidfuzz import process, fuzz

# استيراد الأدوات المحدثة كلياً للأصالة البصرية
from ui_components import inject_pwa_and_styles, draw_technical_coords, draw_neon_section
from app_init import initialize_system_data

st.set_page_config(layout="wide", page_title="ZEGAAR AMMAR GLASS MANAGER", page_icon="🔍")

# تفعيل الهوية البصرية الأصلية الممتدة بكامل تفاصيل زجاج الخلفية
inject_pwa_and_styles()

# استدعاء بيانات الجرد السحابي وتغذية الـ RAM من الجزء الأول
db_data, unique_models, total_models, empty_groups_count, brand_counts = initialize_system_data()

def search_models_callback(search_term: str, **kwargs):
    """المراقب الصامت: تأمين كامل للمدخلات بـ **kwargs لابتلاع أي معاملات زائدة ومنع الـ TypeError"""
    if not search_term or not search_term.strip(): 
        return []
    search_normalized = normalize_text(search_term.strip().lower())
    fuzzy_results = process.extract(search_normalized, unique_models, scorer=fuzz.WRatio, limit=8)
    return [match for match, score, _ in fuzzy_results if score > 60]

# ==========================================
# 🛠️ اللوحة الجانبية (غرفة عمليات المراقب الصامت)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:right;color:#00bfff;'>🛠️ المراقب الصامت</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.expander("🔔 جرس الإشعارات اللحظي", expanded=True):
        st.info("💡 النظام سحابي مستقر 100% والبحث اللحظي الخارق نشط.")
    
    with st.expander("⚙️ الإعدادات والتحكم بالـ RAM", expanded=True):
        st.write(f"📅 تاريخ اليوم الفني: **{datetime.date.today().strftime('%Y-%m-%d')}**")
        st.metric(label="📈 إجمالي الهواتف بالسيستم", value=total_models)
        st.markdown("---")
        if brand_counts:
            for b_name, b_count in sorted(brand_counts.items(), key=lambda x: x, reverse=True)[:4]:
                percentage = round((b_count / total_models) * 100, 1) if total_models > 0 else 0
                st.markdown(f"📋 <b>{b_name}</b>: {b_count} ({percentage}%)", unsafe_allow_html=True)
                st.progress(percentage / 100)
                
        st.markdown("---")
        if st.button("🧹 تشغيل الصيانة وتطهير الشجرة", key="sidebar_inspector_btn"):
            cleaned_db, changes_made = run_intelligent_inspector(db_data)
            if changes_made:
                save_db(cleaned_db)
                st.success("✨ تم تطهير الشجرة وترتيب الموديلات!")
                st.rerun()
            else:
                st.toast("🎯 السيستم نظيف ومطهر كلياً مسبقاً.")

# ==========================================
# 📱 واجهة خطة العمل التتابعية الموحدة النظيفة (أ، ب، ج)
# ==========================================

# العنوان الصافي الأصلي والفاخر وبدون أي علامات أو عدسات زائدة
st.markdown("""
<h1 style='text-align:center;color:#00bfff; font-weight: 900; letter-spacing: 1px; text-shadow: 0 0 10px rgba(0, 191, 255, 0.6);'>
    ZEGAAR AMMAR GLASS MANAGER
</h1>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if "custom_search_input" not in st.session_state: 
    st.session_state.custom_search_input = ""

# 🏁 [الواجهة أ]: نظافة مطلقة 100/100.. شريط البحث فقط يقف وحيداً في المنتصف
selected_phone = st_searchbox(
    search_function=search_models_callback,
    placeholder="🔍 ادخل اسم هاتف الزبون هنا لفحص التوافق والمجموعات الحية...",
    key="phone_search_autocomplete",
    label=""
)

if selected_phone: 
    st.session_state.custom_search_input = selected_phone.strip()

if st.session_state.custom_search_input:
    current_search = st.session_state.custom_search_input
    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(db_data, current_search)
    
    if size_grp:
        compat_results = get_compatibles_strict(db_data, current_search)
        st.markdown("<br>", unsafe_allow_html=True)
        st.success(f"🎯 الموديل [{real_name}] مسجل ومتوافق حياً!")
        
        # [الواجهة ب]: بطاقة تحليل الأبعاد الفنية التتابعية لهاتف الزبون
        draw_technical_coords(size_grp, panel_grp, sensor_grp)
        
        # [الواجهة ج]: بطاقات النيون الفاخرة الملونة الأربعة المقسمة وعزل الحساسات الأصلية العريضة
        draw_neon_section("مطابقة للمقاس تماماً (Exact Matches)", compat_results["exact"], "#2ecc71", "🎯", current_search)
        draw_neon_section("أكبر بقليل بمقدار 0.01 إلى 0.03 (Plus Sizes)", compat_results["plus"], "#3498db", "➕", current_search)
        draw_neon_section("أصغر بقليل بمقدار 0.01 إلى 0.03 (Minus Sizes)", compat_results["minus"], "#e67e22", "➖", current_search)
        draw_neon_section("نفس المقاس ولكن مستشعر مختلف - انتبه! (Warning)", compat_results["warn"], "#ef4444", "⚠️", current_search)
        
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"⚠️ الموديل [{current_search}] غير مسجل في أي مجموعة حالياً داخل النظام.")
        
        with st.form("dynamic_routing_form", clear_on_submit=False):
            st.markdown("<p style='text-align:right; color:#a0aec0;'>المراقب الصامت: يرجى تحديد أبعاد زجاج شاشة هاتف الزبون الممسوك بيدك ليقوم السيستم بتصنيفه تلقائياً:</p>", unsafe_allow_html=True)
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1: input_size = st.text_input("📏 مقاس الهاتف الصافي (مثال: 6.67):")
            with col_in2: input_panel = st.text_input("📺 نوع حماية الشاشة (Flat / Curved):")
            with col_in3: input_sensor = st.text_input("👁️ موقع مستشعر التقارب والقطع (Sensor):")
            
            if st.form_submit_button("⚡ تشغيل الفحص والمطابقة السحابية التلقائية"):
                if input_size.strip() and input_panel.strip() and input_sensor.strip():
                    norm_model = normalize_text(current_search)
                    norm_size = normalize_text(input_size.strip())
                    norm_panel = normalize_text(input_panel.strip())
                    norm_sensor = normalize_text(input_sensor.strip())
                    
                    structure_exists = norm_size in db_data and (norm_panel in db_data[norm_size]) and (norm_sensor in db_data[norm_size][norm_panel])
                    
                    if structure_exists:
                        target_node = db_data[norm_size][norm_panel][norm_sensor]
                        if isinstance(target_node, list): db_data[norm_size][norm_panel][norm_sensor] = {"models": target_node}
                        if norm_model not in db_data[norm_size][norm_panel][norm_sensor]["models"]:
                            db_data[norm_size][norm_panel][norm_sensor]["models"].append(norm_model)
                            save_db(db_data)
                            st.success(f"🎯 [السيناريو 2 تم]: تم دمج الموديل الجديد [{norm_model}] داخل شجرة الحماية بنجاح.")
                            st.rerun()
                    else:
                        if norm_size not in db_data: db_data[norm_size] = {}
                        if norm_panel not in db_data[norm_size]: db_data[norm_size][norm_panel] = {}
                        db_data[norm_size][norm_panel][norm_sensor] = {"models": [norm_model]}
                        save_db(db_data)
                        st.success(f"✨ [السيناريو 3 تم]: تم تسجيل وتأسيس مجموعة مقاس جديدة كلياً باسم [{norm_size}] وحفظ الهاتف!")
                        st.rerun()
