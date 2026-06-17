# ==========================
# 🔍 البحث الذكي الحقيقي
# ==========================

def search_models(q):

    if not q:
        return []


    q_clean = q.lower().strip()


    try:

        # 1) بحث حقيقي بالكلمات
        exact_matches = []


        for model in unique_models:

            model_clean = str(model).lower().strip()


            # نفس بداية الاسم أو يحتوي الكلمات المكتوبة
            if (
                model_clean.startswith(q_clean)
                or q_clean in model_clean
            ):

                exact_matches.append(model)



        if exact_matches:

            return exact_matches[:10]



        # 2) مرحلة تصحيح بسيطة فقط
        # لا تعرض أسماء بعيدة

        result = process.extract(

            q,

            unique_models,

            limit=10,

            scorer=fuzz.WRatio

        )


        suggestions = []


        for item in result:

            name = item[0]
            score = item[1]


            if score >= 92:

                suggestions.append(name)



        return suggestions



    except Exception:

        return []
selected = st_searchbox(

    search_function=lambda q, **k:

    search_models(q),

    placeholder="🔍 ابحث عن هاتف",

    key="phone_search"

)



if isinstance(selected, str):

    selected = selected.strip()

    if selected:

        st.session_state.custom_search_input = selected



phone = st.session_state.custom_search_input
