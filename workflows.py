import os
import time
import streamlit as st
import requests

from database import load_db, save_db
from logic_engine import find_model_coords, get_compatibles_strict
from ui_components import draw_technical_coords, draw_neon_section


def local_check_existing_size_group(db, target_size, target_panel):
    matched_models = []

    if target_size in db and target_panel in db[target_size]:
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
            current_models = [
                line.strip()
                for line in f
                if line.strip()
            ]

        if phone_name not in current_models:

            with open(INDEX_FILE, "a", encoding="utf-8") as f:
                f.write(f"{phone_name}\n")


def run_system_workflows(phone, db_data, suggestions):

    size_str, panel, sensor, real_name = (
        find_model_coords(db_data, phone)
        if phone else
        (None, None, None, None)
    )

    is_exact_match = (
        True
        if real_name and phone.lower() == real_name.lower()
        else False
    )

    global_audit_alerts = []


    if is_exact_match:

        st.markdown(
            f"""
            <div class='section-title'
            style='text-align:right;color:#ffffff;
            font-size:20px;font-weight:bold;
            margin-bottom:15px;'>
            📊 نتائج التوافق للهاتف:
            <span style='color:#00bfff'>{real_name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )


        draw_technical_coords(
            size_str,
            panel,
            sensor
        )


        results = get_compatibles_strict(
            db_data,
            phone
        )


        if "exact" in results:

            draw_neon_section(
                "هواتف مطابقة تماماً",
                results["exact"],
                "#2ecc71",
                "🟢",
                phone
            )


        if "plus" in results:

            draw_neon_section(
                "هواتف أكبر قليلاً",
                results["plus"],
                "#3498db",
                "🔵",
                phone
            )


        if "minus" in results:

            draw_neon_section(
                "هواتف أصغر قليلاً",
                results["minus"],
                "#e67e22",
                "🟤",
                phone
            )


        if results.get("warn"):

            draw_neon_section(
                "تنبيه المستشعر",
                results["warn"],
                "#ef4444",
                "⚠️",
                phone
            )


    should_open_manual_workflow = (
        phone != ""
        and not is_exact_match
        and not suggestions
    )


    if should_open_manual_workflow:

        st.warning(
            f"⚠️ الهاتف {phone} غير مسجل. أدخل المواصفات:"
        )


        col_s, col_p, col_se = st.columns(3)


        with col_s:

            new_size = st.text_input(
                "📐 المقاس:",
                key="workflow_size"
            ).strip()


        chosen_panel = ""
        chosen_sensor = ""


        if new_size:

            with col_p:

                selected_panel = st.selectbox(
                    "🖥️ نوع الشاشة:",
                    [
                        "",
                        "Punch-Hole Screen",
                        "Notch Screen",
                        "Waterdrop Notch",
                        "Full Screen",
                        "Flat Screen",
                        "Curved Screen"
                    ],
                    key="workflow_panel"
                )


                chosen_panel = selected_panel.strip()



        if new_size and chosen_panel:

            with col_se:

                selected_sensor = st.selectbox(
                    "👁️ المستشعر:",
                    [
                        "",
                        "hardware_top_sensor",
                        "virtual_camera_sensor",
                        "under_display_sensor",
                        "side_sensor",
                        "no_visible_sensor"
                    ],
                    key="workflow_sensor"
                )


                chosen_sensor = selected_sensor.strip()



        if new_size and chosen_panel and chosen_sensor:


            matched_list = local_check_existing_size_group(
                db_data,
                new_size,
                chosen_panel
            )


            if f"success_saved_{phone}" not in st.session_state:

                st.session_state[f"success_saved_{phone}"] = False



            if matched_list:


                st.info(
                    "💡 تم العثور على مجموعة موجودة"
                )


                if not st.session_state[f"success_saved_{phone}"]:


                    if st.button(
                        "🔗 دمج الهاتف",
                        key="btn_merge_model"
                    ):


                        db_data.setdefault(
                            new_size,
                            {}
                        )

                        db_data[new_size].setdefault(
                            chosen_panel,
                            {}
                        )

                        db_data[new_size][chosen_panel].setdefault(
                            chosen_sensor,
                            {"models":[]}
                        )


                        db_data[new_size][chosen_panel][chosen_sensor]["models"].append(phone)


                        save_db(db_data)

                        append_to_models_index(phone)


                        st.session_state[f"success_saved_{phone}"] = True

                        st.rerun()



            else:


                st.error(
                    "❌ إنشاء مجموعة جديدة"
                )


                if st.button(
                    "➕ تثبيت المجموعة",
                    key="btn_create_group"
                ):


                    db_data.setdefault(
                        new_size,
                        {}
                    )


                    db_data[new_size].setdefault(
                        chosen_panel,
                        {}
                    )


                    db_data[new_size][chosen_panel].setdefault(
                        chosen_sensor,
                        {"models":[]}
                    )


                    if phone not in db_data[new_size][chosen_panel][chosen_sensor]["models"]:

                        db_data[new_size][chosen_panel][chosen_sensor]["models"].append(phone)


                    save_db(db_data)

                    append_to_models_index(phone)


                    st.session_state[f"success_saved_{phone}"] = True

                    st.rerun()



    st.session_state.notifications = global_audit_alerts
