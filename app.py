import os
import json

from shiny import App, ui, render, reactive
from supabase import create_client, Client
from dotenv import load_dotenv

from ui_components import inject_pwa_and_styles, draw_control_panel


# ======================================
# Supabase
# ======================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ======================================
# Workflow
# ======================================

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


# ======================================
# Local JSON index
# ======================================

JSON_INDEX_PATH = "models_id_db.json"


def load_local_json():

    if not os.path.exists(JSON_INDEX_PATH):
        return {}

    try:

        with open(
            JSON_INDEX_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

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



# ======================================
# تحويل Supabase إلى قاعدة workflow
# ======================================

def convert_supabase_to_workflow(rows):

    database = {}


    for phone in rows:

        size = str(phone.get("size","")).strip()
        panel = str(phone.get("panel","")).strip()
        sensor = str(phone.get("sensor","")).strip()
        model = str(phone.get("model_name","")).strip()


        if not size or not model:
            continue


        database.setdefault(size,{})
        database[size].setdefault(panel,{})
        database[size][panel].setdefault(
            sensor,
            {"models":[]}
        )


        if model not in database[size][panel][sensor]["models"]:

            database[size][panel][sensor]["models"].append(model)


    return database



# ======================================
# UI
# ======================================

app_ui = ui.page_fluid(


    ui.HTML(
        inject_pwa_and_styles()
    ),



    ui.HTML("""
    <div class="header-bar">

        <div
        onclick="document.getElementById('drawer').classList.toggle('open')"
        style="font-size:28px;color:#00bfff;cursor:pointer">

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



# ======================================
# SERVER
# ======================================

def server(input, output, session):


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

            result = (

                supabase
                .table("phones")
                .select("*")
                .execute()

            )


            return result.data or []


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



    @reactive.effect

    @reactive.event(input.search_query)

    def search_change():


        show_suggestions.set(True)


        if current_plan() != 0:

            current_plan.set(0)
@render.ui
def suggestions_curtain_ui():

    if not show_suggestions():
        return ui.div()


    q = input.search_query().strip().lower()


    if not q:
        return ui.div()



    local_data = load_local_json()


    if local_data:

        models = list(local_data.keys())

    else:

        models = [
            x.get("model_name")
            for x in cloud_database()
            if x.get("model_name")
        ]



    matches = [

        m for m in models

        if m and q in str(m).lower()

    ][:8]



    if not matches:

        return ui.div()



    rows = []


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

                );

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

            );

            """

        ),



        ui.div(

            *rows,

            class_="suggestions-curtain"

        )

    )



# ==============================
# إغلاق الستارة
# ==============================

@reactive.effect
def close_curtain():


    try:

        value = input.clicked_outside()

        if value:

            show_suggestions.set(False)

    except:

        pass




# اختيار موديل من الاقتراحات
# ==============================

@reactive.effect
def select_suggestion():


    try:

        choice = input.selected_suggestion()


        if choice:


            ui.update_text(

                "search_query",

                value=choice

            )


            show_suggestions.set(False)


    except:

        pass




# ==============================
# زر البحث
# ==============================

@reactive.effect

@reactive.event(input.btn_search)

def search_phone():


    show_suggestions.set(False)


    query = input.search_query().strip()



    if not query:


        ui.notification_show(

            "اكتب اسم الهاتف أولا",

            type="warning"

        )

        return



    db = cloud_database()



    phone = next(

        (

            x for x in db

            if str(

                x.get("model_name","")

            ).strip().lower()

            ==

            query.lower()

        ),

        None

    )



    if phone:


        current_plan.set(1)



    else:


        current_plan.set(2)

        wizard_step.set(1)



# ==============================
# الخطة 2
# ==============================


@reactive.effect

@reactive.event(input.next1)

def next_step_one():


    if not input.v1().strip():


        ui.notification_show(

            "أدخل المقاس",

            type="error"

        )

        return



    wizard_step.set(2)




@reactive.effect

@reactive.event(input.next2)

def next_step_two():


    wizard_step.set(3)




@reactive.effect

@reactive.event(input.check_spec_match)

def check_match():


    db = cloud_database()


    size = input.v1().strip()

    panel = input.v2()

    sensor = input.v3()



    matches = [

        x for x in db

        if str(x.get("size","")).strip()

        == size


        and str(x.get("panel","")).lower()

        == str(panel).lower()


        and str(x.get("sensor","")).lower()

        == str(sensor).lower()

    ]



    if matches:


        current_plan.set(22)


    else:


        current_plan.set(3)




# ==============================
# عرض النتائج
# ==============================

@render.ui

def main_content_ui():


    plan = current_plan()

    query = input.search_query().strip()



    if not query or show_suggestions():

        return ui.div()



    if plan == 1:


        workflow_db = convert_supabase_to_workflow(

            cloud_database()

        )


        return ui.HTML(

            run_system_workflows(

                query,

                workflow_db

            )

        )



    if plan == 2:


        step = wizard_step()



        if step == 1:


            return ui.div(

                ui.h4(

                    "📏 المقاس",

                    class_="neon-text"

                ),

                ui.input_text(

                    "v1",

                    "مثال 6.7"

                ),

                ui.input_action_button(

                    "next1",

                    "التالي"

                ),

                class_="glass-card"

            )



        if step == 2:


            return ui.div(

                ui.h4(

                    "📺 شكل الشاشة",

                    class_="neon-text"

                ),

                ui.input_select(

                    "v2",

                    "",

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

                ui.h4(

                    "🔌 المستشعر",

                    class_="neon-text"

                ),

                ui.input_select(

                    "v3",

                    "",

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



        html = "".join(

            f"<div>📱 {x.get('model_name')}</div>"

            for x in db

        )


        return ui.HTML(

            f"""

            <div class="glass-card">

            <h3 class="neon-text">

            الهواتف المطابقة

            </h3>

            {html}

            </div>

            """

        )



    if plan == 3:


        return ui.div(

            ui.h3(

                "🚨 خطة الطوارئ",

                class_="neon-text"

            ),

            ui.p(

                "الموديل غير موجود ويمكن إضافته"

            ),

            class_="glass-card"

        )



    return ui.div()



# ==============================
# تشغيل التطبيق
# ==============================

app = App(

    app_ui,

    server

)
