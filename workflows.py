def run_system_workflows(phone, db_data, suggestions):
    """المحرك المركزي لإدارة الخطط الثلاث (1، 2، 3) بالتناغم الكامل"""
    
    # حساب متغيرات التطابق الحرفي العميقة
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone) if phone else (None, None, None, None)
    is_exact_match = True if real_name and phone.lower() == real_name.lower() else False
    global_audit_alerts = []

    # ============================================================
    # الخطة 1: نتائج التوافق الفورية
    # ============================================================
    if is_exact_match:
        st.markdown(f"### 📊 نتائج التوافق والمقاسات للهاتف: {real_name}")
        draw_technical_coords(size_str, panel, sensor)
        results = get_compatibles_strict(db_data, phone)
        
        if "exact" in results:
            draw_neon_section("هواتف مطابقة تماماً", [m for m in results["exact"] if m not in results.get("warn", [])], "#2ecc71", "🟢", phone)
        if "plus" in results:
            draw_neon_section("هواتف أكبر بقليل", results["plus"], "#3498db", "🔵", phone)
        if "minus" in results:
            draw_neon_section("هواتف أصغر بقليل", results["minus"], "#e67e22", "🟤", phone)
        if results.get("warn"):
            draw_neon_section("تنبيه حساس", results["warn"], "#ef4444", "⚠️", phone)

    # ============================================================
    # الخطة 2 و 3: المعالجة اليدوية
    # ============================================================
    should_open_manual_workflow = (phone != "" and not is_exact_match and not suggestions)

    if should_open_manual_workflow:
        st.markdown("---")
        st.warning(f"⚠️ الهاتف ({phone}) غير مسجل. يرجى إكمال المواصفات:")

        col_s, col_p, col_se = st.columns(3)
        with col_s:
            new_size = st.text_input("📐 المقاس الرقمي:", key="workflow_size").strip()
        with col_p:
            panel_options = ["", "Punch-Hole Screen", "Notch Screen", "Waterdrop Notch", "Full Screen", "Flat Screen", "Curved Screen", "➕ إضافة شكل جديد..."]
            selected_panel = st.selectbox("🖥️ نوع الشاشة:", panel_options, key="workflow_panel")
            chosen_panel = st.text_input("✍️ شكل الشاشة:", key="custom_panel_input") if selected_panel == "➕ إضافة شكل جديد..." else selected_panel
        with col_se:
            sensor_options = ["", "hardware_top_sensor", "virtual_camera_sensor", "under_display_fingerprint", "under_display_sensor", "side_sensor", "no_visible_sensor", "➕ إضافة مستشعر جديد..."]
            selected_sensor = st.selectbox("👁️ مستشعر التقارب:", sensor_options, key="workflow_sensor")
            chosen_sensor = st.text_input("✍️ نوع المستشعر:", key="custom_sensor_input") if selected_sensor == "➕ إضافة مستشعر جديد..." else selected_sensor

        if new_size and chosen_panel and chosen_sensor:
            matched_list = local_check_existing_size_group(db_data, new_size, chosen_panel)
            st.markdown("---")

            # تهيئة حالة النجاح
            if f"success_saved_{phone}" not in st.session_state:
                st.session_state[f"success_saved_{phone}"] = False

            # تنفيذ الحفظ (مشترك للخطة 2 و 3)
            def save_new_model():
                if new_size not in db_data: db_data[new_size] = {}
                if chosen_panel not in db_data[new_size]: db_data[new_size][chosen_panel] = {}
                if chosen_sensor not in db_data[new_size][chosen_panel]: db_data[new_size][chosen_panel][chosen_sensor] = {"models": []}
                if phone not in db_data[new_size][chosen_panel][chosen_sensor]["models"]:
                    db_data[new_size][chosen_panel][chosen_sensor]["models"].append(phone)
                save_db(db_data)
                append_to_models_index(phone)
                st.session_state[f"success_saved_{phone}"] = True

            if matched_list:
                st.info(f"💡 تم رصد مجموعة متطابقة: {', '.join(matched_list)}")
                if not st.session_state[f"success_saved_{phone}"]:
                    if st.button("🔗 دمج الموديل الجديد"):
                        save_new_model()
                        st.rerun()
            else:
                st.error("❌ الخطة 3: لا توجد مجموعة مسبقة.")
                if not st.session_state[f"success_saved_{phone}"]:
                    if st.button("➕ إنشاء مجموعة جديدة وإدراج الهاتف"):
                        save_new_model()
                        st.rerun()

            if st.session_state[f"success_saved_{phone}"]:
                st.success("✅ تم قفل ودمج الهاتف بنجاح!")
                if st.button("🔄 تحديث النظام"):
                    st.session_state[f"success_saved_{phone}"] = False
                    st.rerun()

