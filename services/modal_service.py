# services/modal_service.py

from shiny import ui


def build_add_panel_modal():
    return ui.modal(
        ui.input_text(
            "new_panel_name",
            "اسم نوع الشاشة الجديد:",
            placeholder="مثال: IPS LCD"
        ),
        ui.div(
            ui.input_action_button(
                "btn_confirm_add_panel",
                "✅ إضافة",
                style="""
                    background:#2ecc71;
                    color:white;
                    padding:10px 20px;
                    border:none;
                    border-radius:8px;
                    margin-left:10px;
                """
            ),
            ui.input_action_button(
                "btn_cancel_add",
                "❌ إلغاء",
                style="""
                    background:#e74c3c;
                    color:white;
                    padding:10px 20px;
                    border:none;
                    border-radius:8px;
                """
            ),
            style="text-align:center; margin-top:20px;"
        ),
        title="➕ إضافة نوع شاشة جديد",
        easy_close=True
    )


def build_add_sensor_modal():
    return ui.modal(
        ui.input_text(
            "new_sensor_name",
            "اسم المستشعر الجديد:",
            placeholder="مثال: Proximity Sensor"
        ),
        ui.div(
            ui.input_action_button(
                "btn_confirm_add_sensor",
                "✅ إضافة",
                style="""
                    background:#2ecc71;
                    color:white;
                    padding:10px 20px;
                    border:none;
                    border-radius:8px;
                    margin-left:10px;
                """
            ),
            ui.input_action_button(
                "btn_cancel_add",
                "❌ إلغاء",
                style="""
                    background:#e74c3c;
                    color:white;
                    padding:10px 20px;
                    border:none;
                    border-radius:8px;
                """
            ),
            style="text-align:center; margin-top:20px;"
        ),
        title="➕ إضافة مستشعر جديد",
        easy_close=True
    )
