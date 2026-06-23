import os
from shiny import App, ui, render, reactive
from supabase import create_client

from workflows import run_system_workflows
from ui_components import inject_pwa_and_styles



SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)





def convert_database(rows):

    db = {}


    for item in rows:


        size = str(item.get("size","")).strip()

        panel = str(item.get("panel","")).strip()

        sensor = str(item.get("sensor","")).strip()

        model = str(item.get("model_name","")).strip()



        if not size or not model:

            continue



        db.setdefault(size,{})

        db[size].setdefault(panel,{})

        db[size][panel].setdefault(
            sensor,
            {
                "models":[]
            }
        )



        if model not in db[size][panel][sensor]["models"]:

            db[size][panel][sensor]["models"].append(model)



    return db







app_ui = ui.page_fluid(


    inject_pwa_and_styles(),



    ui.HTML("""

<script>

function openDrawer(){

let d=document.getElementById(
'settings_drawer'
);

if(d){

d.classList.add('open');

}

}



function closeDrawer(){

let d=document.getElementById(
'settings_drawer'
);

if(d){

d.classList.remove('open');

}

}

</script>

"""),






    ui.div(


        ui.h3(
            "⚙️ الإعدادات",
            style="color:#00bfff;"
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
            class_="btn-neon"
        ),



        id="settings_drawer",

        class_="drawer"

    ),







    ui.div(


        ui.div(

            ui.h2(
                "ZEGAAR AMMAR",
                style="color:#00bfff;margin:0;"
            ),


            ui.h3(
                "GLASS MANAGER",
                style="color:white;margin:0;"
            ),

        ),



        ui.input_action_button(
            "btn_settings",
            "⚙️",
            class_="btn-neon"
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




    ui.output_ui(
        "results_area"
    )

)









def server(input, output, session):




    @reactive.calc

    def cloud_rows():


        try:


            response = (

                supabase
                .table("phones")
                .select("*")
                .execute()

            )


            return response.data or []



        except Exception as e:


            print(
                "Supabase Error:",
                e
            )


            return []








    @reactive.calc

    def database():


        return convert_database(
            cloud_rows()
        )









    @reactive.effect

    @reactive.event(
        input.btn_settings
    )

    def open_drawer():

        ui.insert_ui(

            ui.HTML(
                "<script>openDrawer();</script>"
            ),

            selector="body"

        )








    @reactive.effect

    @reactive.event(
        input.close_drawer
    )

    def close_drawer():

        ui.insert_ui(

            ui.HTML(
                "<script>closeDrawer();</script>"
            ),

            selector="body"

        )









    @render.ui

    def suggestions_curtain():


        q = (

            input.search_query()
            .strip()
            .lower()

        )



        if not q:

            return None



        matches=[]



        for row in cloud_rows():


            name = str(
                row.get(
                    "model_name",
                    ""
                )
            )



            if q in name.lower():


                matches.append(name)




        matches=list(
            dict.fromkeys(matches)
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
                    '{name}'
                    );

                    """

                )


                for name in matches

            ],


            class_="suggestions-curtain"

        )









    @reactive.effect

    @reactive.event(
        input.selected_model
    )

    def fill_search():


        ui.update_text(

            "search_query",

            value=input.selected_model()

        )









    @render.ui

    def results_area():


        phone = (

            input.search_query()
            .strip()

        )



        if not phone:

            return None




        result = run_system_workflows(

            phone,

            database(),

            None

        )



        if not result:

            return None




        return ui.HTML(
            result
        )









app = App(

    app_ui,

    server

)
