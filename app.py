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

# حقن كود التنسيق المطور لجعل صندوق الإدخال زجاجياً شفافاً والكتابة لأقصى اليسار
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
    direction: ltr !important; /* اتجاه لليسار */
}

/* ⬅️ إجبار المؤشر والنص المكتوب بداخل شريط البحث على البقاء في أقصى اليسار */
div[data-baseweb="input"] input {
    color: #ffffff !important;
    background-color: transparent !important;
    font-size: 16px !important;
    text-align: left !important; /* محاذاة لليسار */
    direction: ltr !important;
}

div[data-baseweb="input"] input::placeholder {
    text-align: left !important;
    direction: ltr !important;
}

div[data-baseweb="input"]:focus-within {
    border: 1px solid #00bfff !important;
    box-shadow: 0 0 15px rgba(0, 191, 255, 0.4) !important;
}

/* ⬅️ إجبار نصوص بطاقات النتائج العريضة على المحاذاة لأقصى اليسار */
.full-width-card {
    text-align: left !important;
    padding-left: 20px !important;
}
</style>
""", unsafe_allow_html=True)

render_app_header()

# 2. تحميل شجرة البيانات وفهرسة الموديلات بالـ RAM
db_data = load_db()
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
# 🔍 4. Zegaarammar glass manger Autocomplete API (تفعيل الإكمال التلقائي حياً)
# ==============================================================================
if "search_input_val" not in st.session_state:
    st.session_state["search_input_val"] = ""

if "final_search_term" not in st.session_state:
    st.session_state["final_search_term"] = ""

if "show_workflow_box" not in st.session_state:
    st.session_state["show_workflow_box"] = False

search_query = st.text_input(
    "🔍 Search target phone model to begin inspection:",
    value=st.session_state["search_input_val"],
    key="pure_automated_search_input"
)

st.session_state["search_input_val"] = search_query

# 🚀 تفعيل التنبؤ حياً: الاقتراحات تظهر فوراً وتتحدث تلقائياً مع كل حرف تكتبه
if search_query.strip() and len(search_query.strip()) >= 2:
    # جلب الهواتف المتطابقة من قاعدة البيانات في الرام
    filtered_suggestions = [m for m in all_registered_models if search_query.lower() in m.lower()][:4]
    
    if filtered_suggestions:
        st.markdown("<p style='text-align:left;color:#00bfff;font-size:14px;margin-bottom:2px;direction:ltr;'>💡 Autocomplete Suggestions:</p>", unsafe_allow_html=True)
        cols = st.columns(len(filtered_suggestions))
        for idx, suggested_name in enumerate(filtered_suggestions):
            with cols[idx]:
                if st.button(f"📱 {suggested_name}", key=f"sug_{idx}", use_container_width=True):
                    st.session_state["search_input_val"] = suggested_name
                    st.session_state["final_search_term"] = suggested_name
                    st.session_state["show_workflow_box"] = False
                    st.rerun()

    if st.button(f"🚀 Inspect Model: {search_query}", type="primary", use_container_width=True):
        st.session_state["final_search_term"] = search_query.strip()
        st.session_state["show_workflow_box"] = False

final_search_term = st.session_state["final_search_term"]
show_workflow_box = st.session_state["show_workflow_box"]
# ==========================================
# ⚙️ 5. محرك التوجيه الصارم والتحكم بالنوافذ والخطط الذكية
# ==========================================
if final_search_term and not show_workflow_box:
    
    size_str, panel, sensor, real_name = find_model_coords(data_cluster, final_search_term)
    
    # 🟢 [الخطة أ]: الهاتف مدرج مسبقاً وتفجر البطاقات العريضة فوراً لليسار
    if size_str and normalize_text(real_name) == normalize_text(final_search_term):
        st.markdown(f"### 📊 Inspection Results for: `{real_name}`")
        
        results = get_compatibles_strict(data_cluster, real_name)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📐 Current Size:** {results['current_model']['size']}")
            st.markdown(f"**🖥️ Panel Type:** {results['current_model']['panel']}")
        with col2:
            st.markdown(f"**👁️ Proximity Sensor:** {results['current_model']['sensor']}")
            
        st.markdown("---")
        display_full_width_cards(results)
        
    else:
        is_typing = any(m.lower().startswith(final_search_term.lower()) for m in all_registered_models)
        
        if is_typing:
            st.caption("⚡ Typing... please complete the name or choose a suggestion above...")
        else:
            # 🔴 انقطعت سبل البحث [الخطة ج]: تنبثق حقول معالج الإدخال تلقائياً
            st.error(f"🚨 Model (`{final_search_term}`) is new and not registered in the database.")
            st.markdown("### 📝 [Plan C]: Insert New Model Specifications:")
            st.session_state["show_workflow_box"] = True
            st.rerun()

# ===== [الخطة ج]: واجهة إدخال هاتف جديد وفحص المقاسات المتقاطعة (الخطة ب) =====
if show_workflow_box:
    inserted_name = st.text_input(
        "Target Phone Model Name:",
        value=final_search_term,
        key="workflow_new_name"
    )
    
    col_s, col_p, col_se = st.columns(3)
    with col_s:
        new_size = st.text_input("📐 Digital Screen Size (e.g., 6.67):", key="workflow_size")
    with col_p:
        new_panel = st.selectbox("🖥️ Structural Screen Type:", ["Notch Screen", "Punch-Hole Screen"], key="workflow_panel")
    with col_se = st.selectbox("👁️ Detected Proximity Sensor:", ["virtual_proximity_sensor", "hardware_proximity_sensor", "hardware_top_sensor", "under_display_fingerprint"], key="workflow_sensor")
    
    # ⚙️ [خيار Auto مفعّل]: فحص وعرض المقاسات المتقاطعة حياً بمجرد إدخال المقاس تلقائياً
    if new_size and new_size.strip() != "":
        size_clean = new_size.strip()
        panel_clean = new_panel
        
        # 🔵 [الخطة ب التلقائية]: استدعاء الفحص والمطابقة الحية للمقاس بدون الحاجة لضغط زر
        matched_list = check_existing_size_group(data_cluster, size_clean, panel_clean)
        st.markdown("---")
        
        if matched_list:
            st.info("💡 **[Plan B Auto-Activated]**: Compatible model group detected in system for this size!")
            st.markdown(f"🎯 **Alternative compatible models available:** {', '.join(matched_list)}")
        else:
            st.warning("🎯 **[Full Plan C]**: This size is unique and independent. No matching size family found.")
            
        # ==========================================
        # 🚀 زر الحفظ السحابي النهائي والتأكيدي
        # ==========================================
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"💾 Save {inserted_name} Permanently to GitHub Cloud", type="primary", use_container_width=True):
            
            if size_clean not in data_cluster:
                data_cluster[size_clean] = {}
            if panel_clean not in data_cluster[size_clean]:
                data_cluster[size_clean][panel_clean] = {}
            if new_sensor not in data_cluster[size_clean][panel_clean]:
                data_cluster[size_clean][panel_clean][new_sensor] = []
                
            if inserted_name.strip() not in data_cluster[size_clean][panel_clean][new_sensor]:
                data_cluster[size_clean][panel_clean][new_sensor].append(inserted_name.strip())
                
                db_data["data"] = data_cluster
                
                if save_db(db_data):
                    st.success(f"✨ Successfully added `{inserted_name}` and synced with GitHub database!")
                    st.session_state["search_input_val"] = ""
                    st.session_state["final_search_term"] = ""
                    st.session_state["show_workflow_box"] = False
                    st.rerun()
                else:
                    st.error("❌ Cloud sync failed. Please verify your GITHUB_TOKEN settings.")
            else:
                st.info("📋 This model is already registered with the same specs.")
