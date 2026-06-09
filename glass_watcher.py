import re
import os
import requests
import json
from database import load_db, save_db, add_notification

def verify_cloud_safety():
    """
    فحص اتصال بـ GitHub وجلب البيانات بشكل آمن وموثوق.
    """
    github_url = "https://githubusercontent.com"
    try:
        res = requests.get(github_url, timeout=10)
        if res.status_code == 200:
            return True, "🟢 السحاب متصل بكفاءة والبيانات الحية متاحة."
        else:
            return False, f"⚠️ تنبيه: فشل الوصول لملف البيانات السحابي (كود {res.status_code})"
    except Exception as e:
        return False, f"⚠️ تحذير: تعذر الاتصال بالسحاب، النظام يعمل بالنسخة الاحتياطية."

def find_device_in_tree(db_data, target_device):
    """
    البحث الذكي داخل شجرة البيانات ومطابقتها.
    """
    content = db_data.get("data", {}) if "data" in db_data else db_data
    if not isinstance(content, dict):
        return None, None, None
        
    for size, screens in content.items():
        if size in ["system_notifications", "metadata", "data"]: continue
        if not isinstance(screens, dict): continue
        for screen, sensors in screens.items():
            if not isinstance(sensors, dict): continue
            for sensor, devices_list in sensors.items():
                if isinstance(devices_list, list) and target_device in devices_list:
                    return size, screen, sensor
    return None, None, None

def run_watcher():
    """
    تشغيل المراقب الصامت كمساعد ذكي وحارس لبيانات المحل.
    """
    try:
        print("🤖 بدء تشغيل المراقب الصامت لتحديث النظام...")
        
        # 1. فحص الاتصال وتسجيل النتيجة في الإشعارات الحية للتطبيق
        cloud_safe, cloud_message = verify_cloud_safety()
        add_notification(cloud_message)
        print(cloud_message)

        # 2. تحميل البيانات وفحص استقرار الموديلات الأساسية بالمحل
        db_envelope = load_db() or {}
        db_data = db_envelope.get("data", {}) if "data" in db_envelope else db_envelope
        
        # قائمة الهواتف التي يراقبها الصامت لضمان وجودها واستقرار مقاساتها دائماً
        target_list = ["Redmi 9", "Redmi 9A", "Realme C11 2021"]
        
        for device in target_list:
            current_size, current_screen, current_sensor = find_device_in_tree(db_data, device)
            
            if current_size:
                print(f"💤 [{device}]: مستقر وآمن في شجرة المقاسات ({current_size}).")
            else:
                warning_msg = f"📱 الموديل النادر [{device}] غير مضاف بالشجرة! تواصل مع عمار لتحديثه."
                add_notification(warning_msg)
                print(f"⚡ {warning_msg}")
            
    except Exception as main_error:
        error_msg = f"🚨 خطأ داخلي في المراقب: {str(main_error)}"
        add_notification(error_msg)
        print(error_msg)
    finally:
        print("Done.")

if __name__ == "__main__":
    run_watcher()
