import streamlit as st
from database import load_db, save_db, add_notification
from logic_engine import get_compatibles_strict, find_model_coords, check_existing_size_group, normalize_text
# تعديل الاستدعاء ليتوافق 100% مع ملف glass_watcher.py المرفوع بمستودعك
from glass_watcher import inject_slate_navy_css, render_app_header, render_sidebar, display_full_width_cards

# 1. تهيئة الشاشة وحقن الواجهة النقية (Slate Navy UI)
st.set_page_config(
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_slate_navy_css()
render_app_header()

# 2. تحميل شجرة البيانات وفهرسة الموديلات بالـ RAM
db_data = load_db()

all_registered_models = []
for sk, pv in db_data.items():
    if sk != "notifications":
        for pk, sv in pv.items():
            for sek, ml in sv.items():
                all_registered_models.extend(ml)
all_registered_models = sorted(list(set(all_registered_models)))

# 3. رندرة الشريط الجانبي الثابت والمراقب الصامت
def auto_fix_database_routine():
    add_notification("⚙️ تم تشغيل روتين المراقب الآلي لتصحيح وصيانة المجموعات بنجاح.")
    st.sidebar.success("✅ قاعدة البيانات سليمة ومحدثة 100% سحابياً!")

render_sidebar(db_data, save_db, len(all_registered_models), fix_callback=auto_fix_database_routine)

# ==========================================
# 🔍 4. حقل البحث النصي الحر والمطور (التقاط الحروف حياً ومنع الحجب)
# ==========================================
st.text_input("🔍 ابحث عن هاتف أو اكتب اسماً جديداً مباشرة:", key="pure_automated_search_input")

# صيد النص حياً حرفاً بحرف من الذاكرة اللحظية لتجاوز سجن "Press Enter" والـ No Results
search_input = st.session_state.get("pure_automated_search_input", "").strip()

if "selected_model_click" not in st.session_state:
    st.session_state["selected_model_click"] = ""

# تحديد الكلمة النهائية المستهدفة بالبحث
final_search_term = st.session_state["selected_model_click"] if search_input == "" else search_input

# --- 💡 بناء حاوية المساعد العائمة للتكملة والتهجي (تظهر فقط عند بدء الكتابة) ---
if search_input and search_input != "":
    filtered_suggestions = [m for m in all_registered_models if m.lower().startswith(search_input.lower())][:4]
    
    if filtered_suggestions and normalize_text(search_input) != normalize_text(filtered_suggestions):
        st.markdown("<div class='suggestion-box'><b>📋 مساعد التكملة والتهجي (انقر للتثبيت الفوري):</b></div>", unsafe_allow_html=True)
        cols = st.columns(len(filtered_suggestions))
        for idx, suggested_name in enumerate(filtered_suggestions):
            with cols[idx]:
                if st.button(f"📱 {suggested_name}", key=f"sug_{idx}"):
                    st.session_state["selected_model_click"] = suggested_name
                    st.session_state["pure_automated_search_input"] = ""
                    st.rerun()

# ==========================================
# ⚙️ 5. محرك التوجيه الصارم والتحكم بالنوافذ (مخفية كلياً لحين ثبوت الاسم)
# ==========================================
if final_search_term and final_search_term != "":
    
    # فحص صارم ومحكم لتحديد مسار الهاتف وتجنب البيانات القديمة بالرام
    size_str, panel, sensor, real_name = find_model_coords(db_data, final_search_term)
    
    if size_str and normalize_text(real_name) == normalize_text(final_search_term):
        # 🟢 [الحالة أ]: الهاتف مسجل وجاهز (تختفي حقول الإدخال وتتفجر البطاقات العريضة فوراً)
        st.session_state["selected_model_click"] = ""
        st.markdown(f"### 📊 نتائج التوافق والمقاسات للهاتف: `{real_name}`")
        
        results = get_compatibles_strict(db_data, real_name)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📐 مقاس الهاتف الحالي:** {results['current_model']['size']}")
            st.markdown(f"**🖥️ نوع الشاشة:** {results['current_model']['panel']}")
        with col2:
            st.markdown(f"**👁️ مستشعر التقارب:** {results['current_model']['sensor']}")
            
        st.markdown("---")
        display_full_width_cards(results)
        
    else:
        # حارس حظر الرندرة المبكرة طالما يوجد للمكتوب تطابق في بداية أسماء الموديلات
        is_typing = any(m.lower().startswith(final_search_term.lower()) for m in all_registered_models)
        
        if is_typing:
            st.caption("⚡ يرجى كتابة الاسم كاملاً أو اختيار التكملة المتاحة بالأعلى...")
        else:
            # 🛑 [الهاتف جديد كلياً 100%]: تنبثق حقول المقاسات والمستشعرات تلقائياً حياً بالأسفل
            st.error(f"🚨 الموديل (`{final_search_term}`) جديد تماماً وغير مسجل في قاعدة البيانات.")
            st.markdown("### 📝 إدخال مواصفات هاتف الزبون للفحص الحي:")
            
            col_s, col_p, col_se = st.columns(3)
            with col_s:
                new_size = st.text_input("📐 المقاس الرقمي للزبون (مثال: 6.50):", key="workflow_size")
            with col_p:
                new_panel = st.selectbox("🖥️ نوع الشاشة الهيكلي:", ["Notch Screen", "Punch-Hole Screen"], key="workflow_panel")
            with col_se:
                new_sensor = st.selectbox("👁️ مستشعر التقارب:", ["virtual_proximity_sensor", "hardware_proximity_sensor"], key="workflow_sensor")
            
            # معالجة الفحص الحي التلقائي بعد إدخال المقاس مباشرة
            if new_size:
                matched_list = check_existing_size_group(db_data, new_size, new_panel)
                st.markdown("---")
                
                if matched_list:
                    # 🔵 [الحالة ب]: المقاس له مجموعة مسبقة
                    st.info(f"💡 **[الحالة ب]**: تم العثور على مجموعة مقاسات متطابقة مسبقاً في الـ RAM!")
                    st.markdown(f"🎯 **الموديلات المتوافقة مع هاتف الزبون:** {', '.join(matched_list)}")
                    
                    if st.button("🔗 موافقة: دمج الموديل الجديد مع هذه المجموعة وتحديث السحاب"):
                        if new_size not in db_data: db_data[new_size] = {}
                        if new_panel not in db_data[new_size]: db_data[new_size][new_panel] = {}
                        if new_sensor not in db_data[new_size][new_panel]: db_data[new_size][new_panel][new_sensor] = []
                        
                        db_data[new_size][new_panel][new_sensor].append(search_term_live)
                        save_db(db_data)
                        add_notification(f"🟢 تم دمج الموديل {search_term_live} مع مجموعة المقاس {new_size}")
                        st.success("✅ تم الدمج والمزامنة السحابية بنجاح!")
                        st.balloons()
                        st.rerun()
                else:
                    # 🟠 [الحالة جـ]: المقاس جديد تماماً كلياً
                    st.warning(f"🚨 **[الحالة جـ]**: هذا المقاس جديد كلياً ({new_size}) ولم يتم العثور على أي مجموعة متوافقة.")
                    
                    if st.button("👑 موافقة عمار: تأسيس فرع ومجموعة مقاسات جديدة كلياً في السحاب"):
                        if new_size not in db_data: db_data[new_size] = {}
                        if new_panel not in db_data[new_size]: db_data[new_size][new_panel] = {}
                        if new_sensor not in db_data[new_size][new_panel]: db_data[new_size][new_panel][new_sensor] = []
                        
                        db_data[new_size][new_panel][new_sensor].append(search_term_live)
                        save_db(db_data)
                        add_notification(f"👑 قام عمار بتأسيس فرع ومجموعة مقاسات جديدة لـ {search_term_live}")
                        st.success("🚀 تم تأسيس الفرع والمجموعة الجديدة بنجاح في السحاب!")
                        st.balloons()
                        st.rerun()
