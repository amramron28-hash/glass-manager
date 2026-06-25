import os

from shiny import ui, render, reactive
from supabase import create_client

from logic_engine import (
    run_system_workflows,
    get_compatibles_strict
)

from ui_components import (
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

        if not isinstance(item, dict):
            continue


        size = str(item.get("size") or "").strip()
        panel = str(item.get("panel") or "").strip()
        sensor = str(item.get("sensor") or "").strip()
        model = str(item.get("model_name") or "").strip()


        if not size or not model:
            continue


        db.setdefault(size, {}) \
          .setdefault(panel, {}) \
          .setdefault(sensor, {"models": []})


        if model not in db[size][panel][sensor]["models"]:

            db[size][panel][sensor]["models"].append(model)


    return db




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

            result = (
                supabase
                .table("phones")
                .select("*")
                .execute()
            )


            return result.data or []


        except Exception as e:

            print("DATABASE ERROR:", e)

            return []





    @reactive.calc
    def database():

        return convert_database(
            cloud_rows()
        )





    @reactive.calc
    def unique_panels():

        values = {

            str(r.get("panel") or "").strip()

            for r in cloud_rows()

            if r.get("panel")

        }


        values.update(
            custom_panels()
        )


        return sorted(
            list(values)
        )





    @reactive.calc
    def unique_sensors():

        values = {

            str(r.get("sensor") or "").strip()

            for r in cloud_rows()

            if r.get("sensor")

        }


        values.update(
            custom_sensors()
        )


        return sorted(
            list(values)
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






    @render.ui
    def drawer_status_area():

        total = len(
            cloud_rows()
        )


        return ui.div(

            ui.div(

                f"📊 إجمالي الهواتف: {total}",

                class_="metric-box"

            )

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



        q = input.search_query().strip().lower()


        if not q:

            return None




        matches = [

            str(r.get("model_name") or "").strip()

            for r in cloud_rows()

        ]



        matches = list(

            set(

                [

                    m for m in matches

                    if q in m.lower()

                ]

            )

        )[:8]




        if not matches:

            return None




        return ui.div(

            *[

                ui.div(

                    m,

                    class_="suggestion-row",

                    onclick=f"""

                    Shiny.setInputValue(

                    'selected_model',

                    '{m.replace(chr(39), chr(92)+chr(39))}',

                    {{priority:'event'}}

                    );

                    """

                )

                for m in matches

            ],

            class_="suggestions-curtain"

        )







    @reactive.effect
    @reactive.event(input.selected_model)
    def fill_search():


        is_programmatic_update.set(True)


        current_search_phone.set(
            input.selected_model()
        )


        ui.update_text(

            "search_query",

            value=input.selected_model()

        )


        show_curtain.set(False)







    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def open_plan_2():


        if not current_search_phone():

            current_search_phone.set(

                input.search_query().strip()

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

                unique_panels(),

                unique_sensors()

            )



        return None







    @reactive.effect
    @reactive.event(input.p2_search)
    def process_p2():


        compat = get_compatibles_strict(

            database(),

            str(input.p2_size() or ""),

            str(input.p2_panel() or ""),

            str(input.p2_sensor() or ""),

            str(current_search_phone() or "")

        )


        exact = compat.get("exact", [])

        plus = compat.get("plus", [])

        minus = compat.get("minus", [])




        if exact or plus or minus:


            active_modal.set(None)


            result_html = ""



            if exact:

                result_html += """
                <div class="neon-glass-card">
                🟢 مطابقة تماماً
                </div>
                """

                result_html += "<br>".join(map(str, exact))




            if plus:

                result_html += """
                <div class="neon-glass-card">
                🔵 أكبر بقليل ±0.03
                </div>
                """

                result_html += "<br>".join(map(str, plus))




            if minus:

                result_html += """
                <div class="neon-glass-card">
                🟠 أصغر قليلاً ±0.03
                </div>
                """

                result_html += "<br>".join(map(str, minus))





            ui.modal_show(

                ui.modal(

                    ui.h3(
                        "🎉 تم العثور على موديلات متوافقة"
                    ),

                    ui.HTML(result_html),

                    ui.hr(),

                    ui.p(
                        "هل تريد دمج الهاتف الجديد داخل هذه المجموعة؟"
                    ),

                    ui.input_action_button(

                        "btn_merge",

                        "🔗 تأكيد الدمج والتعلم",

                        class_="btn-neon"

                    ),

                    ui.modal_button(
                        "إغلاق"
                    ),

                    size="l"

                )

            )


        else:

            active_modal.set(
                "plan_3"
            )







    @render.ui
    def results_area():


        p = input.search_query().strip()



        if not p:

            return None




        html_out = run_system_workflows(

            p,

            database(),

            ""

        )



        return ui.div(

            ui.HTML(html_out),


            ui.input_action_button(

                "trigger_plan_2",

                "🔵 ابدأ إدخال المواصفات والمطابقة الفنية (الخطة 2)",

                class_="btn-plan2-fix"

            )

        )
