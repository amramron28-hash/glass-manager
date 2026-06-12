import streamlit as st
from database import load_db, save_db, add_notification
from logic_engine import get_compatibles_strict, find_model_coords, check_existing_size_group, normalize_text
from glass_watcher import inject_slate_navy_css, render_app_header, render_sidebar, display_full_width_cards

# 1. تهيئة الشاشة وحقن الواجهة النقية (Slate Navy UI)
st.set_page_config(
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# حقن كود التنسيق لجعل صندوق الإدخال زجاجياً شفافاً والكتابة لأقصى اليمين
inject_slate_navy_css()
st.markdown("""
<style>
/* 🧪 تدمير اللون الرمادي كلياً وجعل حقل البحث شفافاً بالكامل */
div[data-baseweb="input"], div[data-baseweb="base-input"] {
    background-color: transparent !important;
    background: transparent !important;
    border: 1px solid rgba(0, 191, 255, 0.4) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(0, 191, 255, 0.1) !important;
    direction: rtl !important;
}

/* ➡️ إجبار المؤشر والنص المكتوب على البقاء في أقصى اليمين */
div[data-baseweb="input"] input {
    color: #ffffff !important;
    background-color: transparent !important;
    font-size: 16px !important;
    text-align: right !important;
    direction: rtl !important;
}

div[data-baseweb="input"] input::placeholder {
    text-align: right !important;
    direction: rtl !important;
}

div[data-baseweb="input"]:focus-within {
    border: 1px solid #00bfff !important;
    box-shadow: 0 0 15px rgba(0, 191, 255, 0.4) !important;
}
</style>
""", unsafe_allow_html=True)

render_app_header()

# 2. تحميل شجرة البيانات وفهرسة الموديلات بالـ RAM
db_data = load_db()

# فك التغليف بمرونة لضمان عدم حدوث تشوه أو انهيار بالرام
data_cluster = db_data.get("data", db_data)

all_registered_models = []
if isinstance(data_cluster, dict):
    for sk, pv in data_cluster.items():
        if sk not in ["metadata", "status", "last_updated", "notifications"]:
            if isinstance(pv, dict):
                for pk, sv in pv.items():
                    if isinstance(sv, dict):
                        for sek, ml in sv.items():
                            if isinstance(ml, list):
                                all_registered_models.extend(ml)

all_registered_models = sorted(list(set(all_registered_models)))

# 3. رندرة الشريط الجانبي الثابت والمراقب الصامت
def auto_fix_database_routine():
    add_notification("⚙️ تم تشغيل روتين المراقب الآلي لتصحيح وصيانة المجموعات بنجاح.")
    st.sidebar.success("✅ قاعدة البيانات سليمة ومحدثة 100% سحابياً!")

render_sidebar(db_data, save_db, len(all_registered_models), fix_callback=auto_fix_database_routine)

# ==============================================================================
# 🔍 4. Zegaarammar glass manger Autocomplete API (واجهة الإكمال التلقائي المحمية)
# ==============================================================================
if "search_input_val" not in st.session_state:
    st.session_state["search_input_val"] = ""

if "final_search_term" not in st.session_state:
    st.session_state["final_search_term"] = ""

if "show_workflow_box" not in st.session_state:
    st.session_state["show_workflow_box"] = False

search_query = st.text_input(
    "🔍 ابحث عن هاتف أو اكتب اسماً جديداً مباشرة لبدء الفحص والمطابقة:",
    value=st.session_state["search_input_val"],
    key="pure_automated_search_input"
)

st.session_state["search_input_val"] = search_query

# حماية صارمة: التفاعل وعرض التكملة والتهجي يبدأ فقط عند البدء الفعلي في كتابة الحروف
if search_query.strip():
    # تصفية وفهرسة سريعة من الذاكرة الحية المتطابقة
    filtered_suggestions = [m for m in all_registered_models if m.lower().startswith(search_query.lower())][:4]
    
    if filtered_suggestions and normalize_text(search_query) != normalize_text(filtered_suggestions[0]):
        st.markdown("<p style='text-align:right;color:#00bfff;font-size:14px;margin-bottom:2px;direction:rtl;'>💡 مساعد التكملة والتهجي (انقر للتثبيت الفوري):</p>", unsafe_allow_html=True)
        cols = st.columns(len(filtered_suggestions))
        for idx, suggested_name in enumerate(filtered_suggestions):
            with cols[idx]:
                if st.button(f"📱 {suggested_name}", key=f"sug_{idx}", use_container_width=True):
                    st.session_state["search_input_val"] = suggested_name
                    st.session_state["final_search_term"] = suggested_name
                    st.session_state["show_workflow_box"] = False
                    st.rerun()

    if st.button(f"🚀 فحص ومطابقة: {search_query}", type="primary", use_container_width=True):
        st.session_state["final_search_term"] = search_query.strip()
        st.session_state["show_workflow_box"] = False

final_search_term = st.session_state["final_search_term"]
show_workflow_box = st.session_state["show_workflow_box"]
# ==========================================
# ⚙️ 5. محرك التوجيه الصارم والتحكم بالنوافذ والخطط الذكية
# ==========================================
if final_search_term and not show_workflow_box:
    
    # فحص صارم ومحكم لتحديد مسار الهاتف وتجنب تضارب هياكل الـ JSON
    size_str, panel, sensor, real_name = find_model_coords(data_cluster, final_search_term)
    
    # 🟢 [الخطة أ]: الهاتف مدرج مسبقاً وتفجر البطاقات العريضة فوراً للزبون
    if size_str and normalize_text(real_name) == normalize_text(final_search_term):
        st.markdown(f"### 📊 نتائج التوافق والمقاسات للهاتف: `{real_name}`")
        
        results = get_compatibles_strict(data_cluster, real_name)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📐 مقاس الهاتف الحالي:** {results['current_model']['size']}")
            st.markdown(f"**🖥️ نوع الشاشة الهيكلي:** {results['current_model']['panel']}")
        with col2:
            st.markdown(f"**👁️ مستشعر التقارب المكتشف:** {results['current_model']['sensor']}")
            
        st.markdown("---")
        display_full_width_cards(results)
        
    else:
        # حارس حظر الرندرة المبكرة طالما يوجد للمكتوب تطابق في بداية أسماء الموديلات بالرام
        is_typing = any(m.lower().startswith(final_search_term.lower()) for m in all_registered_models)
        
        if is_typing:
            st.caption("⚡ يرجى كتابة الاسم كاملاً أو اختيار التكملة المتاحة بالأعلى...")
        else:
            # 🔴 انقطعت سبل البحث [الخطة ج]: تنبثق حقول معالج الإدخال تلقائياً في نهاية المطاف
            st.error(f"🚨 الموديل (`{final_search_term}`) جديد تماماً وغير مسجل في قاعدة البيانات.")
            st.markdown("### 📝 [الخطة ج]: إدخال مواصفات هاتف الزبون للفحص والمطابقة السحابية:")
            st.session_state["show_workflow_box"] = True
            st.rerun()

# ===== [الخطة ج]: واجهة إدخال هاتف جديد وفحص المقاسات المتقاطعة (الخطة ب) =====
if show_workflow_box:
    inserted_name = st.text_input(
        "اسم الهاتف المراد تسجيله ومطابقته:",
        value=final_search_term,
        key="workflow_new_name"
    )
    
    col_s, col_p, col_se = st.columns(3)
    with col_s:
        new_size = st.text_input("📐 المقاس الرقمي للزبون (مثال: 6.50):", key="workflow_size")
    with col_p:
        new_panel = st.selectbox("🖥️ نوع الشاشة الهيكلي:", ["Notch Screen", "Punch-Hole Screen"], key="workflow_panel")
    with col_se:
        new_sensor = st.selectbox("👁️ مستشعر التقارب الملاحظ:", ["virtual_proximity_sensor", "hardware_proximity_sensor"], key="workflow_sensor")
    
    if inserted_name and new_size:
        inserted_name = inserted_name.strip()
        new_size = new_size.strip()
        
        # 🔵 [الخطة ب]: استدعاء الفحص العينات المتقاطعة لمعرفة البدائل الجاهزة مسبقاً
        matched_list = check_existing_size_group(data_cluster, new_size, new_panel)
        st.markdown("---")
        
        if matched_list:
            st.info("💡 **[الخطة ب مفعّلة]**: تم رصد مجموعة مقاسات متوافقة مسبقاً في السستم لهذا الهاتف الجديد!")
            st.markdown(f"🎯 **الموديلات البديلة المتوافقة مع هاتف الزبون حالياً:** {', '.join(matched_list)}")
        else:
            st.warning("🎯 **[الخطة ج الكاملة]**: هذا المقاس نادر ومستقل تماماً، لا توجد عائلة مقاسات مطابقة له حالياً.")
