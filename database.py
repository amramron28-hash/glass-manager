import streamlit as st
from database import load_db, add_model

# =========================
# 📥 تحميل البيانات
# =========================
db_data = load_db()


# =========================
# 🛡️ حماية القيم (مهم جدًا)
# =========================
def safe_text(value):
    """تحويل أي نوع بيانات إلى نص آمن"""
    if value is None:
        return ""
    if isinstance(value, float):
        return ""
    return str(value).strip()


# =========================
# 🧠 البحث المباشر
# =========================
def smart_phone_flow(db_data, phone_name):
    phone_name = safe_text(phone_name).lower()

    for size, panels in db_data.items():
        for panel, sensors in panels.items():
            for sensor, data in sensors.items():
                for model in data.get("models", []):
                    if phone_name == safe_text(model).lower():
                        return {
                            "status": 1,
                            "size": size,
                            "panel": panel,
                            "sensor": sensor,
                            "model": model
                        }

    return {"status": 2}


# =========================
# 🟡 البحث بالمواصفات
# =========================
def find_similar_group(db_data, size, panel, sensor):
    size = safe_text(size)
    panel = safe_text(panel)
    sensor = safe_text(sensor)

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
# 🔴 إنشاء مجموعة جديدة
# =========================
def create_new_group(db_data, size, panel, sensor, model):
    size = safe_text(size)
    panel = safe_text(panel)
    sensor = safe_text(sensor)
    model = safe_text(model)

    if size not in db_data:
        db_data[size] = {}

    if panel not in db_data[size]:
        db_data[size][panel] = {}

    if sensor not in db_data[size][panel]:
        db_data[size][panel][sensor] = {"models": []}

    if model and model not in db_data[size][panel][sensor]["models"]:
        db_data[size][panel][sensor]["models"].append(model)

    return db_data


# =========================
# 🖥️ واجهة التطبيق
# =========================
st.title("📱 Smart Phone System (Protected Version)")


# =========================
# 📌 إدخال الهاتف
# =========================
phone_name = st.text_input("Enter phone name")


# =========================
# 🔍 تشغيل البحث
# =========================
if st.button("Search"):
    result = smart_phone_flow(db_data, phone_name)

    # 🟢 وجد مباشرة
    if result["status"] == 1:
        st.success("✅ Phone found")
        st.json(result)

    # 🟡 غير موجود
    else:
        st.warning("❌ Not found - enter specifications")

        size = st.text_input("Size")
        panel = st.text_input("Panel")
        sensor = st.text_input("Sensor")

        if st.button("Check Similar"):
            match = find_similar_group(db_data, size, panel, sensor)

            if match["status"] == 2:
                st.success("✅ Similar group found")
                st.json(match["data"])

            else:
                st.error("❌ No match found")

                if st.button("Create New Group"):
                    db_data = create_new_group(
                        db_data,
                        size,
                        panel,
                        sensor,
                        phone_name
                    )

                    st.success("✅ New group created safely")
