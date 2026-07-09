from shiny import ui


# ==========================================================
# MODAL OVERLAY
# ==========================================================

def draw_modal_overlay(inner):

    if inner is None:
        return None

    return ui.div(

        inner,

        class_="modal-overlay"

    )



# ==========================================================
# PLAN 2
# ==========================================================

def draw_plan_2_modal(
        phone="",
        panels=None,
        sensors=None
):

    panels = panels or []
    sensors = sensors or []


    return draw_modal_overlay(

        ui.div(

            ui.h2(
                "الخطة الثانية"
            ),


            ui.p(
                f"الهاتف: {phone}"
            ),


            ui.input_select(

                "p2_panel",

                "نوع الشاشة",

                choices=panels

            ),


            ui.input_select(

                "p2_sensor",

                "المستشعر",

                choices=sensors

            ),


            ui.div(

                ui.input_action_button(

                    "btn_plan2_save",

                    "💾 حفظ",

                    class_="btn-neon"

                ),


                ui.input_action_button(

                    "btn_close_modal",

                    "إغلاق",

                    class_="btn-close"

                ),


                class_="modal-buttons"

            ),


            class_="glass-card modal-card"

        )

    )



# ==========================================================
# PLAN 3
# ==========================================================

def draw_plan_3_modal(
        phone="",
        result=None
):

    return draw_modal_overlay(

        ui.div(

            ui.h2(
                "الخطة الثالثة"
            ),


            ui.p(

                f"لم يتم العثور على نتائج للهاتف: {phone}"

            ),


            ui.input_text(

                "p3_size",

                "المقاس"

            ),


            ui.input_text(

                "p3_panel",

                "نوع الشاشة"

            ),


            ui.input_text(

                "p3_sensor",

                "المستشعر"

            ),


            # زر الإضافة المستقبلي +

            ui.input_action_button(

                "btn_plan3_save",

                "💾 إضافة",

                class_="btn-neon"

            ),


            ui.input_action_button(

                "btn_close_modal",

                "إغلاق",

                class_="btn-close"

            ),


            class_="glass-card modal-card"

        )

    )
