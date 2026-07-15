import json
import os
from supabase import create_client, Client

# إعداد المسارات ومفاتيح الاتصال المستخرجة من مشروعك
JSON_FILE_PATH = os.path.join("www", "models_db.json")
SUPABASE_URL = "https://mgmphimlcdchtbiyhhbt.supabase.co"
SUPABASE_KEY = "sb_publishable_5EYoZAX1GHbi1lzyDls_1A_B1KpVIHX"

def sync_local_to_supabase():
    print("🔄 جاري قراءة الملف المصحح محلياً www/models_db.json...")
    
    if not os.path.exists(JSON_FILE_PATH):
        print(f"❌ لم يتم العثور على ملف JSON في المسار: {JSON_FILE_PATH}")
        print("يرجى التأكد من تشغيل السكريبت من المجلد الرئيسي للمشروع.")
        return

    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"❌ خطأ أثناء قراءة ملف الـ JSON: {e}")
            return

    # تفكيك هيكل الملف الشجري إلى صفوف ثنائية الأبعاد لرفعها للجدول
    records = []
    for size, panels in data.items():
        if not isinstance(panels, dict):
            continue
        for panel, sensors in panels.items():
            if not isinstance(sensors, dict):
                continue
            for sensor, s_data in sensors.items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if not isinstance(models_list, list):
                    continue
                for model in models_list:
                    records.append({
                        "size": str(size).strip(),
                        "panel": str(panel).strip(),
                        "sensor": str(sensor).strip(),
                        "model_name": str(model).strip()
                    })

    total_records = len(records)
    print(f"✅ تم تفكيك الملف بنجاح. إجمالي الهواتف المستخرجة للرفع: {total_records} هاتف.")

    # الاتصال بـ Supabase
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ فشل الاتصال بمنصة Supabase: {e}")
        return

    # مسح البيانات القديمة المليئة بالتكرار لتهيئة الجدول
    try:
        print("🧹 جاري تفريغ جدول 'phones' الحالي في Supabase لضمان النظافة ومنع التكرار...")
        supabase.table("phones").delete().neq("size", "none_existent_size").execute()
        print("✅ تم تفريغ الجدول أونلاين بنجاح.")
    except Exception as e:
        print(f"❌ خطأ أثناء مسح الجدول من Supabase: {e}")
        return

    # الرفع على دفعات (Chunks) آمنة لتجنب انقطاع الاتصال أو تجاوز حجم الطلب
    chunk_size = 100
    print(f"🚀 جاري رفع البيانات المصححة والجديدة (حجم الدفعة: {chunk_size})...")
    
    for i in range(0, total_records, chunk_size):
        chunk = records[i:i + chunk_size]
        try:
            supabase.table("phones").insert(chunk).execute()
            print(f"  - تم رفع الدفعة {i//chunk_size + 1}: من {i+1} إلى {min(i+chunk_size, total_records)}")
        except Exception as e:
            print(f"❌ حدث خطأ أثناء رفع الدفعة {i//chunk_size + 1}: {e}")
            print("⚠️ تم إيقاف المزامنة للسلامة.")
            return

    print("\n🎉 تم تحديث ومزامنة قاعدة بيانات Supabase بالكامل أونلاين بنجاح بنسبة 100%!")
    print(f"📊 إجمالي الهواتف النشطة والمنظمة الآن أونلاين: {total_records} هاتف.")

if __name__ == "__main__":
    sync_local_to_supabase()
