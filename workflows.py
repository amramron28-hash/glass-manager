import os
import streamlit as st
from ui_components import draw_technical_coords, draw_neon_section
from logic_engine import find_model_coords, get_compatibles_strict
from database import save_db
from main_module import local_check_existing_size_group, ai_background_global_verify

def append_to_models_index(phone_name):
    """تحديث ملف الفهرس النصي واستقبال أسماء الهواتف تلقائياً دون تكرار."""
    INDEX_FILE = "models_index.txt"
    phone_name = phone_name.strip()
    
    # إنشاء الملف إذا لم يكن موجوداً من قبل
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            pass
            
    # قراءة الأسماء الحالية لتجنب التكرار
    with open(INDEX_FILE, "r", encoding="utf-8") as f: 
        current_models = [line.strip().lower() for line in f if line.strip()]
    
    # إضافة الهاتف الجديد فقط إذا لم يكن مسجلاً مسبقاً
    if phone_name.lower() not in current_models:
        with open(INDEX_FILE, "a", encoding="utf-8") as f: 
            f.write(f"{phone_name}\n")

def create_and_save_new_group(db_data, size, panel, sensor, phone_name):
    """خطة الطوارئ 3: بناء الهيكل الشجري الجديد للمجموعة وحفظها بالملف."""
    if size not in db_data:
        db_data[size] = {}
    if panel not in db_data[size]:
        db_data[size][panel] = {}
    if sensor not in db_data[size][panel]:
        db_data[size][panel][sensor] = {"models": []}
        
    if phone_name not in db_data[size][panel][sensor]["models"]:
        db_data[size][panel][sensor]["models"].append(phone_name)
        
    # حفظ في قاعدة البيانات الرئيسية
    save_db(db_data)
    # تحديث ملف الفهرس النصي تلقائياً
    append_to_models_index(phone_name)
    return True

def run_system_workflows(phone, db_data, suggestions):
    coords = find_model_coords(db_data, phone) if phone else (None, None, None, None)
    size_str, panel, sensor, real_name = coords if coords else (None, None, None, None)
    
    is_exact_match = (real_name and phone.lower() == real_name.lower())

    # -------------------------------------------------------------
    # الخطة 1: المطابقة الدقيقة والكاملة (الهاتف مسجل مسبقاً)
    # -------------------------------------------------------------
    if is_exact_match:
        draw_technical_coords(size_str, panel, sensor)
        results = get_compatibles_strict(db_data, phone)
        if results:
            draw_neon_section("الهواتف المتوافقة تماماً:", results)
        else:
            st.info("لا توجد هواتف مطابقة لهذه المواصفات حالياً في قاعدة البيانات.")
        # تحديث تلقائي للفهرس لضمان تسجيله لو كان مفقوداً
        append_to_models_index(phone)

    # -------------------------------------------------------------
    # الخطط اليدوية والطوارئ (عند عدم وجود تطابق مباشر)
    # -------------------------------------------------------------
    if phone != "" and not is_exact_match and not suggestions:
        st.markdown("---")
        
        # جلب التلميحات الذكية من الـ AI في الخلفية لتسهيل الإدخال
        if f"hint_{phone}" not in st.session_state:
            st.session_state[f"hint_{phone}"] = ai_background_global_verify(phone)
        ai_hint = st.session_state[f"hint_{phone}"]
            
        # حقول إدخال المواصفات الفنية
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
            # التحقق من وجود مجموعة توافق هذه المواصفات محلياً
            matched_list = local_check_existing_size_group(db_data, new_size, chosen_panel)
            
            # -------------------------------------------------------------
            # الخطة 2: التعديل والدمج (المواصفات موجودة والموديل جديد)
            # -------------------------------------------------------------
            if matched_list:
                st.info(f"💡 وجدنا مجموعة تطابق هذا المقاس والشاشة تحتوي على: {', '.join(matched_list[:3])}...")
                
                if st.button(f"🔗 دمج '{phone}' مع المجموعة الحالية", key="merge_btn"):
                    if chosen_sensor not in db_data[new_size][chosen_panel]:
                        db_data[new_size][chosen_panel][chosen_sensor] = {"models": []}
                    
                    if phone not in db_data[new_size][chosen_panel][chosen_sensor]["models"]:
                        db_data[new_size][chosen_panel][chosen_sensor]["models"].append(phone)
                        save_db(db_data)
                        append_to_models_index(phone) # ربط وتحديث الفهرس تلقائياً
                        st.session_state["show_success_alert"] = f"✅ تم دمج وتحديث قاعدة البيانات بنجاح للهاتف '{phone}'!"
                        st.rerun()
            
            # -------------------------------------------------------------
            # الخطة 3: خطة الطوارئ (لا توجد أي مجموعة مطابقة - إنشاء كلي)
            # -------------------------------------------------------------
            else:
                # رسالة خطة الطوارئ المطابقة لتصميم واجهتك تماماً
                st.error("❌ خطة الطوارئ (الخطة 3): لا توجد مجموعة مسبقة تطابق هذه المواصفات.")
                
                if st.button(f"📝 إنشاء مجموعة جديدة وإدراج الهاتف", key="force_create_new_group_btn"):
                    # استدعاء دالة الطوارئ التي تبني الهيكل وتحدث ملف الفهرس تلقائياً
                    success = create_and_save_new_group(db_data, new_size, chosen_panel, chosen_sensor, phone)
                    
                    if success:
                        st.session_state["show_success_alert"] = f"🎉 تم إنشاء مجموعة جديدة بنجاح وإدراج الهاتف '{phone}' وتحديث الفهرس تلقائياً!"
                        st.rerun()

    # -------------------------------------------------------------
    # عرض نافذة النجاح الخضراء بشكل مستقر وثابت بعد الـ rerun
    # -------------------------------------------------------------
    if "show_success_alert" in st.session_state:
        st.success(st.session_state["show_success_alert"])
        st.balloons()
        del st.session_state["show_success_alert"]
