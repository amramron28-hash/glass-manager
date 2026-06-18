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

# 🎨 حقن تصميم الواجهة المخصص، الشعار، وألوان بطاقات الزجاج الفلورية (CSS)
st.markdown(
    """
    <style>
    /* تثبيت الخلفية المظلمة الفاخرة لتتناسب مع ألوان النيون */
    .stApp {
        background-color: #0d1117;
    }
    
    /* تصميم بطاقات النتائج الفلورية المتوافقة */
    .glass-card {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    /* تأثير التوهج الملون عند تمرير الماوس فوق بطاقات الزجاج */
    .glass-card:hover {
        transform: translateY(-2px);
    }
    
    /* نمط خط العناوين الفرعية والمجموعات */
    .app-sub-title {
        font-size: 18px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ☁️ تحميل قاعدة البيانات السحابية المركزية
db_data = load_db()

def local_check_existing_size_group(db, target_size, target_panel):
    """الخطة 2: دالة فحص وتدقيق المجموعات الهيكلية والمقاسات مسبقة الصنع"""
    matched_models = []
    if target_size in db:
        if target_panel in db[target_size]:
            for sensor, s_data in db[target_size][target_panel].items():
                models_list = (
                    s_data.get("models", [])
                    if isinstance(s_data, dict)
                    else s_data
                )
                for m in models_list:
                    matched_models.append(m)
    return matched_models

def ai_background_global_verify(phone_name):
    """دالة التحقق الخلفي الذكي ومطابقة المواصفات عبر الـ API العالمي"""
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

# 📊 احتساب وتحليل إحصائيات النظام السحابي الشاملة
all_flat_models = []
total_models = 0
brand_counts = {}
empty_groups_count = 0

for size, panels in db_data.items():
    size_has_models = False
    for panel, sensors in panels.items():
        for sensor, s_data in sensors.items():
            models_list = (
                s_data.get("models", [])
                if isinstance(s_data, dict)
                else s_data
            )
            if models_list:
                size_has_models = True
                total_models += len(models_list)
                for m in models_list:
                    all_flat_models.append(m)
                    words = m.split()
                    first_word = words[0] if words else "Unknown"
                    brand_counts[first_word] = brand_counts.get(first_word, 0) + 1
    if not size_has_models:
        empty_groups_count += 1

unique_models = sorted(list(set(all_flat_models)))

# ⚡ واجهة المستخدم: الشعار المتوهج الفاخر (ZEGAAR AMMAR GLASS MANAGER)
st.markdown(
"""
<div style="width:100%; font-size:32px; font-weight:900; color:#00bfff; text-align:center; text-shadow:0 0 15px rgba(0,191,255,0.8); margin-top:10px; margin-bottom:5px;">
ZEGAAR AMMAR<br>GLASS MANAGER
</div>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<div class='app-sub-title' style='text-align:center; color:#ffffff; opacity:0.9; margin-bottom:25px; font-family:sans-serif;'>
النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات
</div>
""",
unsafe_allow_html=True
)

# 🔍 محرك البحث والستارة المنسدلة المساعدة لتسريع الكتابة
def phone_search(searchterm):
    if not searchterm:
        return []
    term = searchterm.lower().strip()
    starts_with = [m for m in unique_models if m.lower().startswith(term)]
    contains = [m for m in unique_models if term in m.lower() and m not in starts_with]
    return (starts_with + contains)[:10]

# خانة البحث الحر والتقاط النص المدخل فورياً
phone = st.text_input(
    "البحث والمطابقة الفورية للموديلات:",
    placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة...",
    label_visibility="collapsed",
    key="free_smart_search_input"
).strip()

# توليد مصفوفة الاقتراحات المساعدة للستارة بناءً على مدخلات المستخدم
suggestions = phone_search(phone) if phone else []

# استخراج وفحص إحداثيات الطراز الحالي والتحقق من التطابق الحرفي
size_str, panel, sensor, real_name = find_model_coords(db_data, phone) if phone else (None, None, None, None)
is_exact_match = True if real_name and phone.lower() == real_name.lower() else False

# مصفوفة تخزين التنبيهات وعمليات التدقيق العالمي
global_audit_alerts = []
# ============================================================
# الخطة 1: مساعدة الكتابة الاقتراحية أو ظهور النتائج المطابقة حرفياً
# ============================================================
if phone:
    # أ- مرحلة الاقتراحات الستارية (تظهر فقط أثناء الكتابة وقبل التطابق الحرفي لتسريع العملية)
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
        # (قف) - لا يتم عرض أي خطة أخرى أثناء ظهور الاقتراحات منعاً لتداخل الواجهات

    # ب- مرحلة الهاتف موجود بالاسم الحرفي (تعرض النتائج الفورية وبطاقات النيون الملونة)
    elif is_exact_match:
        st.markdown(
            f"""
            <div class='section-title' style='text-align: right; color: #ffffff; font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 8px;'>
            📊 نتائج التوافق والمقاسات للهاتف: <span style='color: #00bfff;'>{real_name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # رسم الإحداثيات التقنية لشاشة الهاتف
        draw_technical_coords(size_str, panel, sensor)
        
        # استدعاء دالة جلب المتوافقات الصارمة من محرك المنطق
        results = get_compatibles_strict(db_data, phone)

        # 🟢 بطاقة النيون الخضراء: تطابق تام في الأبعاد والقص
        if "exact" in results:
            exact_list = [m for m in results["exact"] if m not in results.get("warn", [])]
            draw_neon_section(
                "هواتف مطابقة تماماً في الأبعاد والقص (Exact 0.00)", 
                exact_list, 
                "#2ecc71", 
                "🟢", 
                phone
            )

        # 🔵 بطاقة النيون الزرقاء: هواتف أكبر بقليل متوافقة
        if "plus" in results:
            draw_neon_section(
                "هواتف أكبر بقليل متوافقة (Plus +0.01 إلى +0.03)", 
                results["plus"], 
                "#3498db", 
                "🔵", 
                phone
            )

        # 🟤 بطاقة النيون البنية: هواتف أصغر بقليل متوافقة
        if "minus" in results:
            draw_neon_section(
                "هواتف أصغر بقليل متوافقة (Minus -0.01 إلى -0.03)", 
                results["minus"], 
                "#e67e22", 
                "🟤", 
                phone
            )

        # ⚠️ بطاقة النيون الحمراء الفلورية للتنبيهات الحساسة
        if results.get("warn"):
            draw_neon_section(
                "تنبيه حساس: هواتف بنفس المقاس ولكن بمستشعر مختلف:", 
                results["warn"], 
                "#ef4444", 
                "⚠️", 
                phone
            )
        # (قف) - انتهاء المسار التشغيلي الكامل للخطة 1 بنجاح

# ============================================================
# شرط عزل الخطة 2 و الخطة 3 (الحظر التام أثناء مرحلة الكتابة والاقتراحات)
# ============================================================
# لا يفتح النظام نوافذ التدقيق اليدوي إلا إذا كتب المستخدم اسماً كاملاً لا توجد له أي اقتراحات مساعدة وغير مسجل مسبقاً
should_open_manual_workflow = (phone != "" and not is_exact_match and not suggestions)

if should_open_manual_workflow:
    st.markdown("---")
    st.warning(f"⚠️ الهاتف ({phone}) غير مسجل بالاسم الحرفي ولا توجد اقتراحات مطابقة له. تم فتح النوافذ التتابعية لإدخال مواصفاته يدوياً:")

    # عرض المدخلات اليدوية الثلاثة تباعاً عبر الأعمدة الهيكلية
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

    # إذا اكتملت النوافذ الثلاثة تباعاً بالتتابع الصارم، تبدأ عملية الفحص السحابي للفصل بين الخطة 2 والخطة 3
    if new_size and new_panel and new_sensor:
        
        # إجراء عملية التدقيق والتحقق الخلفي عبر الـ API العالمي بالخلفية
        global_data = ai_background_global_verify(phone)
        if global_data and global_data["size"]:
            if new_size not in global_data["size"]:
                global_audit_alerts.append(
                    f"🚨 تدقيق عالمي: هاتف `{phone}` تم إدخاله بـ {new_size} والحقيقي في السحاب {global_data['size']}"
                )

        # فحص وجود أي قاعدة هيكلية ومجموعات متطابقة مسبقاً مدمجة في النظام
        matched_list = local_check_existing_size_group(db_data, new_size, new_panel)

        st.markdown("---")

        # ------------------------------------------------------------
        # الخطة 2: الاسم غير موجود ولكن تم العثور على مجموعة ومقاسات مطابقة مسبقاً
        # ------------------------------------------------------------
        if matched_list:
            st.info("💡 تم رصد مجموعة مقاسات وشاشات متطابقة مسبقاً في النظام السحابي!")
            st.markdown(f"🎯 الموديلات المتوافقة مع هذه المجموعة الحالية: **{', '.join(matched_list)}**")

            if st.button("🔗 موافقة: دمج الموديل الجديد وتحديث السحاب", key="btn_merge_model"):
                if new_size not in db_data:
                    db_data[new_size] = {}
                if new_panel not in db_data[new_size]:
                    db_data[new_size][new_panel] = {}
                if new_sensor not in db_data[new_size][new_panel]:
                    db_data[new_size][new_panel][new_sensor] = {"models": []}
                
                if phone not in db_data[new_size][new_panel][new_sensor]["models"]:
                    db_data[new_size][new_panel][new_sensor]["models"].append(phone)

                save_db(db_data)
                st.success(f"✅ تم دمج {phone} بنجاح كعنصر متوافق داخل المجموعة المكتشفة.")
                st.rerun()
            # (قف) - انتهاء الخطة 2 بالدمج التلقائي الناجح للمجموعة الحالية وتوقف المعالجة

        # ------------------------------------------------------------
        # الخطة 3: خطة الطوارئ الشاملة لعدم وجود الاسم والمجموعات (إنشاء مجموعة هيكلية جديدة)
        # ------------------------------------------------------------
        else:
            st.error("❌ خطة الطوارئ (الخطة 3): تعذر وجود الاسم وتطابق المجموعات المسبقة. لا توجد أي مواصفات مماثلة.")

            if st.button("➕ إنشاء مجموعة جديدة وإدراج الهاتف", key="btn_create_group"):
                if new_size not in db_data:
                    db_data[new_size] = {}
                if new_panel not in db_data[new_size]:
                    db_data[new_size][new_panel] = {}

                db_data[new_size][new_panel][new_sensor] = {"models": [phone]}

                save_db(db_data)
                st.success(f"✅ تم تفعيل خطة الطوارئ بنجاح، وإنشاء مجموعة سحابية جديدة لحفظ الهاتف {phone} كأول عنصر.")
                st.rerun()
            # (قف) - انتهاء الخطة 3 بتأسيس قاعدة جديدة كلياً وتوقف المعالجة

# ============================================================
# الإشعارات ولوحة التحكم الإحصائية العامة
# ============================================================
st.session_state.notifications = global_audit_alerts if global_audit_alerts else []

# استدعاء لوحة التحكم التابعة لـ ui_components (تظهر دائماً وبشكل ثابت في ذيل التطبيق)
draw_control_panel(
    notifications=st.session_state.notifications,
    total_models=total_models,
    empty_groups_count=empty_groups_count
)
