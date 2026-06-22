import os
import json
import re

from shiny import App, ui, render, reactive
from supabase import create_client, Client
from dotenv import load_dotenv

from ui_components import inject_pwa_and_styles, draw_control_panel


# ==========================================================
# Supabase
# ==========================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)



# ==========================================================
# Workflow
# ==========================================================

try:

    from workflows import run_system_workflows


except Exception:


    def run_system_workflows(model, db, suggestions):

        return f"""

        <div class="glass-card">

        <h3 class="neon-text">
        {model}
        </h3>

        <p>
        Workflow غير متوفر
        </p>

        </div>

        """




# ==========================================================
# Local index
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
# تنظيف أسماء الموديلات
# ==========================================================

def clean_name(text):

    return re.sub(
        r"\s+",
        " ",
        str(text)
        .lower()
        .strip()
    )





# ==========================================================
# تحويل Supabase لبنية المحرك
# ==========================================================

def build_workflow_db(rows):


    database = {}


    for row in rows:


        model = str(
            row.get("model_name","")
        ).strip()


        size = str(
            row.get("size","")
        ).strip()


        panel = str(
            row.get("panel","")
        ).strip()


        sensor = str(
            row.get("sensor","")
        ).strip()



        if not model or not size:

            continue



        database.setdefault(
            size,
            {}
        )


        database[size].setdefault(
            panel,
            {}
        )


        database[size][panel].setdefault(
            sensor,
            {
                "models":[]
            }
        )



        if model not in database[size][panel][sensor]["models"]:

            database[size][panel][sensor]["models"].append(model)



    return database





# ==========================================================
# واجهة التطبيق
# ==========================================================


app_ui = ui.page_fluid(


    ui.HTML(
        inject_pwa_and_styles()
    ),



    ui.HTML("""

    <div class="header-bar">

    <div
    onclick="
    document.getElementById('drawer')
    .classList.toggle('open')"

    style="
    font-size:28px;
    cursor:pointer;
    color:#00bfff">

    ☰

    </div>


    <div>

    <h2 class="neon-text">
    ZEGAAR AMMAR
    </h2>


    <div style="
    color:#aaa;
    text-align:center">

    GLASS MANAGER

    </div>


    </div>


    </div>


    <div id="drawer" class="drawer">

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
# Server
# ==========================================================


def server(inp, output, session):


    refresh = reactive.value(0)


    current_plan = reactive.value(0)


    show_suggestions = reactive.value(False)
@reactive.calc
    def cloud_database():

        refresh.get()

        try:

            result = (
                supabase
                .table("phones")
                .select("*")
                .execute()
            )


            return result.data or []


        except Exception as e:


            print(
                "Supabase error:",
                e
            )


            return []





    @render.ui
    def control_panel():


        return draw_control_panel(

            total_models=len(
                cloud_database()
            )

        )





    @reactive.effect
    @reactive.event(inp.search_query)
    def typing():


        show_suggestions.set(True)


        current_plan.set(0)





# ==========================================================
# Auto complete
# ==========================================================


    @render.ui
    def suggestions_curtain_ui():


        if not show_suggestions():

            return ui.div()



        q = clean_name(
            inp.search_query()
        )



        if not q:

            return ui.div()



        data = load_local_json()



        models = list(
            data.keys()
        )



        if not models:


            models = [

                x.get("model_name")

                for x in cloud_database()

                if x.get("model_name")

            ]



        matches = [


            m for m in models

            if q in clean_name(m)


        ][:8]



        if not matches:

            return ui.div()



        return ui.div(


            *[

            ui.div(

                f"📱 {m}",

                class_="suggestion-row",

                onclick=f"""

                Shiny.setInputValue(
                'selected_model',
                '{m}',
                {{priority:'event'}}
                )

                """

            )

            for m in matches


            ],


            class_="suggestions-curtain"


        )





    @reactive.effect
    @reactive.event(inp.selected_model)
    def select_model():


        value = inp.selected_model()



        ui.update_text(

            "search_query",

            value=value

        )



        show_suggestions.set(False)





# ==========================================================
# البحث الحقيقي
# ==========================================================


    @reactive.effect
    @reactive.event(inp.btn_search)
    def search_phone():


        show_suggestions.set(False)



        query = clean_name(
            inp.search_query()
        )



        if not query:


            ui.notification_show(

                "اكتب اسم الهاتف",

                type="warning"

            )


            return





        rows = cloud_database()



        phone = next(

            (

            x for x in rows

            if clean_name(
                x.get("model_name","")
            )
            ==
            query

            ),

            None

        )





        if phone:


            current_plan.set(1)



        else:


            ui.notification_show(

                "الموديل غير موجود بالاسم",

                type="warning"

            )


            current_plan.set(2)





# ==========================================================
# عرض النتائج
# ==========================================================


    @render.ui
    def main_content_ui():


        if show_suggestions():

            return ui.div()



        plan = current_plan()



        query = inp.search_query()



        if plan == 1:


            rows = cloud_database()



            workflow_db = build_workflow_db(
                rows
            )



            return ui.HTML(


                run_system_workflows(

                    query,

                    workflow_db,

                    []

                )


            )





        if plan == 2:


            return ui.div(

                ui.h4(
                    "الخطة 2 - إدخال المواصفات"
                ),


                ui.p(
                    "سيتم تشغيلها بعد فشل الاسم"
                ),


                class_="glass-card"


            )



        return ui.div()





app = App(

    app_ui,

    server

        )
