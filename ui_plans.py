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
# WIZARD - STEP 1: SIZE
# ==========================================================

def draw_wizard_size_modal(phone):

    return draw_modal_overlay(

        ui.div(

            ui.h2("لم يتم العثور على الهاتف"),

            ui.p(f"الهاتف: {phone}"),

            ui.p("الخطوة 1 من 3 — أدخل مقاس الشاشة"),

            ui.input_text(
                "wiz_size",
                "المقاس (مثال: 6.5)"
            ),

            ui.div(

                ui.input_action_button(
                    "wiz_size_next",
                    "التالي ⟵",
                    class_="btn-neon"
                ),

                ui.input_action_button(
                    "btn_close_modal",
                    "إلغاء",
                    class_="btn-close"
                ),

                class_="modal-buttons"

            ),

            class_="glass-card modal-card"

        )

    )


# ==========================================================
# WIZARD - STEP 2: PANEL
# ==========================================================

def draw_wizard_panel_modal(phone, panels, add_mode=False):

    body = [

        ui.h2("لم يتم العثور على الهاتف"),

        ui.p(f"الهاتف: {phone}"),

        ui.p("الخطوة 2 من 3 — نوع الشاشة"),

    ]

    if add_mode:

        body.append(
            ui.input_text(
                "wiz_panel_new",
                "اكتب نوع الشاشة الجديد"
            )
        )

    else:

        body.append(
            ui.input_select(
                "wiz_panel",
                "اختر نوع الشاشة",
                choices=panels or ["-"]
            )
        )

    body.append(

        ui.input_action_button(
            "wiz_show_add_panel",
            "↩ اختيار من القائمة" if add_mode else "➕ نوع جديد غير موجود",
            class_="btn-close"
        )

    )

    body.append(

        ui.div(

            ui.input_action_button(
                "wiz_panel_next",
                "التالي ⟵",
                class_="btn-neon"
            ),

            ui.input_action_button(
                "btn_close_modal",
                "إلغاء",
                class_="btn-close"
            ),

            class_="modal-buttons"

        )

    )

    return draw_modal_overlay(
        ui.div(*body, class_="glass-card modal-card")
    )


# ==========================================================
# WIZARD - STEP 3: SENSOR
# ==========================================================

def draw_wizard_sensor_modal(phone, sensors, add_mode=False):

    body = [

        ui.h2("لم يتم العثور على الهاتف"),

        ui.p(f"الهاتف: {phone}"),

        ui.p("الخطوة 3 من 3 — مستشعر التقارب"),

    ]

    if add_mode:

        body.append(
            ui.input_text(
                "wiz_sensor_new",
                "اكتب اسم المستشعر الجديد"
            )
        )

    else:

        body.append(
            ui.input_select(
                "wiz_sensor",
                "اختر المستشعر",
                choices=sensors or ["-"]
            )
        )

    body.append(

        ui.input_action_button(
            "wiz_show_add_sensor",
            "↩ اختيار من القائمة" if add_mode else "➕ مستشعر جديد غير موجود",
            class_="btn-close"
        )

    )

    body.append(

        ui.div(

            ui.input_action_button(
                "wiz_sensor_next",
                "بحث عن مطابقة ⟵",
                class_="btn-neon"
            ),

            ui.input_action_button(
                "btn_close_modal",
                "إلغاء",
                class_="btn-close"
            ),

            class_="modal-buttons"

        )

    )

    return draw_modal_overlay(
        ui.div(*body, class_="glass-card modal-card")
    )


# ==========================================================
# WIZARD - CONFIRM (MERGE OR NEW GROUP)
# ==========================================================

def draw_wizard_confirm_modal(phone, size, panel, sensor, matched):

    if matched:

        title = "🟢 وُجدت مجموعة مطابقة"

        message = f'هل تريد إضافة "{phone}" إلى هذه المجموعة؟'

    else:

        title = "🆕 لا توجد مجموعة مطابقة"

        message = f'هل تريد تسجيل "{phone}" كمجموعة جديدة بهذه المواصفات؟'

    return draw_modal_overlay(

        ui.div(

            ui.h2(title),

            ui.p(message),

            ui.div(
                f"المقاس: {size}",
                class_="coord-line"
            ),

            ui.div(
                f"نوع الشاشة: {panel}",
                class_="coord-line"
            ),

            ui.div(
                f"المستشعر: {sensor}",
                class_="coord-line"
            ),

            ui.div(

                ui.input_action_button(
                    "wiz_confirm_save",
                    "✅ تأكيد الإضافة",
                    class_="btn-neon"
                ),

                ui.input_action_button(
                    "btn_close_modal",
                    "إلغاء",
                    class_="btn-close"
                ),

                class_="modal-buttons"

            ),

            class_="glass-card modal-card"

        )

    )


# ==========================================================
# PLAN 2 (قديم - غير مستخدم حالياً، أُبقي للتوافق)
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
# PLAN 3 (قديم - غير مستخدم حالياً، أُبقي للتوافق)
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
