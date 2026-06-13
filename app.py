hereimport streamlit as st, os, base64
from database import load_db, save_db
from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)
from streamlit_searchbox import st_searchbox
from rapidfuzz import process, fuzz

# ==========================================
# 📺 [الجزء 1]: هندسة واجهات المستخدم الرقمية (UI/UX)
# ==========================================

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# حقن ملف الـ Manifest برمجياً لتفعيل خاصية PWA والتثبيت الفوري
st.markdown("""
<head>
    <link rel="manifest" href="./manifest.json">
</head>
""", unsafe_allow_html=True)

# معالجة وحقن الخلفية الفاخرة المعتمدة بالـ RAM
bg_image_base64 = ""
if os.path.exists("phone_image.webp"):
    with open("phone_image.webp", "rb") as f:
        bg_image_base64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"],
[data-testid="stAppViewMain"],
.stApp,
.stMain,
main,
[data-testid="stApp"] {{
    background-image:
        linear-gradient(
            rgba(10,14,23,0.45),
            rgba(10,14,23,0.45)
        ),
        url('data:image/webp;base64,{bg_image_base64}') !important;

    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    background-color: transparent !important;
}}
</style>
""", unsafe_allow_html=True)

# تحميل ملف CSS الخارجي لتوحيد أبعاد الحقول
if os.path.exists("style.css"):
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ==========================================
# 💾 [الجزء 2]: جرد وتحليل شجرة البيانات سحابياً
# ==========================================

db_data = load_db()
all_flat_models, all_available_sizes, all_available_panels = [], [], []
total_models, empty_groups_count = 0, 0
brand_counts = {}

for size, panels in db_data.items():
    all_available_sizes.append(size)
    size_has_models = False
    for panel, sensors in panels.items():
        if panel not in all_available_panels: 
            all_available_panels.append(panel)
        for sensor, s_data in sensors.items():
            models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
            if models_list:
                size_has_models = True
                total_models += len(models_list)
                for model in models_list:
                    all_flat_models.append(model)
                    first_word = model.split()[0] if model.split() else "Unknown"
                    brand_counts[first_word] = brand_counts.get(first_word, 0) + 1
    if not size_has_models: 
        empty_groups_count += 1

unique_models = sorted(list(set(all_flat_models)))


# 🎯 دالة البحث والتصحيح اللحظي المعتمدة على استراتيجية (أ، ب، ج)
def search_models_callback(search_term: str):
    if not search_term or not search_term.strip(): 
        return []
    search_normalized = normalize_text(search_term.strip().lower())
    # استخدام خوارزمية RapidFuzz لتصحيح أخطاء إملاء الفني حياً وبسرعة فائقة
    fuzzy_results = process.extract(search_normalized, unique_models, scorer=fuzz.WRatio, limit=8)
    return [match for match, score, _ in fuzzy_results if score > 60]


# ==========================================
# 🛠️ [الجزء 3]: اللوحة الجانبية (المراقب الصامت)
# ==========================================

with st.sidebar:
    st.markdown("<h2 style='text-align:right;color:#00bfff;'>🛠️ لوحة التحكم الجانبية</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.expander("🔔 جرس الإشعارات اللحظي", expanded=False):
        st.info("💡 النظام الموحد المحدث نشط ومستقر سحابياً الآن 100% وبأعلى سرعة تصفح.")
        
    with st.expander("⚙️ إعدادات المراقب الصامت", expanded=True):
        st.metric(label="📈 إجمالي الهواتف بالسيستم", value=total_models)
        if brand_counts:
            for b_name, b_count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:4]:
                percentage = round((b_count / total_models) * 100, 1) if total_models > 0 else 0
                st.markdown(f"<p style='text-align:right;margin-bottom:2px;'>📋 <b>{b_name}</b>: {b_count} ({percentage}%)</p>", unsafe_allow_html=True)
                st.progress(percentage / 100)
        st.markdown("---")
        if empty_groups_count > 0: 
            st.warning(f"⚠️ رصد المراقب عدد ({empty_groups_count}) مجموعة فارغة.")
        else: 
            st.success("🎯 فحص سليم: لا توجد مجموعات ميتة بشجرة البيانات.")
            
        if st.button("🧹 تشغيل الصيانة الفورية وتطهير الشجرة", key="sidebar_inspector_btn"):
            cleaned_db, changes_made = run_intelligent_inspector(db_data)
            final_cleaned = {k: v for k, v in cleaned_db.items() if v}
            if len(final_cleaned) != len(db_data) or changes_made:
                save_db(final_cleaned)
                st.success("✨ تم تطهير الشجرة سحابياً وإعادة ترتيب الموديلات حياً!")
                st.rerun()


# ==========================================
# 📱 [الجزء 4]: الواجهة النظيفة وسيناريوهات الفحص والربط (1، 2، 3)
# ==========================================

st.markdown("<h1 style='text-align:center;color:#00bfff; font-weight: bold; margin-bottom: 25px;'>🔍 ZEGAAR AMMAR GLASS MANAGER</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if "custom_search_input" not in st.session_state: 
    st.session_state.custom_search_input = ""

# الشاشة تفتح نظيفة تماماً: لا يوجد بها سوى شريط البحث الموحد والذكي في المنتصف
selected_phone = st_searchbox(
    search_function=search_models_callback,
    placeholder="🔍 ادخل اسم هاتف الزبون هنا لفحص التوافق والمجموعات الحية...",
    key="phone_search_autocomplete",
    label_visibility="collapsed"
)

if selected_phone: 
    st.session_state.custom_search_input = selected_phone

# معالجة تفريغ وتدفق الخطط الثلاث المترابطة حركياً بناءً على إدخال الفني
if st.session_state.custom_search_input:
    current_search = st.session_state.custom_search_input
    coords = find_model_coords(db_data, current_search)
    
    # 🌟 السيناريو 1: وجد ما يطابقه بنجاح في مجموعات الحماية المخزنة مسبقاً
    if coords:
        size_grp, panel_grp, sensor_grp = coords
        compatibles = get_compatibles_strict(db_data, size_grp, panel_grp, sensor_grp)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.success(f"🎯 الموديل [{current_search}] مسجل ومتوافق حالياً!")
        
        # تظهر نافذة المواصفات الفنية كرت تفصيلي تتابعي
        st.markdown(f"""
            <div style='background: rgba(15, 23, 42, 0.6); padding: 20px; border-radius: 12px; border: 1px dashed #00bfff; margin-bottom: 25px;'>
                <h4 style='text-align:center; color:#00bfff; margin-top:0;'>📋 الإحداثيات الفنية التوافقية للمجموعة</h4>
                <div style='display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center;'>
                    <div><p style='color:#a0aec0; margin-bottom:5px;'>📏 مقاس الحماية</p><h5 style='color:#fff; margin-top:0;'>{size_grp}</h5></div>
                    <div><p style='color:#a0aec0; margin-bottom:5px;'>📺 بنية الشاشة</p><h5 style='color:#fff; margin-top:0;'>{panel_grp}</h5></div>
                    <div><p style='color:#a0aec0; margin-bottom:5px;'>👁️ مستشعر التقارب</p><h5 style='color:#fff; margin-top:0;'>{sensor_grp}</h5></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # تظهر نافذة عرض بطاقات النيون الملونة للهواتف البديلة المطابقة كلياً
        st.markdown(f"<h4 style='text-align:right;color:#e2e8f0; margin-bottom: 15px;'>📱 الهواتف المطابقة تماماً لنفس زجاج حماية الشاشة بالمحل ({len(compatibles)}):</h4>", unsafe_allow_html=True)
        cols = st.columns(4)
        for idx, comp_model in enumerate(compatibles):
            with cols[idx % 4]:
                if comp_model.lower() == current_search.lower():
                    st.markdown(f"<div style='background: linear-gradient(135deg, #0f172a, #1e293b); color: #00bfff; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; border: 2px solid #00bfff; box-shadow: 0px 0px 12px rgba(0, 191, 255, 0.5); margin-bottom: 12px;'>⭐ {comp_model}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background: linear-gradient(135deg, #1e293b, #0f172a); color: #e2e8f0; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #475569; margin-bottom: 12px;'>🔹 {comp_model}</div>", unsafe_allow_html=True)

    # 🌟 السيناريو 2 + 3: لم يجد الهاتف نهائياً -> تفتح نافذة الربط والتأسيس السحابي الديناميكي
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"⚠️ الموديل [{current_search}] غير مسجل في أي مجموعة حالياً داخل الـ JSON.")
        
        with st.form("dynamic_routing_form", clear_on_submit=False):
            st.markdown("<p style='text-align:right; color:#a0aec0;'>عينك ويدك الذكية: يرجى تحديد أبعاد زجاج شاشة هاتف الزبون للبدء في دمجه برمجياً:</p>", unsafe_allow_html=True)
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1: 
                input_size = st.text_input("📏 مقاس الهاتف الفعلي الحركي (Size Group):")
            with col_in2: 
                input_panel = st.text_input("📺 نوع حماية الشاشة وعتبة الانحناء (Flat / Curved):")
            with col_in3: 
                input_sensor = st.text_input("👁️ موقع مستشعر التقارب والقطع (Sensor):")
            
            if st.form_submit_button("⚡ تشغيل الفحص والمطابقة السحابية التلقائية"):
                if input_size and input_panel and input_sensor:
                    norm_model = normalize_text(current_search)
                    norm_size = normalize_text(input_size)
                    norm_panel = normalize_text(input_panel)
                    norm_sensor = normalize_text(input_sensor)
