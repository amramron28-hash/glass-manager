import streamlit as st
import os
import base64

def inject_pwa_and_styles():
    """حقن ملف الـ Manifest لمعايير الـ PWA ومعالجة خلفية شاشة الهاتف الديناميكية"""
    st.markdown("""
    <head>
        <link rel="manifest" href="./manifest.json">
    </head>
    """, unsafe_allow_html=True)

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

    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def draw_technical_coords(size_grp, panel_grp, sensor_grp):
    """رسم وإظهار بطاقة تحليل الإحداثيات الفنية التتابعية"""
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

def draw_neon_cards(compatibles, current_search):
    """توليد بطاقات النيون الفاخرة للهواتف البديلة المطابقة مع تمييز الهاتف الحالي"""
    st.markdown(f"<h4 style='text-align:right;color:#e2e8f0; margin-bottom: 15px;'>📱 الهواتف المطابقة تماماً لنفس زجاج حماية الشاشة بالمحل ({len(compatibles)}):</h4>", unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, comp_model in enumerate(compatibles):
        with cols[idx % 4]:
            if comp_model.lower().strip() == current_search.lower().strip():
                st.markdown(f"<div style='background: linear-gradient(135deg, #0f172a, #1e293b); color: #00bfff; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; border: 2px solid #00bfff; box-shadow: 0px 0px 12px rgba(0, 191, 255, 0.5); margin-bottom: 12px;'>⭐ {comp_model}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background: linear-gradient(135deg, #1e293b, #0f172a); color: #e2e8f0; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #475569; margin-bottom: 12px;'>🔹 {comp_model}</div>", unsafe_allow_html=True)
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

# استيراد أدوات الواجهة الفاخرة من الملف الأول كليا
from components import inject_pwa_and_styles, draw_technical_coords, draw_neon_cards

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# تفعيل الهوية البصرية من مكونات الواجهة فوراً
inject_pwa_and_styles()

# قراءة قاعدة البيانات وتحليل المجموعات والبراندات
db_data = load_db()
all_flat_models, all_available_sizes, all_available_panels = [], [], []
total_models, empty_groups_count = 0, 0
brand_counts = {}

for size, panels in db_data.items():
    all_available_sizes.append(size.strip())
    size_has_models = False
    for panel, sensors in panels.items():
        if panel.strip() not in all_available_panels: 
            all_available_panels.append(panel.strip())
        for sensor, s_data in sensors.items():
            models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
            if models_list:
                size_has_models = True
                total_models += len(models_list)
                for model in models_list:
                    all_flat_models.append(model.strip())
                    first_word = model.split()[0] if model.split() else "Unknown"
                    brand_counts[first_word] = brand_counts.get(first_word, 0) + 1
    if not size_has_models: 
        empty_groups_count += 1

unique_models = sorted(list(set(all_flat_models)))

# دالة الفلترة والـ Callback لتصحيح الأخطاء اللحظية ومنع فراغات اللمس المزعجة
def search_models_callback(search_term: str):
    # حماية من الفراغات والمسافات العشوائية: إذا كان فارغاً تماماً لن تفتح الستارة المنسدلة نهائياً
    if not search_term or not search_term.strip(): 
        return []
    
    # تنظيف الحقل المكتوب فورياً
    search_normalized = normalize_text(search_term.strip().lower())
    fuzzy_results = process.extract(search_normalized, unique_models, scorer=fuzz.WRatio, limit=8)
    return [match for match, score, _ in fuzzy_results if score > 60]

# ==========================================
# 🛠️ اللوحة الجانبية (المراقب الصامت)
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
# 📱 واجهة التطبيق النظيفة وسيناريوهات الفحص والربط (1، 2، 3)
# ==========================================
st.markdown("<h1 style='text-align:center;color:#00bfff; font-weight: bold; margin-bottom: 25px;'>🔍 ZEGAAR AMMAR GLASS MANAGER</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if "custom_search_input" not in st.session_state: 
    st.session_state.custom_search_input = ""

# شريط البحث النظيف والوحيد في منتصف التطبيق
selected_phone = st_searchbox(
    search_function=search_models_callback,
    placeholder="🔍 ادخل اسم هاتف الزبون هنا لفحص التوافق والمجموعات الحية...",
    key="phone_search_autocomplete",
    label_visibility="collapsed"
)

# تنظيف وتخزين النص المختار في الجلسة بدون مسافات طرفية مشوهة
if selected_phone: 
    st.session_state.custom_search_input = selected_phone.strip()

# تشغيل سيناريوهات خطة العمل التتابعية (1، 2، 3)
if st.session_state.custom_search_input:
    current_search = st.session_state.custom_search_input
    coords = find_model_coords(db_data, current_search)
    
    # 🌟 السيناريو 1: وجد اسم الهاتف مسبقاً وتظهر النتائج كشلال تتابعي فوري
    if coords:
        size_grp, panel_grp, sensor_grp = coords
        compatibles = get_compatibles_strict(db_data, size_grp, panel_grp, sensor_grp)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.success(f"🎯 الموديل [{current_search}] مسجل ومتوافق حالياً!")
        
        # استدعاء وبناء كروت المظهر من الملف الأول التابع للتقسيم
        draw_technical_coords(size_grp, panel_grp, sensor_grp)
        draw_neon_cards(compatibles, current_search)

    # 🌟 السيناريو 2 + 3: لم يجد الهاتف نهائياً -> تفتح نافذة الربط والتأسيس السحابي الديناميكي
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"⚠️ الموديل [{current_search}] غير مسجل في أي مجموعة حالياً داخل الـ JSON.")
        
        with st.form("dynamic_routing_form", clear_on_submit=False):
            st.markdown("<p style='text-align:right; color:#a0aec0;'>عينك ويدك الذكية: يرجى تحديد أبعاد زجاج شاشة هاتف الزبون للبدء في دمجه برمجياً:</p>", unsafe_allow_html=True)
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1: input_size = st.text_input("📏 مقاس الهاتف الفعلي الحركي (Size Group):")
            with col_in2: input_panel = st.text_input("📺 نوع حماية الشاشة وعتبة الانحناء (Flat / Curved):")
            with col_in3: input_sensor = st.text_input("👁️ مستشعر التقارب والقطع (Sensor):")
            
            if st.form_submit_button("⚡ تشغيل الفحص والمطابقة السحابية التلقائية"):
                # معالجة وتنظيف النصوص المدخلة من أي مسافات زائدة
                if input_size.strip() and input_panel.strip() and input_sensor.strip():
                    norm_model = normalize_text(current_search)
                    norm_size = normalize_text(input_size.strip())
                    norm_panel = normalize_text(input_panel.strip())
                    norm_sensor = normalize_text(input_sensor.strip())
                    
                    structure_exists = norm_size in db_data and (norm_panel in db_data[norm_size]) and (norm_sensor in db_data[norm_size][norm_panel])
                    
                    # 🧩 تابع للسيناريو 2: الأبعاد متوفرة مسبقاً، سنضيف هاتف الزبون لهذه المجموعة القائمة
                    if structure_exists:
                        target_node = db_data[norm_size][norm_panel][norm_sensor]
                        if isinstance(target_node, list): 
                            db_data[norm_size][norm_panel][norm_sensor] = {"models": target_node}
                        if norm_model not in db_data[norm_size][norm_panel][norm_sensor]["models"]:
                            db_data[norm_size][norm_panel][norm_sensor]["models"].append(norm_model)
                            save_db(db_data)
                            st.success(f"🎯 [السيناريو 2 تم]: تم دمج الموديل [{norm_model}] داخل شجرة الحماية بنجاح.")
                            st.rerun()
                    
                    # 🧩 تابع للسيناريو 3: تركيبة فنية ومقاس جديد كلياً على المحل، سنؤسس له مقاس ومجموعة جديدة بالـ JSON
                    else:
                        if norm_size not in db_data: db_data[norm_size] = {}
                        if norm_panel not in db_data[norm_size]: db_data[norm_size][norm_panel] = {}
                        db_data[norm_size][norm_panel][norm_sensor] = {"models": [norm_model]}
                        save_db(db_data)
                        st.success(f"✨ [السيناريو 3 تم]: تم تسجيل وتأسيس مجموعة مقاس جديدة كلياً باسم [{norm_size}] وحفظ هاتف الزبون!")
                        st.rerun()
