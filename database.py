import streamlit as st
from database import load_db, add_model

# =========================
# 📥 تحميل البيانات
# =========================
db_data = load_db()


# =========================
# 🧠 المرحلة 1: بحث مباشر
# =========================
def smart_phone_flow(db_data, phone_name):
    phone_name = phone_name.strip().lower()

    for size, panels in db_data.items():
        for panel, sensors in panels.items():
            for sensor, data in sensors.items():
                for model in data.get("models", []):
                    if phone_name == model.lower():
                        return {
                            "status": 1,
                            "size": size,
                            "panel": panel,
                            "sensor": sensor,
                            "model": model
                        }

    return {"status": 2}


# =========================
# 🟡 المرحلة 2: البحث بالمواصفات
# =========================
def find_similar_group(db_data, size, panel, sensor):
    size = str(size).strip()

    if size in db_data:
        if panel in db_data[size]:
            if sensor in db_data[size][panel]:
                return {
                    "status": 2,
                    "found": True,
                    "data": db_data[size][panel][sensor]
                }

    return {"status": 3}


# =========================
# 🔴 المرحلة 3: إنشاء مجموعة
# =========================
def create_new_group(db_data, size, panel, sensor, model):
    size = str(size).strip()

    if size not in db_data:
        db_data[size] = {}

    if panel not in db_data[size]:
        db_data[size][panel] = {}

    if sensor not in db_data[size][panel]:
        db_data[size][panel][sensor] = {"models": []}

    if model not in db_data[size][panel][sensor]["models"]:
        db_data[size][panel][sensor]["models"].append(model)

    return db_data


# =========================
# 🖥️ واجهة Streamlit
# =========================
st.title("📱 Smart Phone System (1-2-3 Flow)")

phone_name = st.text_input("Enter phone name")


# =========================
# 🔍 تشغيل البحث
# =========================
if st.button("Search"):
    result = smart_phone_flow(db_data, phone_name)

    # 🟢 المرحلة 1
    if result["status"] == 1:
        st.success("✅ Found directly in database")
        st.write(result)

    # 🟡 المرحلة 2
    else:
        st.warning("❌ Not found, enter device specs")

        size = st.text_input("Size (example 6.67)")
        panel = st.text_input("Panel (example Notch Screen)")
        sensor = st.text_input("Sensor (example hardware_top_sensor)")

        if st.button("Check Similar"):
            match = find_similar_group(db_data, size, panel, sensor)

            # 🟡 وجد مجموعة مشابهة
            if match["status"] == 2:
                st.success("✅ Similar group found")
                st.write(match["data"])

            # 🔴 لا يوجد أي تطابق
            else:
                st.error("❌ No match found - create new group")

                if st.button("Create New Group"):
                    db_data = create_new_group(
                        db_data,
                        size,
                        panel,
                        sensor,
                        phone_name
                    )
                    st.success("✅ New group created")
