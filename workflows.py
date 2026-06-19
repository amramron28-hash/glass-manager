import os
import streamlit as st
import requests
from database import load_db, save_db

from logic_engine import (
    find_model_coords,
    get_compatibles_strict
)

from ui_components import (
    draw_technical_coords,
    draw_neon_section
)

def local_check_existing_size_group(db, target_size, target_panel):
    matched_models = []
    if target_size in db:
        if target_panel in db[target_size]:
            for sensor, s_data in db[target_size][target_panel].items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                for m in models_list:
                    matched_models.append(m)
    return matched_models

def ai_background_global_verify(phone_name):
    try:
        url = f"https://vercel.app{requests.utils.quote(phone_name)}"
        res = requests.get(url, timeout=1.5).json()
        if res and "specs" in res:
            return {
                "size": str(res["specs"].get("display_size", "")),
                "panel": str(res["specs"].get("display_type", "")),
                "sensor": str(res["specs"].get("proximity_type", ""))
            }
    except:
        pass
    return None

def append_to_models_index(phone_name):
    INDEX_FILE = "models_index.txt"
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            current_models = [line.strip() for line in f if line.strip()]
        if phone_name not in current_models:
            with open(INDEX_FILE, "a", encoding="utf-8") as f:
                f.write(f"{phone_name}\n")

def run_system_workflows(phone, db_data, suggestions):
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone) if phone else (None, None, None, None)
    is_exact_match = True if real_name and phone.lower() == real_name.lower() else False
    
    # ------------------------------------------------------------
    # الخطة 1: نتائج التوافق الفورية
    # ------------------------------------------------------------
    if is_exact_match:
        st.markdown(f"<div class='section-title' style='text-align: right; color: #ffffff; font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 8px;'>📊 نتائج التوافق للهاتف: <span style='color: #00bfff;'>{real_name}</span></div>", unsafe_allow_html=True)
        draw_technical_coords(size_str, panel, sensor)
        results = get_compatibles_strict(db_data, phone)
        if "exact" in results: draw_neon_section("هواتف مطابقة تماماً", [m for m in results["exact"] if m not in results.get("warn", [])], "#2ecc71", "🟢", phone)
        if "plus" in results: draw_neon_section("هواتف أكبر بقليل (Plus)", results["plus"], "#3498db", "🔵", phone)
        if "minus" in results: draw_neon_section("هواتف أصغر بقليل (Minus)", results["minus"], "#e67e22", "🟤", phone)
        if results.get("warn"): draw_neon_section("تنبيه حساس", results["warn"], "#ef4444", "⚠️", phone)

    # ------------------------------------------------------------
    # الخطة 2 و 3: المعالجة اليدوية
    # ------------------------------------------------------------
    should_open_manual_workflow = (phone != "" and not is_exact_match and not suggestions)
    if should_open_manual_workflow:
        st.markdown("---")
        st.warning(f"⚠️ الهاتف ({phone}) غير مسجل. يرجى إدخال المواصفات:")
        
        col_s, col_p, col_se = st.columns(3)
        with col_s: new_size = st.text_input("📐 المقاس الرقمي:", key="workflow_size").strip()
        
        chosen_panel = ""
        if new_size:
            with col_p:
                selected_panel = st.selectbox("🖥️ نوع الشاشة:", ["", "Punch-Hole Screen", "Notch Screen", "Waterdrop Notch", "Full Screen", "➕ إضافة شكل جديد..."], key="workflow_panel")
                chosen_panel = st.text_input("✍️ شكل الشاشة:", key="custom_panel_input").strip() if selected_panel == "➕ إضافة شكل جديد..." else selected_panel
        
        chosen_sensor = ""
        if new_size and chosen_panel:
            with col_se:
                selected_sensor = st.selectbox("👁️ مستشعر التقارب:", ["", "hardware_top_sensor", "virtual_camera_sensor", "under_display_fingerprint", "➕ إضافة مستشعر جديد..."], key="workflow_sensor")
                chosen_sensor = st.text_input("✍️ نوع المستشعر:", key="custom_sensor_input").strip() if selected_sensor == "➕ إضافة مستشعر جديد..." else selected_sensor

        if new_size and chosen_panel and chosen_sensor:
            matched_list = local_check_existing_size_group(db_data, new_size, chosen_panel)
            st.markdown("---")
            
            # التأكد من حالة النجاح
            success_key = f"success_saved_{phone}"
            if success_key not in st.session_state: st.session_state[success_key] = False

            if not st.session_state[success_key]:
                if matched_list:
                    st.info(f"💡 تم رصد مجموعة مطابقة! الموديلات: {', '.join(matched_list)}")
                    if st.button("🔗 دمج الموديل الجديد وتحديث السحاب"):
                        db_data.setdefault(new_size, {}).setdefault(chosen_panel, {}).setdefault(chosen_sensor, {"models": []})["models"].append(phone)
                        save_db(db_data)
                        append_to_models_index(phone)
                        st.session_state[success_key] = True
                        st.rerun()
                else:
                    st.error("❌ لا توجد مجموعة مسبقة مطابقة.")
                    if st.button("➕ إنشاء مجموعة جديدة وإدراج الهاتف"):
                        db_data.setdefault(new_size, {}).setdefault(chosen_panel, {}).setdefault(chosen_sensor, {"models": []})["models"].append(phone)
                        save_db(db_data)
                        append_to_models_index(phone)
                        st.session_state[success_key] = True
                        st.rerun()
            else:
                st.markdown("<div style='padding:15px; background-color:#2ecc71; color:white; border-radius:8px; font-weight:bold; text-align:center;'>✅ تم إنجاز العملية بنجاح!</div>", unsafe_allow_html=True)
                if st.button("🔄 تحديث النظام"):
                    st.session_state[success_key] = False
                    st.rerun()

