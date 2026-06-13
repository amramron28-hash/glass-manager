import streamlit as st
from database import load_db, save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)
from streamlit_searchbox import st_searchbox
from rapidfuzz import process, fuzz

# استيراد أدوات الواجهة الفاخرة من ملف ui_components المعتمد بجيتهاب كلياً
from ui_components import inject_pwa_and_styles, render_top_bar, draw_technical_coords, draw_neon_section
# استيراد محرك جرد البيانات والتهيئة من الجزء الأول
from app_init import initialize_system_data

st.set_page_config(layout="wide", page_title="ZEGAAR AMMAR GLASS MANAGER", page_icon="🔍")

# تفعيل الهوية البصرية وحقن الـ CSS فوراً لشاشة الهاتف
inject_pwa_and_styles()

# استدعاء بيانات الجرد والتهيئة الحية من الجزء الأول
db_data, unique_models, total_models, empty_groups_count, brand_counts = initialize_system_data()

# دالة الفلترة الذكية لمنع فراغات اللمس ومطابقة الأخطاء الإملائية والكلمات الناقصة حياً
def search_models_callback(search_term: str):
    if not search_term or not search_term.strip(): 
        return []
    search_normalized = normalize_text(search_term.strip().lower())
    fuzzy_results = process.extract(search_normalized, unique_models, scorer=fuzz.WRatio, limit=8)
    return [match for match, score, _ in fuzzy_results if score > 60]

# ==========================================
# 🛠️ اللوحة الجانبية الإحصائية
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:right;color:#00bfff;'>🛠️ لوحة التحكم الجانبية</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("⚙️ إحصائيات البراندات الحية بالـ RAM", expanded=True):
        if brand_counts:
            for b_name, b_count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:4]:
                percentage = round((b_count / total_models) * 100, 1) if total_models > 0 else 0
                st.markdown(f"<p style='text-align:right;margin-bottom:2px;'>📋 <b>{b_name}</b>: {b_count} ({percentage}%)</p>", unsafe_allow_html=True)
                st.progress(percentage / 100)
        st.markdown("---")
        if empty_groups_count > 0: 
            st.warning(f"⚠️ مجموعات فارغة بالشجرة: {empty_groups_count}")
        else: 
            st.success("🎯 فحص سليم: لا توجد مجموعات ميتة.")

# ==========================================
# 📱 واجهة خطة العمل التتابعية النظيفة (أ، ب، ج)
# ==========================================

# 1. استدعاء شريط الأدوات الزجاجي المدمج في أعلى الصفحة (الإشعارات والترس) ليعتمد على الـ RAM
render_top_bar(db_data, total_models)

st.markdown("<h1 style='text-align:center;color:#00bfff; font-weight: bold; margin-top: 10px;'>🔍 ZEGAAR AMMAR GLASS MANAGER</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if "custom_search_input" not in st.session_state: 
    st.session_state.custom_search_input = ""

# 🏁 [الواجهة أ]: الشاشة بيضاء ونظيفة تماماً.. شريط البحث فقط في منتصف التطبيق
selected_phone = st_searchbox(
    search_function=search_models_callback,
    placeholder="🔍 ادخل اسم هاتف الزبون هنا لفحص التوافق والمجموعات الحية...",
    key="phone_search_autocomplete", label_visibility="collapsed"
)

if selected_phone: 
    st.session_state.custom_search_input = selected_phone.strip()

# تشغيل سيناريوهات خطة عمل المحل الذكية (1، 2، 3) تتابعياً بناءً على إدخال الفني
if st.session_state.custom_search_input:
    current_search = st.session_state.custom_search_input
    
    # تفكيك 4 قيم صافية ليتطابق هندسياً مع الـ logic_engine كليا ويمنع توقف الخادم
    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(db_data, current_search)
    
    # 🌟 السيناريو 1: الموديل موجود مسبقاً في مجموعات الحماية المخزنة بالـ JSON
    if size_grp:
        # جلب قاموس التوافق المتشعب والذكي الحسابي
        compat_results = get_compatibles_strict(db_data, current_search)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.success(f"🎯 الموديل [{real_name}] مسجل ومتوافق حياً!")
        
        # 📋 [الواجهة ب]: انبثاق كرت الأبعاد الفنية التوافقية لهاتف الزبون
        draw_technical_coords(size_grp, panel_grp, sensor_grp)
        
        # 📱 [الواجهة ج]: فتح بطاقات النيون الفاخرة الملونة وتوزيعها جينياً حسب نوع التوافق وعزل الحساسات
        draw_neon_section("مطابقة للمقاس تماماً (Exact Matches)", compat_results["exact"], "#00bfff", "🎯", current_search)
        draw_neon_section("أكبر بقليل بمقدار 0.01 إلى 0.03 (Plus Sizes)", compat_results["plus"], "#10b981", "➕", current_search)
        draw_neon_section("أصغر بقليل بمقدار 0.01 إلى 0.03 (Minus Sizes)", compat_results["minus"], "#f59e0b", "➖", current_search)
        draw_neon_section("نفس المقاس ولكن مستشعر مختلف - انتبه! (Warning)", compat_results["warn"], "#ef4444", "⚠️", current_search)
        
    # 🌟 السيناريو 2 + 3: الهاتف غير مسجل نهائياً -> تفتح تلقائياً نافذة الربط والتأسيس السحابي
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"⚠️ الموديل [{current_search}] غير مسجل في أي مجموعة حالياً داخل النظام.")
        
        with st.form("dynamic_routing_form", clear_on_submit=False):
            st.markdown("<p style='text-align:right; color:#a0aec0;'>يرجى تحديد مواصفات زجاج شاشة هاتف الزبون الممسوك بيدك ليقوم السيستم بتصنيفه تلقائياً:</p>", unsafe_allow_html=True)
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
                    
                    # 🧩 تابع للسيناريو 2: الأبعاد متوفرة مسبقاً، سنضيف هاتف الزبون لهذه المجموعة القائمة فوراً
                    if structure_exists:
                        target_node = db_data[norm_size][norm_panel][norm_sensor]
                        if isinstance(target_node, list): db_data[norm_size][norm_panel][norm_sensor] = {"models": target_node}
                        if norm_model not in db_data[norm_size][norm_panel][norm_sensor]["models"]:
                            db_data[norm_size][norm_panel][norm_sensor]["models"].append(norm_model)
                            save_db(db_data)
                            st.success(f"🎯 [السيناريو 2 تم]: تم دمج الموديل الجديد [{norm_model}] داخل شجرة الحماية بنجاح.")
                            st.rerun()
                    
                    # 🧩 تابع للسيناريو 3: تركيبة فنية ومقاس جديد كلياً، سنؤسس له مقاس ومجموعة جديدة بالـ JSON تلقائياً
                    else:
                        if norm_size not in db_data: db_data[norm_size] = {}
                        if norm_panel not in db_data[norm_size]: db_data[norm_size][norm_panel] = {}
                        db_data[norm_size][norm_panel][norm_sensor] = {"models": [norm_model]}
                        save_db(db_data)
                        st.success(f"✨ [السيناريو 3 تم]: تم تسجيل وتأسيس مجموعة مقاس جديدة كلياً باسم [{norm_size}] وحفظ الهاتف كأول عنصر لها!")
                        st.rerun()
