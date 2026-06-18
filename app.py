import streamlit as st
from database import add_model
from logic_engine import (
    find_model_coords,
    get_compatibles_strict
)
from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section,
    draw_control_panel
)
from app_init import initialize_system_data

st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

inject_pwa_and_styles()

@st.cache_data(ttl=300)
def load_system_data():
    return initialize_system_data()

if "notifications" not in st.session_state:
    st.session_state.notifications = []

if "show_success" not in st.session_state:
    st.session_state.show_success = ""

ALL_PANELS = [
    "Notch Screen", "Punch-Hole Screen", "Waterdrop Notch",
    "Full Screen", "Flat Screen", "Curved Screen"
]

ALL_SENSORS = [
    "hardware_top_sensor", "virtual_camera_sensor", "under_display_sensor",
    "side_sensor", "no_visible_sensor"
]

(
    db_data, unique_models, total_models, empty_groups_count,
    brand_counts, live_sizes, live_panels, live_sensors
) = load_system_data()

unique_models = [str(x).strip() for x in unique_models if x]

st.markdown("""
    <div style="font-size:28px; font-weight:900; color:#00bfff; text-shadow:0 0 12px rgba(0,191,255,.7);">
    ZEGAAR AMMAR<br>GLASS MANAGER
    </div>
    """, unsafe_allow_html=True)

if st.session_state.show_success:
    st.success(st.session_state.show_success)
    st.session_state.show_success = ""

phone = st.text_input("📱 اسم الهاتف", placeholder="مثال: Infinix Note 60").strip()

# الخطة 1: ستارة الاقتراحات تظهر فوراً وتتحرك مع كل حرف يكتبه المستخدم
if phone:
    suggestions = [m for m in unique_models if all(w in m.lower() for w in phone.lower().split())]
    if suggestions:
        st.caption("🔍 هواتف مقترحة مطابقة في النظام:")
        for s in suggestions[:3]:
            if st.button(f"📋 {s}", key=f"sug_{s}"):
                st.session_state["phone_input_val"] = s
                st.rerun()

# التحقق والبحث الصارم بالاسم بالخطة 1
size, panel, sensor, real = None, None, None, None
if phone:
    size, panel, sensor, real = find_model_coords(db_data, phone)

is_exact_match = True if real and phone.lower() in real.lower() else False

if size and is_exact_match:
    st.success(f"🎯 الهاتف موجود : {real}")
    draw_technical_coords(size, panel, sensor)
        results = get_compatibles_strict(db_data, phone)

        if results:
            draw_neon_section("مطابق ±0.03", results["exact"], "#2ecc71", "🎯", phone)
            draw_neon_section("أكبر بقليل ±0.03", results["plus"], "#3498db", "➕", phone)
            draw_neon_section("أصغر بقليل ±0.03", results["minus"], "#e67e22", "➖", phone)
            draw_neon_section("تحذير مستشعر مختلف", results["warn"], "#ef4444", "⚠️", phone)
        
        # وينتهي دور الخطة 1 تماماً قف

    else:
        # الخطة 2: تظهر فوراً وبقوة عند إدخال اسم غير موجود بالكامل مثل (infinix note 60)
        st.warning(f"⚠️ الهاتف ({phone}) غير مسجل. يرجى إدخال مواصفاته يدوياً بالتتابع:")
        
        final_size = st.text_input("📏 1. أدخل المقاس", placeholder="مثال 6.78")
        final_panel = ""
        final_sensor = ""

        # القائمة الثانية تظهر تفاعلياً وتلقائياً بعد كتابة المقاس مباشرة
        if final_size.strip():
            final_panel = st.selectbox(
                "📺 2. اختر شكل الشاشة",
                [""] + ALL_PANELS + live_panels + ["➕ إضافة جديد"]
            )
            if final_panel == "➕ إضافة جديد":
                final_panel = st.text_input("اكتب شكل الشاشة الجديد")

        # القائمة الأخيرة التفاعلية يبدأ البحث والفرز الفوري بمجرد الاختيار منها مباشرة
        if final_size.strip() and str(final_panel).strip():
            final_sensor = st.selectbox(
                "👁️ 3. اختر مستشعر التقارب (يبدأ البحث فوراً عند الاختيار)",
                [""] + ALL_SENSORS + live_sensors + ["➕ إضافة جديد"]
            )
            if final_sensor == "➕ إضافة جديد":
                final_sensor = st.text_input("اكتب المستشعر الجديد")

        final_size = str(final_size).strip()
        final_panel = str(final_panel).strip()
        final_sensor = str(final_sensor).strip()

        # معالجة المطابقة الفورية والنهائية فور اختيار القائمة الأخيرة التفاعلية
        if final_size and final_panel and final_sensor:
            group = db_data.get(final_size, {}).get(final_panel, {}).get(final_sensor, {})
            models = group.get("models", [])

            if models:
                st.success("🤝 تم العثور الفوري على مجموعة مطابقة لهذه المواصفات المدخلة!")
                st.write("📋 الهواتف المشتركة حالياً في المجموعة:", models)
                
                if st.button(f"📥 تأكيد إدراج {phone} في هذه المجموعة المطابقة"):
                    add_model(final_size, final_panel, final_sensor, phone)
                    st.session_state.show_success = f"تم إدراج {phone} بنجاح!"
                    st.rerun()
                
                # وينتهي دور الخطة 2 تماماً قف

            else:
                # الخطة 3: خطة الطوارئ النهائية تفتح فوراً في حال عدم وجود مجموعة تطابق مدخلاتك
                st.error("❌ خطة الطوارئ (الخطة 3): لا توجد مجموعة تطابق هذه المواصفات في المكتبة.")
                
                if st.button(f"✨ إنشاء مجموعة جديدة بالكامل وإدراج {phone} فيها"):
                    add_model(final_size, final_panel, final_sensor, phone)
                    st.session_state.show_success = f"تم تطبيق خطة الطوارئ: تم إنشاء المجموعة وإدراج {phone}!"
                    st.rerun()
                
                # وينتهي دور الخطة 3 تماماً قف

# ==========================
# لوحة التحكم
# ==========================
draw_control_panel(
    notifications=st.session_state.notifications,
    total_models=total_models,
    empty_groups_count=empty_groups_count
)
