import os,json
from shiny import App,ui,render,reactive
from supabase import create_client,Client
from dotenv import load_dotenv

from ui_components import inject_pwa_and_styles,draw_control_panel

load_dotenv()

SUPABASE_URL=os.getenv("SUPABASE_URL","")
SUPABASE_KEY=os.getenv("SUPABASE_KEY","")

supabase:Client=create_client(SUPABASE_URL,SUPABASE_KEY)

try:
    from workflows import run_system_workflows
except:
    def run_system_workflows(model,db,suggestions=None):
        return f"""
        <div class="glass-card">
        <h3 class="neon-text">{model}</h3>
        <p>Workflow غير متوفر</p>
        </div>
        """

JSON_INDEX_PATH="models_id_db.json"


def load_local_json():
    if os.path.exists(JSON_INDEX_PATH):
        try:
            with open(JSON_INDEX_PATH,"r",encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_local_json(data):
    try:
        with open(JSON_INDEX_PATH,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
    except Exception as e:
        print(e)


def convert_supabase_to_workflow(rows):
    db={}

    for x in rows:
        size=str(x.get("size","")).strip()
        panel=str(x.get("panel","")).strip()
        sensor=str(x.get("sensor","")).strip()
        model=str(x.get("model_name","")).strip()

        if not size or not model:
            continue

        db.setdefault(size,{})
        db[size].setdefault(panel,{})
        db[size][panel].setdefault(sensor,{"models":[]})

        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)

    return db


app_ui=ui.page_fluid(

    ui.HTML(inject_pwa_and_styles()),

    ui.HTML("""
    <div id="drawer" class="drawer">
        <h3 class="neon-text">🛠️ لوحة التحكم</h3>
        <div id="drawer-content"></div>
    </div>

    <div class="header-bar">
        <div onclick="document.getElementById('drawer').classList.toggle('open')"
        style="font-size:28px;cursor:pointer;color:#00bfff">
        ☰
        </div>

        <h2 style="color:#00bfff">
        ZEGAAR AMMAR
        </h2>
    </div>
    """),

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



def server(input,output,session):

    refresh_trigger=reactive.value(0)
    current_plan=reactive.value(0)
    wizard_step=reactive.value(1)

    show_suggestions=reactive.value(False)

    screen_options=reactive.value([
        "Notch",
        "Punch",
        "Curved"
    ])

    sensor_options=reactive.value([
        "hardware",
        "under_display"
    ])


    @reactive.calc
    def cloud_database():

        refresh_trigger.get()

        try:
            r=supabase.table("phones").select("*").execute()
            return r.data or []
        except Exception as e:
            print(e)
            return []


    @render.ui
    def control_panel():

        return draw_control_panel(
            total_models=len(cloud_database())
        )


    @render.text
    def model_count_display():

        return f"📱 عدد الموديلات: {len(cloud_database())}"


    @reactive.effect
    @reactive.event(input.search_query)
    def reset_search():

        show_suggestions.set(True)

        if current_plan()!=0:
            current_plan.set(0)
@render.ui
    def suggestions_curtain_ui():

        if not show_suggestions():
            return ui.div()

        q=input.search_query().strip().lower()

        if not q:
            return ui.div()


        local=load_local_json()

        models=list(local.keys())


        if not models:
            models=[
                x.get("model_name")
                for x in cloud_database()
                if x.get("model_name")
            ]


        matches=[
            m for m in models
            if m and q in str(m).lower()
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



    @reactive.effect
    @reactive.event(input.clicked_outside)
    def close_suggestion():

        show_suggestions.set(False)



    @reactive.effect
    @reactive.event(input.selected_suggestion)
    def select_suggestion():

        value=input.selected_suggestion()

        ui.update_text(
            "search_query",
            value=value
        )

        show_suggestions.set(False)



    @reactive.effect
    @reactive.event(input.btn_search)
    def search_phone():

        show_suggestions.set(False)

        query=input.search_query().strip()


        if not query:

            ui.notification_show(
                "اكتب اسم الهاتف أولاً",
                type="warning"
            )

            return



        db=cloud_database()


        phone=next(
            (
                x for x in db
                if str(x.get("model_name","")).lower()
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

            ui.notification_show(
                "الموديل غير مطابق بالاسم، الانتقال للخطة 2",
                type="warning"
            )



    @render.ui
    def main_content_ui():

        plan=current_plan()

        query=input.search_query().strip()


        if not query:

            return ui.div()



        if plan==1:

            db=convert_supabase_to_workflow(
                cloud_database()
            )


            return ui.HTML(
                run_system_workflows(
                    query,
                    db,
                    None
                )
            )



        if plan==2:

            step=wizard_step()


            if step==1:

                return ui.div(

                    ui.h4(
                    "📏 الخطة 2 - المقاس",
                    class_="neon-text"
                    ),

                    ui.input_text(
                    "v1",
                    "أدخل المقاس:"
                    ),

                    ui.input_action_button(
                    "next1",
                    "التالي ➡️",
                    class_="btn-neon"
                    ),

                    class_="glass-card"
                )



            if step==2:

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
                    "التالي ➡️",
                    class_="btn-neon"
                    ),

                    class_="glass-card"
                )



            if step==3:

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
                    "فحص 🔍",
                    class_="btn-neon"
                    ),

                    class_="glass-card"
                )



        if plan==22:

            db=cloud_database()


            size=input.v1()
            panel=input.v2()
            sensor=input.v3()


            result=[

                x for x in db

                if str(x.get("size"))==size
                and str(x.get("panel")).lower()==panel.lower()
                and str(x.get("sensor")).lower()==sensor.lower()

            ]


            cards="".join(

                [
                f"""
                <div class="ammar-flat-card flat-exact">
                <div class="flat-phone-text">
                📱 {x.get('model_name')}
                </div>
                </div>
                """
                for x in result
                ]

            )


            return ui.HTML(
                cards
            )



        if plan==3:

            return ui.div(

                ui.h4(
                "🚨 خطة الطوارئ",
                class_="neon-text"
                ),

                ui.p(
                f"الموديل: {query}"
                ),

                ui.input_action_button(
                "emergency_save",
                "حفظ 💾",
                class_="btn-neon"
                ),

                class_="glass-card"
            )


        return ui.div()



    @reactive.effect
    @reactive.event(input.next1)
    def next_step_one():

        if input.v1().strip():

            wizard_step.set(2)



    @reactive.effect
    @reactive.event(input.next2)
    def next_step_two():

        wizard_step.set(3)



    @reactive.effect
    @reactive.event(input.check_spec_match)
    def check_specs():

        db=cloud_database()

        size=input.v1()
        panel=input.v2()
        sensor=input.v3()


        ok=[

        x for x in db

        if str(x.get("size")).strip()==size.strip()
        and str(x.get("panel")).lower()==panel.lower()
        and str(x.get("sensor")).lower()==sensor.lower()

        ]


        if ok:

            current_plan.set(22)

        else:

            current_plan.set(3)



app=App(
    app_ui,
    server
        )
    
