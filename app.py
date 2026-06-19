import streamlit as st
import os
import requests

from database import load_db, save_db

from logic_engine import (
    normalize_text,
    find_model_coords,
    get_compatibles_strict,
    run_intelligent_inspector
)

from ui_components import (
    inject_pwa_and_styles,
    draw_technical_coords,
    draw_neon_section,
    draw_control_panel
)

# 🖥️ إعدادات الصفحة العامة للنظام الموحد
st.set_page_config(
    layout="wide",
    page_title="ZEGAAR AMMAR GLASS MANAGER",
    page_icon="🔍"
)

# حقن أنماط الـ PWA والملفات الأساسية
inject_pwa_and_styles()

# 🎨 تصميم الواجهة وتصحيح تموضع الشعار لمنع التداخل مع صورة الخلفية
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0d1117;
    }
    .main-header-container {
        width: 100%;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 20px;
        padding: 5px;
    }
    .main-logo {
        font-size: 32px; 
        font-weight: 900; 
        color: #00bfff; 
        text-shadow: 0 0 15px rgba(0,191,255,0.8);
        line-height: 1.2;
    }
    .main-subtitle {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        opacity: 0.95;
        margin-top: 8px;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
    }
    .glass-card {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
    }
    </style>
    
    <div class="main-header-container">
        <div class="main-logo">ZEGAAR AMMAR<br>GLASS MANAGER</div>
        <div class="main-subtitle">النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ☁️ تحميل قاعدة البيانات السحابية المركزية
db_data = load_db()

# 🗂️ تحديد ملف الأسماء الخفيف (مؤشر مساعدة الكتابة)
INDEX_FILE = "models_index.txt"

def load_flat_models_index():
    """قراءة الأسماء فقط من الملف النصي الخفيف لصناعة ستارة مساعدة فلاشية"""
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return sorted(list(set([line.strip() for line in f if line.strip()])))

def append_to_models_index(phone_name):
    """ضخ الاسم الجديد تلقائياً في ملف الأسماء الخفيف عند الحفظ أو الدمج"""
    current_models = load_flat_models_index()
    if phone_name not in current_models:
        with open(INDEX_FILE, "a", encoding="utf-8") as f:
            f.write(f"{phone_name}\n")

# جلب مصفوفة الهواتف من الملف النصي الخفيف (استجابة فلاشية للمساعدة في الكتابة)
unique_models = load_flat_models_index()

def local_check_existing_size_group(db, target_size, target_panel):
    matched_models = []
    if target_size in db:
        if target_panel in db[target_size]:
            for sensor, s_data in db[target_size][target_panel].items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                for m in models_list:
                    matched_models.append(m)
    return matched_models

def ai_background_global_verify(phone_name):
    try:
        url = f"https://vercel.app{requests.utils.quote(phone_name)}"
        res = requests.get(url, timeout=1.5).json()
        if res and "specs" in res:
            return {
                "size": str(res["specs"].get("display_size", "")),
                "panel": str(res["specs"].get("display_type", "")),
                "sensor": str(res["specs"].get("proximity_type", ""))
            }
    except:
        pass
    return None

# حساب الإحصائيات العامة من مصفوفة الأسماء المساعدة مباشرة
total_models = len(unique_models)
empty_groups_count = 0
for size, panels in db_data.items():
    size_has_models = False
    for panel, sensors in panels.items():
        for sensor, s_data in sensors.items():
            models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
            if models_list:
                size_has_models = True
    if not size_has_models:
        empty_groups_count += 1

# 🔍 دالة جلب الاقتراحات اللحظية من الملف النصي الخفيف
def fast_phone_search(searchterm):
    if not searchterm:
        return []
    term = searchterm.lower().strip()
    starts_with = [m for m in unique_models if m.lower().startswith(term)]
    contains = [m for m in unique_models if term in m.lower() and m not in starts_with]
    return (starts_with + contains)[:10]

# خانة البحث الحر الفوري
phone = st.text_input(
    "البحث والمطابقة الفورية للموديلات:",
    placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة...",
    label_visibility="collapsed",
    key="free_smart_search_input"
).strip()

# جلب الاقتراحات المساعدة لحظياً وبسرعة خارقة من الملف الخفيف أثناء الكتابة فقط
suggestions = fast_phone_search(phone) if phone else []
# ============================================================
# إنهاء دور الملف الخفيف فوراً بمجرد الضغط على زر الإدخال (Enter)
# ============================================================
# إذا كتب المستخدم نصاً وضغط Enter (أو اختار اسماً كاملاً يطابق المؤشر)، ينتهي دور الستارة المساعدة تماماً وقف
# هنا نتحقق هل النص المكتوب يمثل تطابقاً حرفياً كاملاً في قاعدة البيانات الحقيقية
size_str, panel, sensor, real_name = (
    find_model_coords(db_data, phone) 
    if phone 
    else (None, None, None, None)
)

is_exact_match = True if real_name and phone.lower() == real_name.lower() else False
global_audit_alerts = []


# ============================================================
# الخطة 1: مساعدة الكتابة الاقتراحية أو ظهور النتائج المطابقة حرفياً
# ============================================================
if phone:
    # أ- مرحلة الاقتراحات المساعدة (تظهر فلاشياً من الملف الخفيف أثناء الكتابة فقط وقبل ضغط Enter والتطابق)
    if suggestions and not is_exact_match:
        st.markdown(
            """
            <div style='padding: 10px; background: rgba(0, 191, 255, 0.05); border-right: 4px solid #00bfff; margin-bottom: 15px; border-radius: 4px;'>
                <span style='color: #00bfff; font-weight: bold;'>💡 اقتراحات البحث المساعدة لتسريع الكتابة:</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        for item in suggestions:
            st.markdown(f"🔍 **{item}**")
        # (قف) - ينتهي دور هذه الكتلة تماماً ولا تتداخل مع أي واجهة أخرى

    # b- مرحلة الهاتف موجود بالاسم الحرفي (تعرض النتائج الفورية بعد تأكيد الاسم وضغط Enter)
    elif is_exact_match:
        st.markdown(
            f"""
            <div class='section-title' style='text-align: right; color: #ffffff; font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 8px;'>
            📊 نتائج التوافق والمقاسات للهاتف: <span style='color: #00bfff;'>{real_name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # رسم الإحداثيات التقنية لشاشة الهاتف المستهدف
        draw_technical_coords(size_str, panel, sensor)
        
        # جلب المتوافقات الصارمة وبطاقات النيون الملونة لزجاج الحماية
        results = get_compatibles_strict(db_data, phone)

        if "exact" in results:
            exact_list = [m for m in results["exact"] if m not in results.get("warn", [])]
            draw_neon_section("هواتف مطابقة تماماً في الأبعاد والقص (Exact 0.00)", exact_list, "#2ecc71", "🟢", phone)

        if "plus" in results:
            draw_neon_section("هواتف أكبر بقليل متوافقة (Plus +0.01 إلى +0.03)", results["plus"], "#3498db", "🔵", phone)

        if "minus" in results:
            draw_neon_section("هواتف أصغر بقليل متوافقة (Minus -0.01 إلى -0.03)", results["minus"], "#e67e22", "🟤", phone)

        if results.get("warn"):
            draw_neon_section("تنبيه حساس: هواتف بنفس المقاس ولكن بمستشعر مختلف:", results["warn"], "#ef4444", "⚠️", phone)
        # (قف) - انتهاء المسار التشغيلي الكامل للخطة 1 بنجاح


# ============================================================
# شرط عزل الخطة 2 و الخطة 3 (حظر واجهات الإدخال اليدوي أثناء الكتابة)
# ============================================================
# بمجرد الضغط على Enter وعدم وجود أي تطابق أو اقتراح مساعد، يتم فتح واجهة المدخلات التتابعية فوراً
should_open_manual_workflow = (phone != "" and not is_exact_match and not suggestions)

if should_open_manual_workflow:
    st.markdown("---")
    st.warning(f"⚠️ الهاتف ({phone}) غير مسجل بالاسم الحرفي. تم تفعيل النوافذ التتابعية لإدخال مواصفاته:")

    # رسم المدخلات الثلاثة تباعاً عبر الأعمدة الهيكلية
    col_s, col_p, col_se = st.columns(3)

    with col_s:
        new_size = st.text_input("📐 1. المقاس الرقمي للزبون (مثال: 6.67):", key="workflow_size").strip()

    new_panel = ""
    new_sensor = ""

    # ظهور النافذة الثانية مشروط باكتمال الأولى
    if new_size:
        with col_p:
            new_panel = str(st.selectbox(
                "🖥️ 2. نوع الشاشة الهيكلي:",
                ["", "Punch-Hole Screen", "Notch Screen", "Waterdrop Notch", "Full Screen", "Flat Screen", "Curved Screen"],
                key="workflow_panel"
            )).strip()

    # ظهور النافذة الثالثة مشروط باكتمال الثانية
    if new_size and new_panel:
        with col_se:
            new_sensor = str(st.selectbox(
                "👁️ 3. مستشعر التقارب المكتشف والمراقب:",
                ["", "hardware_top_sensor", "virtual_camera_sensor", "under_display_fingerprint", "under_display_sensor", "side_sensor", "no_visible_sensor"],
                key="workflow_sensor"
            )).strip()

    # إذا اكتملت النوافذ الثلاثة بالتتابع الصارم، يبدأ الفحص السحابي وضخ البيانات تلقائياً
    if new_size and new_panel and new_sensor:
        
        global_data = ai_background_global_verify(phone)
        if global_data and global_data["size"]:
            if new_size not in global_data["size"]:
                global_audit_alerts.append(
                    f"🚨 تدقيق عالمي: هاتف `{phone}` تم إدخاله بـ {new_size} والحقيقي في السحاب {global_data['size']}"
                )

        # فحص وجود مجموعات متطابقة مسبقاً في النظام
        matched_list = local_check_existing_size_group(db_data, new_size, new_panel)

        st.markdown("---")

        # ------------------------------------------------------------
        # الخطة 2: دمج الهاتف الجديد تلقائياً في مجموعة مسجلة مسبقاً
        # ------------------------------------------------------------
        if matched_list:
            st.info("💡 تم رصد مجموعة مقاسات وشاشات متطابقة مسبقاً في النظام السحابي!")
            st.markdown(f"🎯 الموديلات المتوافقة مع هذه المجموعة: **{', '.join(matched_list)}**")

            if st.button("🔗 موافقة: دمج الموديل الجديد وتحديث السحاب", key="btn_merge_model"):
                if new_size not in db_data:
                    db_data[new_size] = {}
                if new_panel not in db_data[new_size]:
                    db_data[new_size][new_panel] = {}
                if new_sensor not in db_data[new_size][new_panel]:
                    db_data[new_size][new_panel][new_sensor] = {"models": []}
                
                if phone not in db_data[new_size][new_panel][new_sensor]["models"]:
                    db_data[new_size][new_panel][new_sensor]["models"].append(phone)

                # 1. حفظ البيانات في السحاب الشامل للمواصفات
                save_db(db_data)
                
                # 2. التناغُم والضخ الدوري: ضخ الاسم الجديد تلقائياً لملف الأسماء الخفيف ليصبح مساعداً في المرات القادمة
                append_to_models_index(phone)
                
                st.success(f"✅ تم دمج {phone} وضخ اسمه تلقائياً في مؤشر المساعدة الفلاشي.")
                st.rerun()
            # (قف) - انتهاء الخطة 2 بالكامل

        # ------------------------------------------------------------
        # الخطة 3: خطة الطوارئ (إنشاء مجموعة هيكلية جديدة تماماً في السحاب والمؤشر)
        # ------------------------------------------------------------
        else:
            st.error("❌ خطة الطوارئ (الخطة 3): تعذر وجود تطابق في المجموعات المسبقة.")

            if st.button("➕ إنشاء مجموعة جديدة وإدراج الهاتف", key="btn_create_group"):
                if new_size not in db_data:
                    db_data[new_size] = {}
                if new_panel not in db_data[new_size]:
                    db_data[new_size][new_panel] = {}

                db_data[new_size][new_panel][new_sensor] = {"models": [phone]}

                # 1. حفظ البيانات وتأسيس المجموعة الجديدة في السحاب
                save_db(db_data)
                
                # 2. التناغُم والضخ الدوري: ضخ الاسم الجديد تلقائياً لملف الأسماء الخفيف
                append_to_models_index(phone)
                
                st.success(f"✅ تم تفعيل خطة الطوارئ، وتأسيس المجموعة وضخ الهاتف {phone} في النظام.")
                st.rerun()
            # (قف) - انتهاء الخطة 3 بالكامل


# ============================================================
# الإشعارات ولوحة التحكم الإحصائية العامة
# ============================================================
st.session_state.notifications = global_audit_alerts if global_audit_alerts else []

# استدعاء لوحة التحكم التابعة لـ ui_components (ثابتة في ذيل التطبيق)
draw_control_panel(
    notifications=st.session_state.notifications,
    total_models=total_models,
    empty_groups_count=empty_groups_count
)
