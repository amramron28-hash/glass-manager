import re
import os
import urllib.request
import urllib.parse
import requests
import json
from database import load_db, save_db, add_notification

def verify_cloud_safety():
    """
    يفحص أمان الاتصال بالسحاب للتأكد من عدم ضياع فهارس عمار عند عمل Factory Rebuild.
    """
    npoint_url = os.environ.get("NPOINT_URL")
    if not npoint_url:
        return False, "⚠️ تحذير: رابط السحاب NPOINT_URL غير معرف! البيانات تحفظ محلياً فقط وتتعرض للضياع!"
        
    try:
        # اختبار القراءة
        res = requests.get(npoint_url, timeout=5)
        if res.status_code != 200:
            return False, f"⚠️ خطر: السحاب معطل (كود {res.status_code})! لا تضغط Factory Rebuild!"
            
        # اختبار الكتابة الآمنة
        current_data = res.json()
        test_res = requests.put(npoint_url, data=json.dumps(current_data), headers={"Content-Type": "application/json"}, timeout=5)
        if test_res.status_code != 200:
            return False, "⚠️ خطر: السحاب يرفض حفظ البيانات الجديدة! الحفظ محلي فقط حالياً!"
            
        return True, "🟢 السحاب مستقر ومؤمن بنسبة 100%. جاهز لإعادة البناء بأمان."
    except:
        return False, "⚠️ تحذير: فشل الاتصال بالسحاب (انقطاع إنترنت أو حظر)! البيانات غير محمية حالياً!"

def fetch_device_specs_online(model_name):
    """
    جلب مواصفات الهاتف من الإنترنت مع توفير البيانات.
    """
    try:
        query = urllib.parse.quote(f"{model_name} specs screen size proximity sensor")
        url = f"https://duckduckgo.com{query}" 
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode('utf-8').lower()
            
        sensor = "virtual_proximity_sensor" if any(x in html for x in ["virtual proximity", "virtual sensing", "software-based", "ultrasonic"]) else "hardware_proximity_sensor"
        screen = "Notch Screen" if any(x in html for x in ["notch", "waterdrop", "v-notch", "u-notch"]) else "Punch-Hole Screen"
        
        size_match = re.search(r'(\.\d{1,2})', html)
        size = str(float(size_match.group(1))) if size_match else "6.5"
            
        return size, screen, sensor
    except:
        return None, None, None

def find_device_in_tree(db_data, target_device):
    """
    البحث داخل شجرة البيانات الحالية لمعرفة حالة الجهاز.
    """
    for size, screens in db_data.items():
        if size == "system_notifications":
            continue
        for screen, sensors in screens.items():
            for sensor, devices_list in sensors.items():
                if isinstance(devices_list, list) and target_device in devices_list:
                    return size, screen, sensor
    return None, None, None

def run_watcher():
    """
    المراقب الصامت المطور: يراقب الهواتف، ويفحص أمان السحاب، ويرسل تنبيهات وقائية لعمار.
    """
    try:
        print("🤖 بدء تشغيل المراقب الصامت المدمج...")
        
        # 1. فحص أمان السحاب أولاً وقبل كل شيء
        cloud_safe, cloud_message = verify_cloud_safety()
        if not cloud_safe:
            # حقن تحذير صارم في جرس الإشعارات باللوحة الجانبية
            add_notification(cloud_message)
            print(f"🚨 تنبيه أمني: {cloud_message}")
        else:
            print(cloud_message)

        db_data = load_db() or {}
        target_list = ["Redmi 9", "Redmi 9A", "Realme C11 2021"]
        db_changed = False

        for device in target_list:
            current_size, current_screen, current_sensor = find_device_in_tree(db_data, device)
            
            is_valid = False
            if current_size:
                try:
                    if float(current_size) > 0: is_valid = True
                except ValueError: pass

            # وضع السكون لتوفير البيانات
            if is_valid:
                print(f"💤 [{device}]: مستقر في الشجرة. (وضع السكون)")
                continue

            print(f"⚡ [{device}]: جاري تصحيحه من الإنترنت...")
            online_size, online_screen, online_sensor = fetch_device_specs_online(device)
            
            if online_size and online_screen and online_sensor:
                if current_size and current_screen and current_sensor:
                    if device in db_data[current_size][current_screen][current_sensor]:
                        db_data[current_size][current_screen][current_sensor].remove(device)
                
                db_data.setdefault(online_size, {}).setdefault(online_screen, {}).setdefault(online_sensor, [])
                if device not in db_data[online_size][online_screen][online_sensor]:
                    db_data[online_size][online_screen][online_sensor].append(device)
                    db_changed = True
                    add_notification(f"🔄 تصحيح صامت: تم توجيه [{device}] للمقاس {online_size}")

        if db_changed:
            save_db(db_data)
            print("💾 تم حفظ وتزامن التعديلات.")
            
    except Exception as main_error:
        print(f"🚨 خطأ: {main_error}")
    finally:
        print("Done.")

if __name__ == "__main__":
    run_watcher()
