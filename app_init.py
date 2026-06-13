from database import load_db

def initialize_system_data():
    """
    قراءة قاعدة البيانات وتطهيرها من المسافات، وحساب حصص الـ RAM للبراندات
    """
    db_data = load_db()
    all_flat_models = []
    all_available_sizes = []
    all_available_panels = []
    total_models = 0
    empty_groups_count = 0
    brand_counts = {}

    for size, panels in db_data.items():
        all_available_sizes.append(size.strip())
        size_has_models = False
        for panel, sensors in panels.items():
            if panel.strip() not in all_available_panels: 
                all_available_panels.append(panel.strip())
            for sensor, s_data in sensors.items():
                models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                if models_list:
                    size_has_models = True
                    total_models += len(models_list)
                    for model in models_list:
                        all_flat_models.append(model.strip())
                        first_word = model.split()[0] if model.split() else "Unknown"
                        brand_counts[first_word] = brand_counts.get(first_word, 0) + 1
        if not size_has_models: 
            empty_groups_count += 1

    unique_models = sorted(list(set(all_flat_models)))
    
    return db_data, unique_models, total_models, empty_groups_count, brand_counts

