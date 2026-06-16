# ==========================================
# 🛠️ لوحة التحكم الذكية
# 🔔 إشعارات + ⚙️ إعدادات + 🛡️ مراقب صامت
# ==========================================

def draw_control_panel(
    notifications=None,
    total_models=0,
    empty_groups_count=0
):

    notifications = notifications or []


    with st.sidebar:


        st.markdown(
            """
            <div style="
            text-align:center;
            color:#00bfff;
            font-size:26px;
            font-weight:900;
            ">
            🛠️ المراقب الصامت
            </div>
            """,
            unsafe_allow_html=True
        )


        st.divider()



        # ==========================
        # 🔔 الجرس
        # ==========================

        with st.expander(
            "🔔 مركز الإشعارات",
            expanded=False
        ):


            if notifications:


                for note in notifications:

                    st.warning(note)


            else:

                st.success(
                    "✅ لا توجد أخطاء مكتشفة"
                )



        # ==========================
        # ⚙️ الإعدادات
        # ==========================

        with st.expander(
            "⚙️ إعدادات التطبيق",
            expanded=False
        ):


            guard_active = st.toggle(
                "🧠 تشغيل المراقب الذكي",
                value=True
            )


            if guard_active:

                st.success(
                    "المراقب مفعل"
                )

            else:

                st.error(
                    "المراقب متوقف"
                )



            st.caption(
                "يقوم بفحص المقاسات القريبة واختلاف المستشعرات قبل الإدراج"
            )



        # ==========================
        # 🛡️ المراقب الصامت
        # ==========================

        with st.expander(
            "🛡️ حالة المراقب الصامت",
            expanded=True
        ):


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "📱 الهواتف",
                    total_models
                )


            with col2:

                st.metric(
                    "🧹 مراجعة",
                    empty_groups_count
                )



            st.info(
                "المراقب يراقب الإدخالات الجديدة ويمنع تشابهات خطرة مثل اختلاف الحساس مع نفس الزجاج"
            )
