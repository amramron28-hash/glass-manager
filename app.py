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

# محرك الذكاء الاصطناعي لاقتراح المواصفات فقط كمساعد للمستخدم
def ai_suggest_coords(phone_name, db):
    words = phone_name.lower().split()
    if not words:
        return "6.78", "Punch-Hole Screen", "virtual_camera_sensor"
    best_match = 0
    p_size, p_panel, p_sensor = "6.78", "Punch-Hole Screen", "virtual_camera_sensor"
    for size, panels in db.items():
        for panel, sensors in panels.items():
            for sensor, group_data in sensors.items():
                for model in group_data.get("models", []):
                    matches = sum(1 for w in words if w in model.lower())
                    if matches > best_match:
                        best_match = matches
                        p_size, p_panel, p_sensor = size, panel, sensor
    return p_size, p_panel, p_sensor

st.markdown("""
    <div style="font-size:28px; font-weight:900; color:#00bfff; text-shadow:0 0 12px rgba(0,191,255,.7);">
    ZEGAAR AMMAR<br>GLASS MANAGER
    </div>
    """, unsafe_allow_html=True)

if st.session_state.show_success:
    st.success(st.session_state.show_success)
    st.session_state.show_success = ""

phone = st.text_input("📱 اسم الهاتف", placeholder="مثال: Infinix Note 60").strip()

if phone:
    suggestions = [m for m in unique_models if all(w in m.lower() for w in phone.lower().split())]
    if suggestions:
        st.caption("🔍 هواتف قد تقصدها في النظام:")
        for s in suggestions[:3]:
            st.write(f"• {s}")

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

    else:
        st.warning(f"⚠️ الهاتف ({phone}) غير مسجل في النظام.")
        
        # 1. ينتهي دور الـ AI هنا بمجرد اقتراح المواصفات الثلاثة فقط كمعلومة استرشادية
        ai_size, ai_panel, ai_sensor = ai_suggest_coords(phone, db_data)
        st.info(f"🤖 **مواصفات مقترحة ذكياً لهذا الهاتف:** المقاس: `{ai_size}` | الشاشة: `{ai_panel}` | المستشعر: `{ai_sensor}`")
        
        # 2. العودة للخطة 1: البحث التلقائي بناءً على المواصفات المقترحة في جميع مجموعات المكتبة
        group = db_data.get(ai_size, {}).get(ai_panel, {}).get(ai_sensor, {})
        models = group.get("models", [])

        # 3. النتيجة وعرض النافذة المناسبة للاتخاذ الإجراء فوراً
        if models:
            st.success("🤝 تم العثور على مجموعة مطابقة لهذه المواصفات في المكتبة!")
            st.write("📋 الهواتف الحالية في المجموعة:", models)
            
            if st.button(f"📥 إدراج {phone} في هذه المجموعة المطابقة"):
                add_model(ai_size, ai_panel, ai_sensor, phone)
                st.session_state.show_success = f"تم إدراج {phone} بنجاح في المجموعة المطابقة!"
                st.rerun()
        else:
            st.error("❌ لم يتم العثور على أي مجموعة مطابقة لهذه المواصفات في المكتبة.")
            
            if st.button(f"✨ إنشاء مجموعة جديدة بالكامل وإدراج {phone} فيها"):
                add_model(ai_size, ai_panel, ai_sensor, phone)
                st.session_state.show_success = f"تم إنشاء المجموعة الجديدة بنجاح وإدراج {phone}!"
                st.rerun()

# ==========================
# لوحة التحكم
# ==========================
draw_control_panel(
    notifications=st.session_state.notifications,
    total_models=total_models,
    empty_groups_count=empty_groups_count
)

