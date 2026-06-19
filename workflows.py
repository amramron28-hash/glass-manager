import os
import streamlit as st
import requests
from database import load_db, save_db

from logic_engine import (
    find_model_coords,
    get_compatibles_strict
)

from ui_components import (
    draw_technical_coords,
    draw_neon_section,
    draw_control_panel
)

def local_check_existing_size_group(db, target_size, target_panel):
    """فحص وتدقيق المجموعات الهيكلية مسبقة الصنع"""
    matched_models = []
    if target_size in db:
        if target_panel in db[target_size]:
            for sensor, s_data in db[target_size][target_panel].items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                for m in models_list:
                    matched_models.append(m)
    return matched_models

def ai_background_global_verify(phone_name):
    """التحقق الذكي عبر الـ API العالمي في الخلفية"""
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

def append_to_models_index(phone_name):
    """ضخ الاسم الجديد تلقائياً في ملف الأسماء الخفيف ليدخل في الستارة مستقبلاً"""
    INDEX_FILE = "models_index.txt"
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            current_models = [line.strip() for line in f if line.strip()]
        if phone_name not in current_models:
            with open(INDEX_FILE, "a", encoding="utf-8") as f:
                f.write(f"{phone_name}\n")

def run_system_workflows(phone, db_data, suggestions, total_models, empty_groups_count):
    """المحرك المركزي لإدارة الخطط الثلاث (1، 2، 3) بالتناغم الكامل"""
    
    # حساب متغيرات التطابق الحرفي العميقة
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone) if phone else (None, None, None, None)
    is_exact_match = True if real_name and phone.lower() == real_name.lower() else False
    global_audit_alerts = []

    # ============================================================
    # الخطة 1: نتائج التوافق الفورية للهواتف المطابقة حرفياً
    # ============================================================
    if is_exact_match:
        st.markdown(
            f"""
            <div class='section-title' style='text-align: right; color: #ffffff; font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 8px;'>
            📊 نتائج التوافق والمقاسات للهاتف: <span style='color: #00bfff;'>{real_name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        draw_technical_coords(size_str, panel, sensor)
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
        # [قف]

    # ============================================================
    # شرط عزل الخطة 2 و الخطة 3 (تفتح فقط بعد الحظر التام للاقتراحات وضغط Enter)
    # ============================================================
    should_open_manual_workflow = (phone != "" and not is_exact_match and not suggestions)

    if should_open_manual_workflow:
        st.markdown("---")
        st.warning(f"⚠️ الهاتف ({phone}) غير مسجل بالاسم الحرفي. تم تفعيل النوافذ التتابعية لإدخال مواصفاته:")

        col_s, col_p, col_se = st.columns(3)

        with col_s:
            new_size = st.text_input("📐 1. المقاس الرقمي للزبون (مثال: 6.67):", key="workflow_size").strip()

        chosen_panel = ""
        chosen_sensor = ""

        # تتابع النافذة الثانية: استعادة القوائم الثابتة القديمة تماماً مع تذييلها بخيار (+)
        if new_size:
            with col_p:
                panel_options = [
                    "",
                    "Punch-Hole Screen",
                    "Notch Screen",
                    "Waterdrop Notch",
                    "Full Screen",
                    "Flat Screen",
                    "Curved Screen",
                    "➕ إضافة شكل جديد..."
                ]
                selected_panel = st.selectbox("🖥️ 2. نوع الشاشة الهيكلي:", panel_options, key="workflow_panel")
                
                if selected_panel == "➕ إضافة شكل جديد...":
                    chosen_panel = st.text_input("✍️ اكتب شكل الشاشة الجديد هنا:", key="custom_panel_input").strip()
                else:
                    chosen_panel = str(selected_panel).strip()

        # تتابع النافذة الثالثة: استعادة القوائم الثابتة القديمة تماماً مع تذييلها بخيار (+)
        if new_size and chosen_panel:
            with col_se:
                sensor_options = [
                    "",
                    "hardware_top_sensor",
                    "virtual_camera_sensor",
                    "under_display_fingerprint",
                    "under_display_sensor",
                    "side_sensor",
                    "no_visible_sensor",
                    "➕ إضافة مستشعر جديد..."
                ]
                selected_sensor = st.selectbox("👁️ 3. مستشعر التقارب المكتشف:", sensor_options, key="workflow_sensor")
                
                if selected_sensor == "➕ إضافة مستشعر جديد...":
                    chosen_sensor = st.text_input("✍️ اكتب نوع المستشعر الجديد هنا:", key="custom_sensor_input").strip()
                else:
                    chosen_sensor = str(selected_sensor).strip()

        # تشغيل الفحص السحابي والدمج بعد اكتمال النوافذ التتابعية الصارمة
        if new_size and chosen_panel and chosen_sensor:
            global_data = ai_background_global_verify(phone)
            if global_data and global_data["size"]:
                if new_size not in global_data["size"]:
                    global_audit_alerts.append(
                        f"🚨 تدقيق عالمي: هاتف `{phone}` تم إدخاله بـ {new_size} والحقيقي في السحاب {global_data['size']}"
                    )

            matched_list = local_check_existing_size_group(db_data, new_size, chosen_panel)
            st.markdown("---")

            # ------------------------------------------------------------
            # الخطة 2: دمج الهاتف الجديد في مجموعة هيكلية مكتشفة مسبقاً
            # ------------------------------------------------------------
            if matched_list:
                st.info("💡 تم رصد مجموعة مقاسات وشاشات متطابقة مسبقاً في النظام السحابي!")
                st.markdown(f"🎯 الموديلات المتوافقة مع هذه المجموعة: **{', '.join(matched_list)}**")

                if st.button("🔗 موافقة: دمج الموديل الجديد وتحديث السحاب", key="btn_merge_model"):
                    if new_size not in db_data:
                        db_data[new_size] = {}
                    if chosen_panel not in db_data[new_size]:
                        db_data[new_size][chosen_panel] = {}
                    if chosen_sensor not in db_data[new_size][chosen_panel]:
                        db_data[new_size][chosen_panel][chosen_sensor] = {"models": []}
                    
                    if phone not in db_data[new_size][chosen_panel][chosen_sensor]["models"]:
                        db_data[new_size][chosen_panel][chosen_sensor]["models"].append(phone)

                    save_db(db_data)
                    append_to_models_index(phone)
                    st.success(f"✅ تم دمج {phone} وتحديث النظام السحابي بنجاح.")
                    st.rerun()
                # [قف]

            # ------------------------------------------------------------
            # الخطة 3: خطة الطوارئ وإنشاء مواصفات ومجموعة جديدة كلياً
            # ------------------------------------------------------------
            else:
                st.error("❌ خطة الطوارئ (الخطة 3): لا توجد مجموعة مسبقة تطابق هذه المواصفات.")

                if st.button("➕ إنشاء مجموعة جديدة وإدراج الهاتف", key="btn_create_group"):
                    if new_size not in db_data:
                        db_data[new_size] = {}
                    if chosen_panel not in db_data[new_size]:
                        db_data[new_size][chosen_panel] = {}

                    db_data[new_size][chosen_panel][chosen_sensor] = {"models": [phone]}

                    save_db(db_data)
                    append_to_models_index(phone)
                    st.success(f"✅ تم تفعيل خطة الطوارئ، وتأسيس المجموعة وإدراج {phone} بنجاح.")
                    st.rerun()
                # [قف]

    # تحديث واستدعاء لوحة التحكم الإحصائية العامة بأسفل الصفحة
    st.session_state.notifications = global_audit_alerts if global_audit_alerts else []
    draw_control_panel(
        notifications=st.session_state.notifications,
        total_models=total_models,
        empty_groups_count=empty_groups_count
    )

