import os
import json
from shiny import App, ui, render, reactive
from supabase import create_client

from workflows import run_system_workflows, get_compatibles_strict
from ui_components import (
    inject_pwa_and_styles,
    draw_plan_2_modal,
    draw_plan_3_modal
)


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def convert_database(rows):
    db = {}

    for item in rows:
        size = str(item.get("size", "")).strip()
        panel = str(item.get("panel", "")).strip()
        sensor = str(item.get("sensor", "")).strip()
        model = str(item.get("model_name", "")).strip()

        if not size or not model:
            continue

        db.setdefault(size, {})
        db[size].setdefault(panel, {})
        db[size][panel].setdefault(
            sensor,
            {"models": []}
        )

        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)

    return db



app_ui = ui.page_fluid(

    inject_pwa_and_styles(),

    ui.HTML("""
    <script>
    Shiny.addCustomMessageHandler(
        'toggle_drawer',
        function(msg){
            let d=document.getElementById('settings_drawer');

            if(d){
                if(msg === 'open'){
                    d.classList.add('open');
                }
                else{
                    d.classList.remove('open');
                }
            }
        }
    );
    </script>
    """),


    ui.div(
        ui.h3(
            "⚙️ الإعدادات",
            style="color:#00bfff;text-align:right;"
        ),

        ui.div(
            "🔔 الإشعارات نشطة",
            class_="metric-box"
        ),

        ui.div(
            "🛡️ المراقب الصامت يعمل",
            class_="metric-box"
        ),

        ui.input_action_button(
            "close_drawer",
            "إغلاق",
            class_="btn-neon",
            style="width:100%;"
        ),

        id="settings_drawer",
        class_="drawer"
    ),



    ui.div(

        ui.div(
            ui.h2(
                "ZEGAAR AMMAR",
                style="color:#00bfff;margin:0;font-weight:900;"
            ),

            ui.h3(
                "GLASS MANAGER",
                style="color:white;margin:0;letter-spacing:2px;"
            )
        ),

        ui.input_action_button(
            "btn_settings",
            "⚙️",
            class_="btn-neon",
            style="font-size:20px;padding:10px 15px;"
        ),

        class_="header-bar"
    ),



    ui.div(

        ui.input_text(
            "search_query",
            "",
            placeholder="🔍 ابحث عن موديل الهاتف..."
        ),

        ui.output_ui(
            "suggestions_curtain"
        ),

        class_="search-box"

    ),


    ui.output_ui("results_area"),

    ui.output_ui("modal_layer")

)



def server(input, output, session):


    db_trigger = reactive.Value(0)

    current_search_phone = reactive.Value("")

    show_curtain = reactive.Value(False)

    active_modal = reactive.Value(None)

    custom_panels = reactive.Value([])

    custom_sensors = reactive.Value([])

    is_programmatic_update = reactive.Value(False)



    @reactive.calc
    def cloud_rows():

        db_trigger()

        try:
            res = (
                supabase
                .table("phones")
                .select("*")
                .execute()
            )

            return res.data or []

        except Exception as e:

            print("Supabase Error:", e)

            return []



    @reactive.calc
    def database():

        return convert_database(
            cloud_rows()
        )



    @reactive.calc
    def unique_panels():

        data = {
            str(x.get("panel","")).strip()
            for x in cloud_rows()
        }

        data.update(custom_panels())

        return sorted(
            x for x in data if x
        )



    @reactive.calc
    def unique_sensors():

        data = {
            str(x.get("sensor","")).strip()
            for x in cloud_rows()
        }

        data.update(custom_sensors())

        return sorted(
            x for x in data if x
        )



    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer():

        await session.send_custom_message(
            "toggle_drawer",
            "open"
        )



    @reactive.effect
    @reactive.event(input.close_drawer)
    async def close_drawer():

        await session.send_custom_message(
            "toggle_drawer",
            "close"
        )



    @reactive.effect
    @reactive.event(input.search_query)
    def track_search():

        if is_programmatic_update():

            is_programmatic_update.set(False)

        else:

            show_curtain.set(True)



    @render.ui
    def suggestions_curtain():

        if not show_curtain():
            return None


        q = (
            input.search_query()
            .strip()
            .lower()
        )


        if not q:
            return None



        matches = list(
            dict.fromkeys(
                str(r.get("model_name",""))
                for r in cloud_rows()
                if q in str(r.get("model_name","")).lower()
            )
        )[:8]



        if not matches:
            return None



        return ui.div(

            *[

                ui.div(

                    name,

                    class_="suggestion-row",

                    onclick=f"""
                    Shiny.setInputValue(
                    'selected_model',
                    {json.dumps(name)},
                    {{priority:'event'}}
                    )
                    """

                )

                for name in matches

            ],

            class_="suggestions-curtain"

        )



    @reactive.effect
    @reactive.event(input.selected_model)
    def fill_search():

        is_programmatic_update.set(True)

        ui.update_text(
            "search_query",
            value=input.selected_model()
        )

        show_curtain.set(False)



    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def launch_plan_2():

        current_search_phone.set(
            input.trigger_plan_2()
        )

        active_modal.set(
            "plan_2"
        )



    @render.ui
    def modal_layer():

        m = active_modal()


        if m == "plan_2":

            return draw_plan_2_modal(
                current_search_phone(),
                unique_panels(),
                unique_sensors()
            )


        if m == "plan_3":

            return draw_plan_3_modal(
                current_search_phone(),
                input.p2_size(),
                input.p2_panel(),
                input.p2_sensor()
            )


        return None



    @reactive.effect
    @reactive.event(input.p2_cancel)
    def cancel_p2():

        active_modal.set(None)



    @reactive.effect
    @reactive.event(input.p2_search)
    def process_p2():

        compat = get_compatibles_strict(
            database(),
            str(input.p2_size() or ""),
            input.p2_panel(),
            input.p2_sensor(),
            current_search_phone()
        )


        if (
            compat["exact"]
            or compat["plus"]
            or compat["minus"]
        ):

            active_modal.set(None)

        else:

            active_modal.set("plan_3")



    @render.ui
    def results_area():

        p = (
            input.search_query()
            .strip()
        )


        if not p:
            return None


        return ui.HTML(
            run_system_workflows(
                p,
                database(),
                None
            )
        )



app = App(
    app_ui,
    server
    )
