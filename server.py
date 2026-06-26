import os
import urllib.request
import json
from shiny import ui, render, reactive

# استيراد الدوال من الملفات المعتمدة بالمشروع
from database import load_db, add_model
from logic_engine import run_system_workflows, get_compatibles_strict, find_model_coords, extract_numeric_size
from ui_components import draw_plan_2_modal, draw_plan_3_modal, draw_warning_card, draw_technical_coords, draw_neon_section

# --- 1. قسم إدارة الحالة والتحويل ---

def convert_database_from_raw(rows):
    db = {}
    for item in rows:
        if not isinstance(item, dict): 
            continue
        size = str(item.get("size") or "").strip()
        panel = str(item.get("panel") or "").strip()
        sensor = str(item.get("sensor") or "").strip()
        model = str(item.get("model_name") or "").strip()
        
        if not size or not model: 
            continue
            
        db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})
        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)
    return db

def setup_server_state(input, output, session):
    db_trigger = reactive.Value(0)
    current_search_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)
    
    # متغيرات حفظ البيانات المدخلة يدوياً في الخطة 2 والخطة 3
    p2_computed_results = reactive.Value(None)
    p2_input_size = reactive.Value("")
    p2_input_panel = reactive.Value("")
    p2_input_sensor = reactive.Value("")
    
    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])
    
    return (db_trigger, current_search_phone, show_curtain, active_modal, 
            p2_computed_results, p2_input_size, p2_input_panel, p2_input_sensor,
            custom_panels, custom_sensors)


# --- 2. محرك الخادم الرئيسي (Server Function) ---

def server(input, output, session):
    # تفكيك الحالات التفاعلية
    (db_trigger, current_search_phone, show_curtain, active_modal, 
     p2_computed_results, p2_input_size, p2_input_panel, p2_input_sensor,
     custom_panels, custom_sensors) = setup_server_state(input, output, session)

    @reactive.calc
    def database_data():
        """جلب محتويات قاعدة البيانات وتحويلها للبنية الشجرية بشكل آمن"""
        db_trigger()
        try:
            rows = load_db()
            if isinstance(rows, list):
                return convert_database_from_raw(rows)
            return rows if isinstance(rows, dict) else {}
        except Exception as e:
            print(f"SERVICE_DATABASE_FETCH_ERROR: {e}")
            return {}

    # --- 3. مراقبة وإدارة أحداث واجهة المستخدم (الخطة 1: البحث التلقائي) ---

    @reactive.effect
    @reactive.event(input.search_query)
    def handle_search_typing():
        query = (input.search_query() or "").strip()
        if query:
            show_curtain.set(True)
            current_search_phone.set(query)
            p2_computed_results.set(None)
        else:
            show_curtain.set(False)
            current_search_phone.set("")
            p2_computed_results.set(None)

    @reactive.effect
    @reactive.event(input.selected_model)
    def handle_suggestion_click():
        selected = input.selected_model()
        if selected:
            ui.update_text("search_query", value=selected, session=session)
            current_search_phone.set(selected)
            show_curtain.set(False)

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer():
        await session.send_custom_message("toggle_drawer", "open")


    # --- الخطة 2: التكامل اليدوي وفحص المجموعات ---

    @reactive.effect
    @reactive.event(input.trigger_plan_2)
    def open_plan_2_dialog():
        db = database_data()
        panels = set()
        sensors = set()
        for size, panel_dict in db.items():
            for p_name, sensor_dict in panel_dict.items():
                if p_name: panels.add(p_name)
                for s_name in sensor_dict.keys():
                    if s_name: sensors.add(s_name)
                    
        custom_panels.set(list(panels))
        custom_sensors.set(list(sensors))
        active_modal.set("plan_2")

    @reactive.effect
    @reactive.event(input.p2_search)
    def process_plan_2_matching():
        """البحث المتقدم داخل المجموعات بناءً على المدخلات اليدوية"""
        size_val = input.p2_size()
        panel_val = input.p2_panel()
        sensor_val = input.p2_sensor()
        
        if size_val is None or not panel_val or not sensor_val:
            return

        p2_input_size.set(f"{size_val} inches")
        p2_input_panel.set(panel_val)
        p2_input_sensor.set(sensor_val)

        db = database_data()
        current_size = float(size_val)
        TOLERANCE = 0.05
        
        compatibles = {"exact": [], "plus": [], "minus": []}
        
        for size_key, panels in db.items():
            loop_size = extract_numeric_size(size_key)
            if loop_size is None: continue
            
            size_diff = loop_size - current_size
            
            for panel_key, sensors in panels.items():
                if panel_key != panel_val: continue
                
                for sensor_key, s_data in sensors.items():
                    models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                    if not isinstance(models_list, list): continue
                    
                    for model in models_list:
                        if abs(size_diff) < 0.001 and sensor_key == sensor_val:
                            if model not in compatibles["exact"]: compatibles["exact"].append(model)
                        elif 0 < size_diff <= TOLERANCE:
                            if model not in compatibles["plus"]: compatibles["plus"].append(model)
                        elif -TOLERANCE <= size_diff < 0:
                            if model not in compatibles["minus"]: compatibles["minus"].append(model)

        if compatibles["exact"] or compatibles["plus"] or compatibles["minus"]:
            p2_computed_results.set(compatibles)
            active_modal.set(None)
        else:
            p2_computed_results.set("__EMPTY_PLAN2__")
            active_modal.set("plan_3")

    @reactive.effect
    @reactive.event(input.btn_learn_and_merge)
    def handle_learning_and_merge():
        phone = current_search_phone().strip()
        size = p2_input_size()
        panel = p2_input_panel()
        sensor = p2_input_sensor()
        
        if phone and size and panel and sensor:
            success = add_model(size, panel, sensor, phone)
            if success:
                db_trigger.set(db_trigger() + 1)
                p2_computed_results.set(None)
                ui.update_text("search_query", value=phone, session=session)


    # --- خطة الطوارئ 3: التأسيس والإنشاء ---

    @reactive.effect
    @reactive.event(input.p3_search)
    def process_plan_3_creation():
        phone = current_search_phone().strip()
        size_val = input.p3_size()
        panel_val = input.p3_panel()
        sensor_val = input.p3_sensor()
        
        if phone and size_val and panel_val and sensor_val:
            size_str = f"{size_val} inches"
            success = add_model(size_str, panel_val, sensor_val, phone)
            if success:
                db_trigger.set(db_trigger() + 1)
                active_modal.set(None)
                p2_computed_results.set(None)
    # --- 4. مخرجات العرض الذكية (Render Outputs) ---

    @render.ui
    def suggestions_curtain():
        if not show_curtain(): return None
        q = current_search_phone().lower().strip()
        if not q: return None
        
        db = database_data()
        all_models = set()
        for size, panels in db.items():
            for panel, sensors in panels.items():
                for sensor, s_data in sensors.items():
                    for model in s_data.get("models", []):
                        all_models.add(model)
                        
        matches = [m for m in all_models if q in m.lower()][:8]
        if not matches: return None
        
        return ui.div(
            *[ui.div(m, class_="suggestion-row", onclick=f"Shiny.setInputValue('selected_model', '{m}', {{priority:'event'}});") for m in matches], 
            class_="suggestions-curtain"
        )

    @render.ui
    def results_area():
        p = current_search_phone().strip()
        if not p: return None
        
        db = database_data()
        size, panel, sensor, real_name = find_model_coords(db, p)
        
        if real_name:
            workflow_html = run_system_workflows(p, db, "")
            return ui.HTML(workflow_html)
            
        p2_res = p2_computed_results()
        if isinstance(p2_res, dict):
            output_cards = [
                draw_technical_coords(p2_input_size(), p2_input_panel(), p2_input_sensor(), f"{p} (مواصفات يدوية)"),
                draw_neon_section("مجموعات مطابقة تماماً مقترحة", p2_res.get("exact", []), "#2ecc71", "🟢", "exact"),
                draw_neon_section("مجموعات أكبر بقليل مقترحة", p2_res.get("plus", []), "#3498db", "🔵", "plus"),
                draw_neon_section("مجموعات أصغر قليلاً مقترحة", p2_res.get("minus", []), "#e67e22", "🟠", "minus"),
                ui.div(
                    ui.input_action_button(
                        "btn_learn_and_merge", 
                        f"🔄 دمج {p} في هذه المجموعة لتعلّمها مستقبلاً", 
                        style="width:100%; background:#2ecc71; color:white; padding:14px; border-radius:12px; font-weight:bold; margin-top:15px; border:none;"
                    )
                )
            ]
            return ui.div(*output_cards)
            
        if p2_res == "__EMPTY_PLAN2__":
            return ui.div(
                draw_warning_card(
                    f"فشلت خطة المطابقة الفنية لـ {p}. تم الانتقال لواجهة التأسيس."
                )
            )

        return ui.div(
            draw_warning_card(
                f"الموديل {p} غير مسجل مسبقاً في النظام"
            ),
            ui.div(style="margin-top:20px; text-align:center;"),
            ui.input_action_button(
                "trigger_plan_2",
                "🔵 ابدأ فحص المجموعات والمطابقة الفنية (الخطة 2)",
                style="""
                width:100%;
                background:#00bfff;
                color:white;
                padding:14px;
                border-radius:12px;
                font-weight:bold;
                border:none;
                """
            )
        )

    @render.ui
    def modal_layer():
        mode = active_modal()

        if mode == "plan_2":
            return draw_plan_2_modal(
                current_search_phone(),
                custom_panels(),
                custom_sensors()
            )

        elif mode == "plan_3":
            return draw_plan_3_modal(
                current_search_phone(),
                custom_panels(),
                custom_sensors()
            )

        return None

