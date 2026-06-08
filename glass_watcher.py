import re
import os
import requests
import json
from database import load_db, save_db, add_notification

def verify_cloud_safety():
    """
    نسخة مصححة: فحص اتصال بـ GitHub (قراءة فقط) لتجنب أخطاء PUT.
    """
    github_url = os.environ.get("GITHUB_JSON_URL")
    if not github_url:
        return False, "⚠️ تحذير: رابط GitHub غير معرف!"
        
    try:
        # استخدام GET فقط لأن GitHub لا يدعم PUT بدون API Key
        res = requests.get(github_url, timeout=10)
        if res.status_code == 200:
            return True, "🟢 السحاب متصل والبيانات متاحة."
        else:
            return False, f"⚠️ خطأ: فشل الوصول لملف البيانات (كود {res.status_code})"
    except Exception as e:
        return False, f"⚠️ تحذير: تعذر الاتصال بـ GitHub: {str(e)}"

def find_device_in_tree(db_data, target_device):
    """
    البحث داخل شجرة البيانات مع مراعاة مفتاح 'data' الجديد.
    """
    # استخراج محتوى البيانات الأساسي
    content = db_data.get("data", {})
    
    for size, screens in content.items():
        if not isinstance(screens, dict): continue
        for screen, sensors in screens.items():
            for sensor, devices_list in sensors.items():
                if isinstance(devices_list, list) and target_device in devices_list:
                    return size, screen, sensor
    return None, None, None

def run_watcher():
    """
    المراقب المطور والمصحح للعمل مع GitHub و JSON الجديد.
    """
    try:
        print("🤖 بدء تشغيل المراقب الصامت...")
        
        # 1. فحص الاتصال
        cloud_safe, cloud_message = verify_cloud_safety()
        if not cloud_safe:
            add_notification(cloud_message)
            print(f"🚨 {cloud_message}")
        else:
            print(cloud_message)

        # 2. تحميل البيانات
        db_data = load_db() or {}
        target_list = ["Redmi 9", "Redmi 9A", "Realme C11 2021"]
        db_changed = False

        for device in target_list:
            current_size, current_screen, current_sensor = find_device_in_tree(db_data, device)
            
            # إذا كان الجهاز موجوداً ومستقراً، تخطاه
            if current_size:
                print(f"💤 [{device}]: مستقر في الشجرة.")
                continue

            print(f"⚡ [{device}]: جاري المعالجة...")
            # هنا يمكنك استدعاء دالة fetch_device_specs_online إذا أردت تحديث البيانات
            # ... (باقي منطق التحديث)
            
        if db_changed:
            save_db(db_data)
            print("💾 تم حفظ التعديلات محلياً.")
            
    except Exception as main_error:
        print(f"🚨 خطأ: {main_error}")
    finally:
        print("Done.")

if __name__ == "__main__":
    run_watcher()
