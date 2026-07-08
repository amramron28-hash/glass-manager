from shiny import ui


def show_info_modal(title: str, message: str):
    """
    نافذة معلومات عامة.
    """
    ui.modal_show(
        ui.modal(
            ui.p(message),
            title=title,
            easy_close=True,
            footer=ui.modal_button("إغلاق"),
        )
    )


def show_success_modal(message: str):
    """
    نافذة نجاح.
    """
    ui.modal_show(
        ui.modal(
            ui.div(
                ui.h4("✅ تمت العملية بنجاح"),
                ui.p(message),
            ),
            title="نجاح",
            easy_close=True,
            footer=ui.modal_button("إغلاق"),
        )
    )


def show_error_modal(message: str):
    """
    نافذة خطأ.
    """
    ui.modal_show(
        ui.modal(
            ui.div(
                ui.h4("❌ حدث خطأ"),
                ui.p(message),
            ),
            title="خطأ",
            easy_close=True,
            footer=ui.modal_button("إغلاق"),
        )
    )


def confirm_modal(
    title: str,
    message: str,
    confirm_id: str = "confirm_btn",
    cancel_label: str = "إلغاء",
    confirm_label: str = "تأكيد",
):
    """
    إنشاء نافذة تأكيد وإرجاعها.
    """
    return ui.modal(
        ui.p(message),
        title=title,
        easy_close=False,
        footer=ui.div(
            ui.input_action_button(confirm_id, confirm_label),
            ui.modal_button(cancel_label),
        ),
    )
