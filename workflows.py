import os
import requests
import streamlit as st
from ui_components import draw_technical_coords, draw_neon_section
from logic_engine import find_model_coords, get_compatibles_strict
from database import save_db

def local_check_existing_size_group(db, target_size, target_panel):
    """التحقق من وجود مجموعة مقاسات وشاشة مسجلة مسبقاً."""
    matched_models = []
    if target_size in db and target_panel in db[target_size]:
        for sensor, s_data in db[target_size][target_panel].items():
            models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
            matched_models.extend(models_list)
    return matched_models

def ai_background_global_verify(phone_name):
    """جلب بيانات الهاتف من مصدر خارجي للتدقيق."""
    try:
        url = f"https://vercel.app{requests.utils.quote(phone_name)}"
        res = requests.get(url, timeout=1.5).json()
        if res and "specs" in res:
            return {
                "size": str(res["specs"].get("display_size", "")), 
                "panel": str(res["specs"].get("display_type", "")), 
                "sensor": str(res["specs"].get("proximity_type", ""))
            }
    except: pass
    return None

def append_to_models_index(phone_name):
    """تحديث ملف الفهرس المحلي للهواتف تلقائياً وبدون تكرار."""
    INDEX_FILE = "models_index.txt"
    phone_name = phone_name.strip()
    
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            pass
            
    with open(INDEX_FILE, "r", encoding="utf-8") as f: 
        current_models = [line.strip().lower() for line in f if line.strip()]
    
    if phone_name.lower() not in current_models:
        with open(INDEX_FILE, "a", encoding="utf-8") as f: 
            f.write(f"{phone_name}\n")

def create_and_save_new_group(db_data, size, panel, sensor, phone_name):
    """خطة الطوارئ 3: دالة الحفظ المفقودة لبناء هيكل المجموعة الجديدة كلياً وكتابتها بالملف."""
    if size not in db_data:
        db_data[size] = {}
    if panel not in db_data[size]:
        db_data[size][panel] = {}
    if sensor not in db_data[size][panel]:
        db_data[size][panel][sensor] = {"models": []}
        
    if phone_name not in db_data[size][panel][sensor]["models"]:
        db_data[size][panel][sensor]["models"].append(phone_name)
        
    # حفظ في قاعدة البيانات الرئيسية وتحديث الفهرس النصي فوراً
    save_db(db_data)
    append_to_models_index(phone_name)
    return True

def run_system_workflows(phone, db_data, suggestions):
    """المحرك الرئيسي لإدارة تدفق العمليات للخطط الثلاث."""
    coords = find_model_coords(db_data, phone) if phone else (None, None, None, None)
    size_str, panel, sensor, real_name = coords if coords else (None, None, None, None)
    
    is_exact_match = (real_name and phone.lower() == real_name.lower())

    # -------------------------------------------------------------
    # الخطة 1: عرض النتائج المباشرة للمطابقة الدقيقة
    # -------------------------------------------------------------
    if is_exact_match:
        draw_technical_coords(size_str, panel, sensor)
        results = get_compatibles_strict(db_data, phone)
        if results:
            # تمرير المعاملات الكاملة لتفادي خطأ TypeError في واجهة النيون
            draw_neon_section(
                title="الهواتف المتوافقة تماماً:", 
                models_list=results, 
                color_hex="#00f3ff", 
                badge_icon="📱", 
                current_search=phone
            )
        else:
            st.info("لا توجد هواتف مطابقة لهذه المواصفات حالياً في قاعدة البيانات.")
        append_to_models_index(phone)

    # -------------------------------------------------------------
    # الخطط اليدوية والطوارئ (عند عدم تطابق الاسم وعدم وجود اقتراحات)
    # -------------------------------------------------------------
    if phone != "" and not is_exact_match and not suggestions:
        st.markdown("---")
        
        # جلب التلميحات السريعة من الـ AI
        if f"hint_{phone}" not in st.session_state:
            st.session_state[f"hint_{phone}"] = ai_background_global_verify(phone)
        ai_hint = st.session_state[f"hint_{phone}"]
            
        # تصميم حقول المدخلات الفنية بشكل أفقي متناسق
        col1, col2, col3 = st.columns(3)
        with col1:
            default_size = ai_hint["size"] if ai_hint else ""
            new_size = st.text_input("مقاس الشاشة (مثال: 6.67):", value=default_size, key="input_size").strip()
        with col2:
            default_panel = ai_hint["panel"] if ai_hint else ""
            chosen_panel = st.text_input("نوع الشاشة (مثال: AMOLED):", value=default_panel, key="input_panel").strip()
        with col3:
            default_sensor = ai_hint["sensor"] if ai_hint else "Unknown"
            chosen_sensor = st.text_input("مستشعر التقارب (Proximity):", value=default_sensor, key="input_sensor").strip()
            
        if new_size and chosen_panel and chosen_sensor:
            matched_list = local_check_existing_size_group(db_data, new_size, chosen_panel)
            
            # -------------------------------------------------------------
            # الخطة 2: التعديل والدمج (المواصفات لها مجموعة مسبقة والموديل جديد)
            # -------------------------------------------------------------
            if matched_list:
                st.info(f"💡 وجدنا مجموعة تطابق هذا المقاس والشاشة تحتوي على: {', '.join(matched_list[:3])}...")
                
                if st.button(f"🔗 دمج '{phone}' مع المجموعة الحالية", key="merge_btn"):
                    if chosen_sensor not in db_data[new_size][chosen_panel]:
                        db_data[new_size][chosen_panel][chosen_sensor] = {"models": []}
                    
                    if phone not in db_data[new_size][chosen_panel][chosen_sensor]["models"]:
                        db_data[new_size][chosen_panel][chosen_sensor]["models"].append(phone)
                        save_db(db_data)
                        append_to_models_index(phone)
                        st.session_state["show_success_alert"] = f"✅ تم دمج وتحديث قاعدة البيانات بنجاح للهاتف '{phone}'!"
                        st.rerun()
            
            # -------------------------------------------------------------
            # الخطة 3: خطة الطوارئ (لا توجد أي مجموعة مطابقة - إنشاء مجموعة جديدة)
            # -------------------------------------------------------------
            else:
                # رسالة الخطأ الحمراء الموضحة في صورتك
                st.error("❌ خطة الطوارئ (الخطة 3): لا توجد مجموعة مسبقة تطابق هذه المواصفات.")
                
                if st.button(f"📝 إنشاء مجموعة جديدة وإدراج الهاتف", key="force_create_new_group_btn"):
                    # استدعاء دالة الحفظ الصريحة التي تحل مشكلة عدم استجابة الزر
                    success = create_and_save_new_group(db_data, new_size, chosen_panel, chosen_sensor, phone)
                    if success:
                        st.session_state["show_success_alert"] = f"🎉 تم إنشاء مجموعة جديدة بنجاح وإدراج الهاتف '{phone}' وتحديث الفهرس تلقائياً!"
                        st.rerun()

    # -------------------------------------------------------------
    # عرض التنبيه الأخضر بثبات تام بعد إعادة تحديث الصفحة (Rerun)
    # -------------------------------------------------------------
    if "show_success_alert" in st.session_state:
        st.success(st.session_state["show_success_alert"])
        st.balloons()
        del st.session_state["show_success_alert"]
