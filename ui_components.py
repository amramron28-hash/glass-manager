import os
import base64
from html import escape
from shiny import ui
from silent_monitor import get_database, refresh, get_status

# --- الدوال الأساسية للواجهة ---
def inject_pwa_and_styles():
    return ui.HTML("<style>body { background-color: #0a0e17; color: white; direction: rtl; }</style>")

def draw_database_status(total):
    return ui.div(f"📊 إجمالي الهواتف في القاعدة: {total}", class_="status-card")

def draw_monitor_component(status_data):
    return ui.div(f"المراقب: {status_data.get('status', 'OFFLINE')}", class_="monitor-card")

def draw_notifications(status_data):
    return ui.div("🔔 الإشعارات نشطة", class_="notify-card")

# --- دوال النوافذ المنبثقة (التي كانت مفقودة) ---
def draw_plan_2_modal(phone_name, panels, sensors):
    return ui.div(
        ui.h3(f"إعدادات الخطة 2 لـ {phone_name}"),
        ui.input_text("p2_search", "بحث في الخطة 2"),
        ui.div("قائمة الـ Panels والـ Sensors ستظهر هنا"),
        class_="modal-content"
    )

def draw_plan_3_modal(phone_name, panels, sensors):
    return ui.div(
        ui.h3(f"إعدادات الخطة 3 لـ {phone_name}"),
        ui.input_text("p3_search", "بحث في الخطة 3"),
        class_="modal-content"
    )

def build_add_panel_modal():
    return ui.div(
        ui.h4("إضافة لوحة جديدة (Panel)"),
        ui.input_text("new_panel_name", "اسم اللوحة"),
        ui.input_action_button("btn_confirm_add_panel", "تأكيد الإضافة"),
        ui.input_action_button("btn_cancel_add", "إلغاء"),
        class_="modal-content"
    )

def build_add_sensor_modal():
    return ui.div(
        ui.h4("إضافة مستشعر جديد (Sensor)"),
        ui.input_text("new_sensor_name", "اسم المستشعر"),
        ui.input_action_button("btn_confirm_add_sensor", "تأكيد الإضافة"),
        ui.input_action_button("btn_cancel_add", "إلغاء"),
        class_="modal-content"
    )

# --- تذييل الملف ---
# تأكد من أن هذا الملف يسمى ui_components.py
