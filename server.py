import os
import json
import urllib.request

from shiny import ui
from shiny import render
from shiny import reactive

from database import add_model

from silent_monitor.py import (
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


def convert_database_from_raw(rows):

    db = {}

    for item in rows:

        if not isinstance(item, dict):
            continue

        size = str(item.get("size") or "").strip()
        panel = str(item.get("panel") or "").strip()
        sensor = str(item.get("sensor") or "").strip()
        model = str(item.get("model_name") or "").strip()

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


def setup_server_state(input, output, session):

    db_trigger = reactive.Value(0)

    current_search_phone = reactive.Value("")

    show_curtain = reactive.Value(False)

    active_modal = reactive.Value(None)

    p2_computed_results = reactive.Value(None)

    p2_input_size = reactive.Value("")

    p2_input_panel = reactive.Value("")

    p2_input_sensor = reactive.Value("")

    custom_panels = reactive.Value([])

    custom_sensors = reactive.Value([])

    return (

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

    )
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

            print(f"SERVER_DATABASE_ERROR: {e}")

            return {}

    @reactive.effect
    def watcher_refresh():

        db_trigger()

        try:

            refresh()

        except Exception as e:

            print(f"WATCHER_REFRESH_ERROR: {e}")

    @reactive.effect
    @reactive.event(input.search_query)
    def handle_search():

        query = (input.search_query() or "").strip()

        current_search_phone.set(query)

        p2_computed_results.set(None)

        if query:

            show_curtain.set(True)

        else:

            show_curtain.set(False)

    @reactive.effect
    @reactive.event(input.selected_model)
    def select_model():

        value = input.selected_model()

        if value:

            ui.update_text(
                "search_query",
                value=value,
                session=session
            )

            current_search_phone.set(value)

            show_curtain.set(False)

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer():

        await session.send_custom_message(
            "toggle_drawer",
            "open"
        )

    @reactive.effect
    @reactive.event(input.btn_close_drawer_trigger)
    async def close_drawer():

        await session.send_custom_message(
            "toggle_drawer",
            "close"
        )
    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def open_plan_2():

        db = database_data()

        panels = set()

        sensors = set()

        for size, panel_dict in db.items():

            if not isinstance(panel_dict, dict):
                continue

            for panel_name, sensor_dict in panel_dict.items():

                if panel_name:
                    panels.add(panel_name)

                if not isinstance(sensor_dict, dict):
                    continue

                for sensor_name in sensor_dict.keys():

                    if sensor_name:
                        sensors.add(sensor_name)

        custom_panels.set(sorted(list(panels)))

        custom_sensors.set(sorted(list(sensors)))

        active_modal.set("plan_2")

    @reactive.effect
    @reactive.event(input.p2_search)
    def process_plan2():

        size_value = input.p2_size()

        panel_value = input.p2_panel()

        sensor_value = input.p2_sensor()

        if size_value is None:

            return

        if not panel_value:

            return

        if not sensor_value:

            return

        p2_input_size.set(f"{size_value} inches")

        p2_input_panel.set(panel_value)

        p2_input_sensor.set(sensor_value)

        db = database_data()

        compatibles = {

            "exact": [],

            "plus": [],

            "minus": []

        }

        current_size = float(size_value)

        tolerance = 0.05

        for size_key, panel_dict in db.items():

            loop_size = extract_numeric_size(size_key)

            if loop_size is None:

                continue

            diff = loop_size - current_size

            for panel_name, sensor_dict in panel_dict.items():

                if panel_name != panel_value:

                    continue

                for sensor_name, sensor_data in sensor_dict.items():

                    models = sensor_data.get("models", [])

                    for model in models:

                        if abs(diff) < 0.001 and sensor_name == sensor_value:

                            if model not in compatibles["exact"]:

                                compatibles["exact"].append(model)

                        elif 0 < diff <= tolerance:

                            if model not in compatibles["plus"]:

                                compatibles["plus"].append(model)

                        elif -tolerance <= diff < 0:

                            if model not in compatibles["minus"]:

                                compatibles["minus"].append(model)

        if (

            compatibles["exact"]

            or compatibles["plus"]

            or compatibles["minus"]

        ):

            p2_computed_results.set(compatibles)

            active_modal.set(None)

        else:

            p2_computed_results.set("__EMPTY_PLAN2__")

            active_modal.set("plan_3")
    @reactive.effect
    @reactive.event(input.btn_learn_and_merge)
    def learn_current_phone():

        phone = current_search_phone().strip()

        if not phone:

            return

        success = add_model(

            p2_input_size(),

            p2_input_panel(),

            p2_input_sensor(),

            phone

        )

        if success:

            try:

                refresh()

            except Exception:

                pass

            db_trigger.set(

                db_trigger() + 1

            )

            p2_computed_results.set(None)

            ui.update_text(

                "search_query",

                value=phone,

                session=session

            )

    @reactive.effect
    @reactive.event(input.p3_search)
    def create_new_group():

        phone = current_search_phone().strip()

        if not phone:

            return

        size = input.p3_size()

        panel = input.p3_panel()

        sensor = input.p3_sensor()

        if (

            size is None

            or not panel

            or not sensor

        ):

            return

        success = add_model(

            f"{size} inches",

            panel,

            sensor,

            phone

        )

        if success:

            try:

                refresh()

            except Exception:

                pass

            db_trigger.set(

                db_trigger() + 1

            )

            active_modal.set(None)

            p2_computed_results.set(None)
    @render.ui
    def suggestions_curtain():

        if not show_curtain():

            return None

        query = current_search_phone().strip().lower()

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

                    models = sensor_data.get("models", [])

                    for model in models:

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

                    onclick=f"Shiny.setInputValue('selected_model','{model}',{{priority:'event'}});"

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
                    result.get("exact", []),
                    "#2ecc71",
                    "🟢",
                    "exact"
                ),

                draw_neon_section(
                    "أكبر بقليل",
                    result.get("plus", []),
                    "#3498db",
                    "🔵",
                    "plus"
                ),

                draw_neon_section(
                    "أصغر قليلاً",
                    result.get("minus", []),
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

        stats = get_statistics()

        return draw_database_status(

            stats.get("phones", 0)

        )


    @reactive.effect
    def watcher_status():

        try:

            status = get_status()

            if status != "ONLINE":

                print(

                    f"GLASS_WATCHER_STATUS: {status}"

                )

        except Exception as e:

            print(

                f"WATCHER_STATUS_ERROR: {e}"

            )
