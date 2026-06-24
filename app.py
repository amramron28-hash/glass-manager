import os
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

    ui.tags.head(

        ui.tags.link(
            rel="manifest",
            href="/manifest.json"
        ),

        ui.tags.script("""
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                    navigator.serviceWorker.register('/service-worker.js')
                    .then(function(reg) {
                        console.log('Service Worker Registered', reg);
                    })
                    .catch(function(err) {
                        console.log('Service Worker Failed', err);
                    });
                });
            }
        """)

    ),

    ui.HTML(
        """
        <script>
        Shiny.addCustomMessageHandler(
            'toggle_drawer',
            function(msg){

                let d = document.getElementById(
                    'settings_drawer'
                );

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
        """
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

        except Exception:

            return []




    @reactive.calc
    def database():

        return convert_database(
            cloud_rows()
        )




    @reactive.calc
    def unique_panels():

        values = set()

        for r in cloud_rows():

            values.add(
                str(r.get("panel","")).strip()
            )


        values.update(
            custom_panels()
        )


        return sorted(
            list(values)
        )




    @reactive.calc
    def unique_sensors():

        values = set()

        for r in cloud_rows():

            values.add(
                str(r.get("sensor","")).strip()
            )


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


        notif = (
            "🟢 جرس الإشعارات: نشط"
            if input.switch_notif()
            else
            "🔴 جرس الإشعارات: متوقف"
        )


        monitor = (
            "🟢 المراقب الصامت: يحرس البيانات"
            if input.switch_monitor()
            else
            "🔴 المراقب الصامت: متوقف"
        )


        return ui.div(

            ui.div(
                f"📊 إجمالي الهواتف بالسحاب: {total}",
                class_="metric-box"
            ),


            ui.div(
                notif,
                style="font-size:13px;"
            ),


            ui.div(
                monitor,
                style="font-size:13px;"
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



        matches = list(
            dict.fromkeys(
                [
                    str(r.get("model_name",""))
                    for r in cloud_rows()
                    if q in str(
                        r.get("model_name","")
                    ).lower()
                ]
            )
        )[:8]



        if not matches:
            return None



        rows = []


        for name in matches:

            safe_name = (
                name
                .replace("'", "\\'")
                .replace('"', '\\"')
            )


            rows.append(

                ui.div(

                    name,

                    class_="suggestion-row",

                    onclick=
                    f"""
                    Shiny.setInputValue(
                        'selected_model',
                        '{safe_name}',
                        {{priority:'event'}}
                    );
                    """

                )

            )


        return ui.div(

            *rows,

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
    @reactive.event(input.btn_add_panel)
    def add_panel():

        ui.modal_show(

            ui.modal(

                ui.input_text(
                    "new_p",
                    "اسم الشاشة الجديدة:"
                ),


                ui.input_action_button(
                    "save_p",
                    "إضافة",
                    class_="btn-neon"
                ),


                ui.modal_button(
                    "تراجع"
                ),


                title="✨ إضافة شاشة"

            )

        )





    @reactive.effect
    @reactive.event(input.save_p)
    def save_p():


        value = input.new_p().strip()


        if value:

            current = custom_panels()

            if value not in current:

                custom_panels.set(
                    current + [value]
                )


        ui.modal_remove()





    @reactive.effect
    @reactive.event(input.btn_add_sensor)
    def add_sensor():


        ui.modal_show(

            ui.modal(

                ui.input_text(
                    "new_s",
                    "اسم المستشعر الجديد:"
                ),


                ui.input_action_button(
                    "save_s",
                    "إضافة",
                    class_="btn-neon"
                ),


                ui.modal_button(
                    "تراجع"
                ),


                title="✨ إضافة مستشعر"

            )

        )





    @reactive.effect
    @reactive.event(input.save_s)
    def save_s():


        value = input.new_s().strip()


        if value:

            current = custom_sensors()


            if value not in current:

                custom_sensors.set(
                    current + [value]
                )


        ui.modal_remove()





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
            compat.get("exact")
            or compat.get("plus")
            or compat.get("minus")
        ):


            active_modal.set(None)


            ui.modal_show(

                ui.modal(

                    ui.h3(
                        "🎉 تم العثور على مجموعات متوافقة!",
                        style="color:#2ecc71;text-align:center;"
                    ),


                    ui.p(
                        "هل تريد الدمج تلقائياً مع هذه المجموعة في السحاب؟"
                    ),


                    ui.input_action_button(
                        "btn_merge",
                        "🔗 ادمج الهاتف فوراً",
                        class_="btn-neon"
                    ),

                    ui.modal_button(
                        "إلغاء"
                    )

                )

            )


        else:

            active_modal.set(
                "plan_3"
            )





    @reactive.effect
    @reactive.event(input.btn_merge)
    def do_merge():


        phone = (
            str(current_search_phone())
            .strip()
        )



        if input.switch_monitor():

            exists = any(

                phone.lower()
                ==
                str(r.get("model_name",""))
                .strip()
                .lower()

                for r in cloud_rows()

            )


            if exists:


                if input.switch_notif():

                    ui.notification_show(

                        "🚨 المراقب الصامت: الموديل موجود مسبقاً",

                        type="error",

                        duration=5

                    )


                ui.modal_remove()

                return




        try:


            supabase.table(
                "phones"
            ).insert(

                {

                    "model_name": phone,

                    "size":
                    str(input.p2_size()),

                    "panel":
                    input.p2_panel(),

                    "sensor":
                    input.p2_sensor()

                }

            ).execute()



            db_trigger.set(
                db_trigger() + 1
            )


            ui.modal_remove()



            if input.switch_notif():

                ui.notification_show(
                    "✔️ تم الدمج بنجاح",
                    type="message"
                )


        except Exception as e:

            print(e)






    @reactive.effect
    @reactive.event(input.p3_cancel)
    def cancel_p3():

        active_modal.set(
            "plan_2"
        )






    @reactive.effect
    @reactive.event(input.p3_submit)
    def do_p3():


        phone = str(
            current_search_phone()
        ).strip()



        if input.switch_monitor():


            exists = any(

                phone.lower()
                ==
                str(r.get("model_name",""))
                .strip()
                .lower()

                for r in cloud_rows()

            )



            if exists:


                if input.switch_notif():

                    ui.notification_show(

                        "🚨 تم منع إنشاء مجموعة مكررة",

                        type="error",

                        duration=5

                    )


                active_modal.set(None)

                return





        try:


            supabase.table(
                "phones"
            ).insert(

                {

                    "model_name": phone,

                    "size":
                    str(input.p2_size()),

                    "panel":
                    input.p2_panel(),

                    "sensor":
                    input.p2_sensor()

                }

            ).execute()



            db_trigger.set(
                db_trigger()+1
            )


            active_modal.set(None)



            if input.switch_notif():

                ui.notification_show(

                    "🚨 تم تأسيس مرجع فني جديد",

                    type="warning"

                )


        except Exception as e:

            print(e)







    @render.ui
    def results_area():

        p = input.search_query().strip()


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
