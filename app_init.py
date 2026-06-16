from database import load_db

def initialize_system_data():
    """
    تحميل آمن للبيانات + تنظيف + حساب الإحصائيات + استخراج قوائم النقر الحية لـ app.py
    """
    db_data = load_db() or {}

    all_flat_models = []
    all_available_sizes = []
    all_available_panels = []
    all_available_sensors = []
    total_models = 0
    empty_groups_count = 0
    brand_counts = {}

    for size, panels in db_data.items():
        size_clean = str(size).strip()
        if size_clean and size_clean not in all_available_sizes:
            all_available_sizes.append(size_clean)

        size_has_models = False

        for panel, sensors in panels.items():
            panel_clean = str(panel).strip()
            if panel_clean and panel_clean not in all_available_panels:
                all_available_panels.append(panel_clean)

            for sensor, s_data in sensors.items():
                sensor_clean = str(sensor).strip()
                if sensor_clean and sensor_clean not in all_available_sensors:
                    all_available_sensors.append(sensor_clean)

                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if not models_list:
                    continue

                size_has_models = True

                for model in models_list:
                    model_clean = str(model).strip()
                    if not model_clean:
                        continue

                    all_flat_models.append(model_clean)
                    total_models += 1

                    # استخراج البراند بأمان
                    words = model_clean.split()
                    first_word = words[0] if words else "Unknown"
                    brand_counts[first_word] = brand_counts.get(first_word, 0) + 1

        if not size_has_models:
            empty_groups_count += 1

    unique_models = sorted(list(set(all_flat_models)))

    # 🎯 التعديل الفوري: إرجاع الـ 8 متغيرات كاملة لتطابق محرك واجهة app.py وطرد الصفر
    return db_data, unique_models, total_models, empty_groups_count, brand_counts, all_available_sizes, all_available_panels, all_available_sensors
