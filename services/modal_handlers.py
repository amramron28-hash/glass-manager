# services/modal_handlers.py

from shiny import ui
from core.logger import get_logger

log = get_logger("modal_handlers")


def handle_show_add_panel(show_curtain, suggestions_list):
    show_curtain.set(False)
    suggestions_list.set([])

    ui.modal_show(
        ui.modal(
            ui.input_text(
                "new_panel_name",
                "اسم نوع الشاشة الجديد:",
                placeholder="مثال: IPS LCD",
            ),
            ui.div(
                ui.input_action_button(
                    "btn_confirm_add_panel",
                    "✅ إضافة",
                    style="background:#2ecc71;color:white;padding:10px 20px;border:none;border-radius:8px;margin-left:10px;",
                ),
                ui.input_action_button(
                    "btn_cancel_add",
                    "❌ إلغاء",
                    style="background:#e74c3c;color:white;padding:10px 20px;border:none;border-radius:8px;",
                ),
                style="text-align:center;margin-top:20px;",
            ),
            title="➕ إضافة نوع شاشة جديد",
            easy_close=True,
        )
    )


def handle_show_add_sensor(show_curtain, suggestions_list):
    show_curtain.set(False)
    suggestions_list.set([])

    ui.modal_show(
        ui.modal(
            ui.input_text(
                "new_sensor_name",
                "اسم المستشعر الجديد:",
                placeholder="مثال: Proximity Sensor",
            ),
            ui.div(
                ui.input_action_button(
                    "btn_confirm_add_sensor",
                    "✅ إضافة",
                    style="background:#2ecc71;color:white;padding:10px 20px;border:none;border-radius:8px;margin-left:10px;",
                ),
                ui.input_action_button(
                    "btn_cancel_add",
                    "❌ إلغاء",
                    style="background:#e74c3c;color:white;padding:10px 20px;border:none;border-radius:8px;",
                ),
                style="text-align:center;margin-top:20px;",
            ),
            title="➕ إضافة مستشعر جديد",
            easy_close=True,
        )
    )


def confirm_add_panel(input, custom_panels, invalidate_workflow):
    try:
        value = input.new_panel_name().strip()

        if value:
            panels = custom_panels()

            if value not in panels:
                custom_panels.set(panels + [value])
                invalidate_workflow()
                log.info(f"Added panel: {value}")

        ui.modal_remove()

    except Exception as e:
        log.error(f"Add panel error: {e}")


def confirm_add_sensor(input, custom_sensors, invalidate_workflow):
    try:
        value = input.new_sensor_name().strip()

        if value:
            sensors = custom_sensors()

            if value not in sensors:
                custom_sensors.set(sensors + [value])
                invalidate_workflow()
                log.info(f"Added sensor: {value}")

        ui.modal_remove()

    except Exception as e:
        log.error(f"Add sensor error: {e}")


def cancel_add():
    ui.modal_remove()
