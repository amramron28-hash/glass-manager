import os
print("RUNNING:", os.path.abspath(__file__)) 
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

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


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


app_ui = ui.page_fluid(

    inject_pwa_and_styles(),

    ui.tags.head(

        ui.tags.link(
            rel="manifest",
            href="manifest.json"
        ),

        ui.tags.style("""

        .neon-glass-card {

            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border:1px solid rgba(0,191,255,0.3);
            box-shadow:0 0 15px rgba(0,191,255,0.2);

            color:#00e5ff;

            padding:15px;
            margin-bottom:12px;

            border-radius:15px;

            text-align:center;
            font-weight:bold;
        }


        .neon-red-card {

            border:1px solid rgba(255,0,85,0.5);

            box-shadow:
            0 0 15px rgba(255,0,85,0.3);

            color:#ff4d4d;

        }


        .btn-plan2-fix {

            width:100%;
            max-width:500px;

            margin:15px auto;

            padding:14px;

            background:
            linear-gradient(135deg,#007bff,#0056b3)
            !important;

            color:white !important;

            border:1px solid #00bfff !important;

            border-radius:14px !important;

            font-weight:bold;

            box-shadow:
            0 4px 15px rgba(0,123,255,0.4)
            !important;

            display:block;

        }

        """),


        ui.tags.script("""

        if ('serviceWorker' in navigator) {

            window.addEventListener(
                'load',
                function(){

                    navigator.serviceWorker.register(
                        'service-worker.js'
                    );

                }
            );

        }


        Shiny.addCustomMessageHandler(
            'toggle_drawer',
            function(msg){

                let d =
                document.getElementById(
                    'settings_drawer'
                );


                if(d){

                    if(msg === 'open')
                        d.classList.add('open');

                    else
                        d.classList.remove('open');

                }

            }
        );

        """)

    ),



    ui.div(

        ui.h3(
            "⚙️ الإعدادات",
            style=
            "color:#00bfff;text-align:right;margin-bottom:25px;"
        ),


        ui.div(

            ui.input_switch(
                "switch_notif",
                "🔔 تفعيل جرس الإشعارات",
                value=True
            ),

            class_="metric-box"

        ),


        ui.div(

            ui.input_switch(
                "switch_monitor",
                "🛡️ تشغيل المراقب الصامت",
                value=True
            ),

            class_="metric-box"

        ),


        ui.output_ui(
            "drawer_status_area"
        ),


        ui.input_action_button(
            "close_drawer",
            "إغلاق الترس",
            class_="btn-neon",
            style="width:100%;"
        ),


        id="settings_drawer",
        class_="drawer"

    ),



    ui.div(

        ui.div(

            ui.div(
                "ZEGAAR AMMAR",
                class_="brand-neon-main"
            ),

            ui.div(
                "GLASS MANAGER",
                class_="brand-neon-sub"
            ),

            class_="brand-neon-title"

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



    ui.output_ui(
        "results_area"
    ),



    ui.output_ui(
        "modal_layer"
    )

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
print("P2 BUTTON CLICKED")
        compat = get_compatibles_strict(

            database(),

            str(input.p2_size() or ""),

            str(input.p2_panel() or ""),

            str(input.p2_sensor() or ""),

            str(current_search_phone() or "")

        )


        print("PLAN2 SEARCH RESULT:")

        print(compat)


        exact = compat.get("exact", []) or []

        plus = compat.get("plus", []) or []

        minus = compat.get("minus", []) or []



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


print("BEFORE APP CREATE")

app = App(
    app_ui,
    server
)

print("APP CREATED")
