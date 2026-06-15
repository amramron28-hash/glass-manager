import os
import re
from rapidfuzz import process, fuzz
from database import supabase # الاستيراد المباشر من محرك السحابة الآمن

# ==========================================
# 👁️ 1. عين التطبيق: دالة الفحص السريع والذكاء النصي
# ==========================================
def normalize_text(text):
    if not text:
        return ""
    text = str(text).lower().strip()
    # إزالة المسافات الزائدة والرموز التي تعيق المطابقة الفنية
    text = re.sub(r'[\s\-_/]+', ' ', text)
    return text

def find_model_coords(db_data, search_name):
    """تبحث بدقة في شجرة البيانات المسترجعة سحابياً عن إحداثيات الهاتف"""
    if not db_data or not search_name:
        return None, None, None, ""
    
    normalized_search = normalize_text(search_name)
    
    for size, panels in db_data.items():
        for panel, sensors in panels.items():
            for sensor, data in sensors.items():
                for model in data.get("models", []):
                    if normalize_text(model) == normalized_search:
                        return size, panel, sensor, model
    return None, None, None, ""

# ==========================================
# 🗂️ 2. العقل الهندسي: حساب المقاسات المتوافقة بدقة
# ==========================================
def get_compatibles_strict(db_data, current_search):
    results = {"exact": [], "plus": [], "minus": [], "warn": []}
    size_grp, panel_grp, sensor_grp, real_name = find_model_coords(db_data, current_search)
    
    if not size_grp:
        return results

    try:
        current_size = float(size_grp)
    except ValueError:
        return results

    for size, panels in db_data.items():
        try:
            target_size = float(size)
        except ValueError:
            continue
            
        for panel, sensors in panels.items():
            for sensor, data in sensors.items():
                for model in data.get("models", []):
                    if normalize_text(model) == normalize_text(current_search):
                        continue
                        
                    # تصنيف التوافق بناءً على قواعد القياس الدقيقة ومستشعر الغراء
                    if target_size == current_size and panel == panel_grp and sensor == sensor_grp:
                        results["exact"].append(model)
                    elif target_size == round(current_size + 0.1, 2) and panel == panel_grp:
                        results["plus"].append(model)
                    elif target_size == round(current_size - 0.1, 2) and panel == panel_grp:
                        results["minus"].append(model)
                    elif target_size == current_size and panel == panel_grp and sensor != sensor_grp:
                        results["warn"].append(f"{model} (مستشعر مختلف)")
                        
    return results

# ==========================================
# 🛡️ 3. يد الحارس: دالة الصيانة الذكية والمراقب الصامت (الأتمتة السحابية)
# ==========================================
def run_intelligent_inspector(db_data=None):
    """
    يعمل كعين ويد داخل التطبيق: 
    يفحص السحابة، ينظف التكرارات، يحذف المجموعات الفارغة، ويصلح التلف فوراً.
    """
    changes_made = False
    cleaned_db = {}
    
    try:
        # جلب البيانات الحية مباشرة من السحابة لضمان دقة الفحص
        res = supabase.table("phones").select("*").execute()
        rows = res.data or []
        
        if not rows:
            return {}, False

        # معالجة وفحص البيانات سحابياً خطوة بخطوة
        for r in rows:
            row_id = r.get("id")
            size = str(r.get("size", "")).strip()
            panel = str(r.get("panel", "")).strip()
            sensor = str(r.get("sensor", "")).strip()
            model = str(r.get("model_name") or r.get("model") or "").strip()

            # 🛠️ يد المراقب: حذف السطور التالفة أو الفارغة من السحابة تلقائياً
            if not all([size, panel, sensor, model]) or size == "" or model == "":
                supabase.table("phones").delete().eq("id", row_id).execute()
                changes_made = True
                continue

            # بناء الهيكل النظيف ومنع التكرار البرمجي
            cleaned_db.setdefault(size, {})
            cleaned_db[size].setdefault(panel, {})
            cleaned_db[size][panel].setdefault(sensor, {"models": []})

            if model not in cleaned_db[size][panel][sensor]["models"]:
                cleaned_db[size][panel][sensor]["models"].append(model)
            else:
                # 🛠️ يد المراقب: تدمير التكرار الحقيقي في السحابة فوراً للحفاظ على المساحة
                supabase.table("phones").delete().eq("id", row_id).execute()
                changes_made = True

        return cleaned_db, changes_made

    except Exception:
        # حماية البيانات من التلف في حالة انقطاع الشبكة
        return db_data if db_data else {}, False
