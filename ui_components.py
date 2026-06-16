# ==========================================
# 🛠️ لوحة التحكم الذكية (الإشعارات + الإعدادات + المراقب)
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
            <h2 style="
            text-align:center;
            color:#00bfff;
            ">
            ⚙️ لوحة التحكم
            </h2>
            """,
            unsafe_allow_html=True
        )


        with st.expander("🔔 الإشعارات", expanded=False):

            if notifications:

                for note in notifications:
                    st.warning(note)

            else:

                st.info(
                    "لا توجد تنبيهات حالياً"
                )


        with st.expander("⚙️ الإعدادات", expanded=False):

            st.write(
                "إعدادات التطبيق"
            )

            st.checkbox(
                "تفعيل تنبيهات المراقب الصامت",
                value=True
            )


        with st.expander("🛠️ المراقب الصامت", expanded=True):

            st.metric(
                "📱 إجمالي الهواتف",
                total_models
            )

            st.metric(
                "🧹 مجموعات تحتاج مراجعة",
                empty_groups_count
            )


            st.caption(
                "المراقب جاهز لمتابعة الإدخالات الجديدة"
            )
