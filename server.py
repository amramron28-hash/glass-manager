import os
import json
import urllib.request

from shiny import ui
from shiny import render
from shiny import reactive

from database import add_model

from silent_monitor import (
    get_database,
    refresh,
    get_status,
    get_statistics
)

from logic_engine import (
    run_system_workflows,
    get_compatibles_strict,
    find_model_coords,
    extract_numeric_size
)

from ui_components import (
    draw_plan_2_modal,
    draw_plan_3_modal,
    draw_warning_card,
    draw_technical_coords,
    draw_neon_section,
    draw_database_status
)


MODELS_INDEX_FILE = "models_index.txt"


def load_models_index():

    try:

        with open(
            MODELS_INDEX_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return [
                line.strip()
                for line in f
                if line.strip()
            ]

    except Exception:

        return []


def convert_database_from_raw(rows):

    db = {}

    if not isinstance(rows, list):
        return db

    for item in rows:

        if not isinstance(item, dict):
            continue

        size = str(
            item.get("size") or ""
        ).strip()

        panel = str(
            item.get("panel") or ""
        ).strip()

        sensor = str(
            item.get("sensor") or ""
        ).strip()

        model = str(
            item.get("model_name") or ""
        ).strip()


        if not size or not model:
            continue


        db.setdefault(size, {})
        db[size].setdefault(panel, {})
        db[size][panel].setdefault(
            sensor,
            {
                "models": []
            }
        )


        if model not in db[size][panel][sensor]["models"]:

            db[size][panel][sensor]["models"].append(model)


    return db



def server(input, output, session):


    (
        db_trigger,
        current_search_phone,
        show_curtain,
        active_modal,
        p2_computed_results,
        p2_input_size,
        p2_input_panel,
        p2_input_sensor,
        custom_panels,
        custom_sensors

    ) = setup_server_state(
        input,
        output,
        session
    )


    models_index = reactive.Value(
        load_models_index()
    )



    @reactive.calc
    def database_data():

        db_trigger()

        try:

            db = get_database()


            if isinstance(db, dict):

                return db


            if isinstance(db, list):

                return convert_database_from_raw(db)


            return {}


        except Exception as e:


            print(
                f"SERVER_DATABASE_ERROR: {e}"
            )

            return {}



    @reactive.effect
    def watcher_refresh():


        db_trigger()


        try:


            refresh()


            models_index.set(
                load_models_index()
            )


        except Exception as e:


            print(
                f"WATCHER_REFRESH_ERROR: {e}"
            )



    @render.ui
    def suggestions_curtain():


        if not show_curtain():

            return None



        query = (
            current_search_phone()
            .strip()
            .lower()
        )


        if not query:

            return None



        db = database_data()


        all_models = set()



        for size, panels in db.items():


            if not isinstance(panels, dict):

                continue



            for panel, sensors in panels.items():


                if not isinstance(sensors, dict):

                    continue



                for sensor, sensor_data in sensors.items():


                    if not isinstance(sensor_data, dict):

                        continue



                    for model in sensor_data.get(
                        "models",
                        []
                    ):

                        all_models.add(model)



        matches = [

            model

            for model in sorted(all_models)

            if query in model.lower()

        ][:8]



        if not matches:

            return None



        return ui.div(

            *[

                ui.div(

                    model,

                    class_="suggestion-row",

                    onclick=(
                        f"Shiny.setInputValue("
                        f"'selected_model','{model}',"
                        f"{{priority:'event'}});"
                    )

                )

                for model in matches

            ],

            class_="suggestions-curtain"

            )
    @render.ui
    def results_area():


        phone = current_search_phone().strip()


        if not phone:

            return None



        db = database_data()



        size, panel, sensor, real_name = find_model_coords(

            db,

            phone

        )



        if real_name:


            return ui.HTML(

                run_system_workflows(

                    phone,

                    db,

                    ""

                )

            )



        result = p2_computed_results()



        if isinstance(result, dict):


            return ui.div(


                draw_technical_coords(

                    p2_input_size(),

                    p2_input_panel(),

                    p2_input_sensor(),

                    f"{phone} (مواصفات يدوية)"

                ),



                draw_neon_section(

                    "مطابقة تماماً",

                    result.get(
                        "exact",
                        []
                    ),

                    "#2ecc71",

                    "🟢",

                    "exact"

                ),



                draw_neon_section(

                    "أكبر بقليل",

                    result.get(
                        "plus",
                        []
                    ),

                    "#3498db",

                    "🔵",

                    "plus"

                ),



                draw_neon_section(

                    "أصغر قليلاً",

                    result.get(
                        "minus",
                        []
                    ),

                    "#e67e22",

                    "🟠",

                    "minus"

                ),



                ui.input_action_button(

                    "btn_learn_and_merge",

                    "🔄 دمج الهاتف داخل هذه المجموعة",

                    style="""
                    width:100%;
                    background:#2ecc71;
                    color:white;
                    padding:14px;
                    border:none;
                    border-radius:12px;
                    font-weight:bold;
                    margin-top:15px;
                    """

                )


            )




        if result == "__EMPTY_PLAN2__":


            return ui.div(


                draw_warning_card(

                    "لم يتم العثور على مجموعة مطابقة، سيتم إنشاء مجموعة جديدة."

                )

            )




        return ui.div(



            draw_warning_card(

                f"الموديل {phone} غير موجود داخل قاعدة البيانات."

            ),



            ui.input_action_button(

                "trigger_plan_2",

                "🔵 بدء المطابقة الفنية",


                style="""
                width:100%;
                background:#00bfff;
                color:white;
                padding:14px;
                border:none;
                border-radius:12px;
                font-weight:bold;
                """

            )


        )




    @render.ui
    def modal_layer():


        mode = active_modal()



        if mode == "plan_2":


            return draw_plan_2_modal(

                current_search_phone(),

                custom_panels(),

                custom_sensors()

            )



        if mode == "plan_3":


            return draw_plan_3_modal(

                current_search_phone(),

                custom_panels(),

                custom_sensors()

            )



        return None





    @render.ui
    def database_status_area():


        try:


            stats = get_statistics()



            if not isinstance(stats, dict):

                stats = {}



            return draw_database_status(

                stats.get(
                    "phones",
                    0
                )

            )


        except Exception as e:


            print(

                f"DATABASE_STATUS_ERROR: {e}"

            )


            return draw_database_status(0)





    @reactive.effect
    def watcher_status():


        try:


            status = get_status()



            if isinstance(status, dict):


                current = status.get(
                    "status"
                )


                if current != "ONLINE":


                    print(

                        f"SILENT_MONITOR_STATUS: {status}"

                    )


            else:


                print(

                    f"SILENT_MONITOR_STATUS: {status}"

                )



        except Exception as e:


            print(

                f"WATCHER_STATUS_ERROR: {e}"

            )



# =========================
# End of server.py
# =========================
