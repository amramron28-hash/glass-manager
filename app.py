import os
import json
from shiny import App, ui, render, reactive
from supabase import create_client, Client
from dotenv import load_dotenv

from ui_components import inject_pwa_and_styles, draw_control_panel


# ==========================================================
# 1) Supabase
# ==========================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==========================================================
# 2) Workflow
# ==========================================================

try:
    from workflows import run_system_workflows

except Exception:

    def run_system_workflows(model, db, suggestions=None):
        return f"""
        <div class="glass-card">
            <h3 class="neon-text">{model}</h3>
            <p>Workflow غير متوفر</p>
        </div>
        """



# ==========================================================
# 3) Local index
# ==========================================================

JSON_INDEX_PATH = "models_id_db.json"


def load_local_json():

    if os.path.exists(JSON_INDEX_PATH):

        try:

            with open(
                JSON_INDEX_PATH,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except:

            return {}

    return {}



def save_local_json(data):

    try:

        with open(
            JSON_INDEX_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        print(e)



# ==========================================================
# 4) UI
# ==========================================================


app_ui = ui.page_fluid(

    ui.HTML(
        inject_pwa_and_styles()
    ),


    ui.HTML("""

    <div id="drawer" class="drawer">

    </div>

    <div class="header-bar">

        <div onclick="
        document.getElementById('drawer')
        .classList.toggle('open')"
        style="
        font-size:28px;
        cursor:pointer;
        color:#00bfff">

        ☰

        </div>


        <h2 style="color:#00bfff">
        ZEGAAR AMMAR
        </h2>


    </div>

    """),



    ui.output_ui(
        "control_panel"
    ),



    ui.div(

        ui.input_text(
            "search_query",
            "",
            placeholder="ابحث عن موديل الهاتف..."
        ),


        ui.output_ui(
            "suggestions_curtain_ui"
        ),



        ui.input_action_button(
            "btn_search",
            "افحص الهاتف 🔍",
            class_="btn-neon"
        ),



        ui.output_ui(
            "main_content_ui"
        ),


        class_="search-box"

    )

)



# ==========================================================
# 5) Server
# ==========================================================


def server(inp, output, session):


    refresh_trigger = reactive.value(0)

    current_plan = reactive.value(0)

    wizard_step = reactive.value(1)

    show_suggestions = reactive.value(False)



    screen_options = reactive.value(
        [
            "Notch",
            "Punch",
            "Curved"
        ]
    )


    sensor_options = reactive.value(
        [
            "hardware",
            "under_display"
        ]
    )



    @reactive.calc
    def cloud_database():

        refresh_trigger.get()

        try:

            res = (
                supabase
                .table("phones")
                .select("*")
                .execute()
            )

            return res.data or []


        except Exception as e:

            print(e)

            return []



    @render.ui
    def control_panel():

        return draw_control_panel(
            total_models=len(
                cloud_database()
            )
        )



    @render.text
    def model_count_display():

        return (
            f"📱 عدد الموديلات: "
            f"{len(cloud_database())}"
        )



    # ======================================================
    # Auto complete
    # ======================================================


    @reactive.effect
    @reactive.event(inp.search_query)
    def search_change():

        show_suggestions.set(True)

        current_plan.set(0)



    @render.ui
    def suggestions_curtain_ui():


        if not show_suggestions():

            return ui.div()



        q = inp.search_query().strip().lower()


        if not q:

            return ui.div()



        local = load_local_json()


        models = list(local.keys())


        if not models:

            models = [
                x.get("model_name")
                for x in cloud_database()
                if x.get("model_name")
            ]



        matches = [

            m for m in models

            if m and q in m.lower()

        ][:8]



        if not matches:

            return ui.div()



        rows=[]


        for m in matches:


            rows.append(

                ui.div(

                    f"📱 {m}",

                    class_="suggestion-row",

                    onclick=f"""
                    Shiny.setInputValue(
                    'selected_suggestion',
                    '{m}',
                    {{priority:'event'}}
                    )
                    """

                )

            )



        return ui.div(

            ui.div(

                class_="dismiss-overlay",

                onclick="""
                Shiny.setInputValue(
                'clicked_outside',
                Math.random(),
                {priority:'event'}
                )
                """

            ),

            ui.div(

                *rows,

                class_="suggestions-curtain"

            )

)
# ==========================================================
# إغلاق الستارة
# ==========================================================


    @reactive.effect
    @reactive.event(inp.clicked_outside)
    def close_curtain():

        show_suggestions.set(False)



    @reactive.effect
    @reactive.event(inp.selected_suggestion)
    def select_model():

        value = inp.selected_suggestion()

        ui.update_text(
            "search_query",
            value=value
        )

        show_suggestions.set(False)



# ==========================================================
# البحث الرئيسي
# ==========================================================


    @reactive.effect
    @reactive.event(inp.btn_search)
    def search_button():


        show_suggestions.set(False)


        query = inp.search_query().strip()



        if not query:


            ui.notification_show(
                "اكتب اسم الهاتف أولاً",
                type="warning"
            )

            return



        db = cloud_database()



        phone = next(

            (

                x for x in db

                if str(
                    x.get("model_name","")
                ).lower().strip()
                ==
                query.lower().strip()

            ),

            None

        )



        if phone:


            current_plan.set(1)



        else:


            ui.notification_show(

                "الموديل غير موجود بالاسم، الانتقال للخطة 2",

                type="warning"

            )


            current_plan.set(2)

            wizard_step.set(1)





# ==========================================================
# الخطة 2
# ==========================================================


    @reactive.effect
    @reactive.event(inp.next1)
    def next_one():


        if not inp.v1().strip():

            ui.notification_show(
                "أدخل المقاس",
                type="error"
            )

            return


        wizard_step.set(2)



    @reactive.effect
    @reactive.event(inp.next2)
    def next_two():

        wizard_step.set(3)





    @reactive.effect
    @reactive.event(inp.check_spec_match)
    def check_match():


        db = cloud_database()


        size = inp.v1().strip()

        panel = inp.v2()

        sensor = inp.v3()



        matches = [

            x for x in db

            if

            str(x.get("size","")).strip()
            == size

            and

            str(x.get("panel","")).lower().strip()
            ==
            str(panel).lower().strip()

            and

            str(x.get("sensor","")).lower().strip()
            ==
            str(sensor).lower().strip()

        ]



        if matches:

            current_plan.set(22)


        else:

            current_plan.set(3)





# ==========================================================
# الخطة 3 حفظ
# ==========================================================


    @reactive.effect
    @reactive.event(inp.emergency_save)
    def emergency_save():


        name = inp.search_query().strip()


        data = {

            "model_name":name,

            "size":inp.v1(),

            "panel":inp.v2(),

            "sensor":inp.v3()

        }



        try:


            supabase.table(
                "phones"
            ).insert(data).execute()



            local = load_local_json()



            local[name] = data



            save_local_json(local)



            refresh_trigger.set(
                refresh_trigger()+1
            )



            current_plan.set(0)



            ui.update_text(
                "search_query",
                value=""
            )



            ui.notification_show(
                "تم الحفظ بنجاح",
                type="message"
            )


        except Exception as e:


            ui.notification_show(
                str(e),
                type="error"
            )





# ==========================================================
# عرض النتائج
# ==========================================================


    @render.ui
    def main_content_ui():


        plan = current_plan()


        query = inp.search_query().strip()



        if not query:

            return ui.div()



        if plan == 1:


            db = cloud_database()


            return ui.HTML(

                run_system_workflows(
                    query,
                    db
                )

            )





        if plan == 2:


            step = wizard_step()



            if step == 1:


                return ui.div(

                    ui.h4(
                        "📏 الخطة 2"
                    ),


                    ui.input_text(
                        "v1",
                        "المقاس"
                    ),


                    ui.input_action_button(
                        "next1",
                        "التالي"
                    ),

                    class_="glass-card"

                )



            if step == 2:


                return ui.div(

                    ui.input_select(
                        "v2",
                        "شكل الشاشة",
                        choices=screen_options()
                    ),


                    ui.input_action_button(
                        "next2",
                        "التالي"
                    ),

                    class_="glass-card"

                )



            if step == 3:


                return ui.div(

                    ui.input_select(
                        "v3",
                        "المستشعر",
                        choices=sensor_options()
                    ),


                    ui.input_action_button(
                        "check_spec_match",
                        "فحص"
                    ),

                    class_="glass-card"

                )





        if plan == 22:


            db = cloud_database()


            return ui.HTML(

                run_system_workflows(
                    query,
                    db
                )

            )





        if plan == 3:


            return ui.div(

                ui.h4(
                    "🚨 إضافة مجموعة جديدة"
                ),


                ui.input_action_button(
                    "emergency_save",
                    "حفظ"
                ),


                class_="glass-card"

            )



        return ui.div()





app = App(
    app_ui,
    server
            )
