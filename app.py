import os
import base64
import pandas as pd
from html import escape
from shiny import App, ui, render, reactive
from ui_components import inject_pwa_and_styles

# 1. تحويل صورة الخلفية المرفقة لترميز ويب آمن
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# 2. تصميم واجهة المستخدم (UI)
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML('<link rel="manifest" href="/manifest.json">'),
        ui.HTML('<link rel="apple-touch-icon" href="/AMMAR.jpg">'),
        ui.HTML('<meta name="theme-color" content="#00bfff">'),
        ui.HTML('<meta name="apple-mobile-web-app-capable" content="yes">'),
        ui.HTML('<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'),

        ui.HTML("""
        <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/service-worker.js')
            .then(reg => console.log('PWA Connected'))
            .catch(err => console.log('PWA Failed', err));
        }

        if (window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches) {
            document.addEventListener('click', e => {
                const target = e.target.closest('a');
                if (target && target.host === window.location.host) {
                    e.preventDefault();
                    window.location.href = target.href;
                }
            }, false);
        }
        </script>
        """),

        ui.HTML(inject_pwa_and_styles()),

        ui.HTML(f"""
        <style>
        .main-header-container {{
            width: 100%;
            text-align: center;
            margin-top: 20px;
            margin-bottom: 25px;
            padding: 5px;
            background: rgba(13,17,23,0.7);
            border-radius: 8px;
        }}

        .main-logo {{
            font-size: 24px !important;
            font-weight: 900 !important;
            color: #00bfff !important;
            text-shadow: 0 0 10px rgba(0,191,255,0.6),
                         0 0 20px rgba(0,191,255,0.4) !important;
            line-height: 1.4 !important;
        }}

        .main-subtitle {{
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            opacity: 0.9;
            margin-top: 8px;
        }}

        .search-wrapper-box {{
            width: 100% !important;
            max-width: 85% !important;
            margin: 0 auto !important;
            position: relative !important;
        }}

        .shiny-input-container {{
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        .shiny-input-container input {{
            background: rgba(255,255,255,0.07) !important;
            color: white !important;
            border: 1px solid rgba(0,191,255,0.3) !important;
            border-radius: 6px;
            padding: 12px;
            width: 100% !important;
            text-align: left !important;
            direction: ltr !important;
        }}

        .curtain-dropdown-menu {{
            position: absolute !important;
            top: 100% !important;
            left: 0 !important;
            width: 100% !important;
            background: rgba(10,14,23,0.98) !important;
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border-left: 1px solid #00bfff !important;
            border-right: 1px solid #00bfff !important;
            border-bottom: 1px solid #00bfff !important;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            z-index: 99999 !important;
            box-shadow: 0 10px 25px rgba(0,191,255,0.35) !important;
            padding: 5px 0;
            margin-top: 2px;
        }}

        .curtain-title {{
            padding: 8px 15px;
            font-size: 13px;
            color: #00bfff;
            font-weight: bold;
            border-bottom: 1px solid rgba(0,191,255,0.15);
            text-align: right;
            direction: rtl;
        }}

        .suggestion-link-btn {{
            background: transparent;
            color: #ffffff;
            border: none;
            width: 100%;
            text-align: left;
            padding: 10px 15px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s ease;
            direction: ltr;
        }}

        .suggestion-link-btn:hover {{
            background-color: rgba(0,191,255,0.15);
            color: #00bfff;
            padding-left: 22px;
        }}

        .row,
        .col-12,
        .p-1,
        .p-2,
        .shiny-output-ui {{
            width: 100% !important;
            max-width: 100% !important;
            display: block !important;
            clear: both !important;
            float: none !important;
            padding: 0 !important;
            margin: 0 !important;
            box-sizing: border-box !important;
        }}

        .side-drawer-container {{
            position: fixed;
            top: 15px;
            left: -290px;
            width: 290px;
            height: auto;
            background: rgba(13,17,23,0.95);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid #00bfff;
            box-shadow: 0 0 25px rgba(0,191,255,0.4);
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
            transition: left 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
            z-index: 9999;
            padding: 15px;
            direction: ltr;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .side-drawer-container.drawer-open {{
            left: 0 !important;
        }}

        .drawer-toggle-btn {{
            position: absolute;
            top: 50%;
            right: -35px;
            transform: translateY(-50%);
            width: 35px;
            height: 45px;
            background: rgba(13,17,23,0.95);
            border-top: 1px solid #00bfff;
            border-right: 1px solid #00bfff;
            border-bottom: 1px solid #00bfff;
            border-left: none;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            color: #00bfff;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 5px 0 15px rgba(0,191,255,0.3);
        }}

        .drawer-observer {{
            font-size: 11px;
            color: #a0aec0;
            white-space: nowrap;
        }}

        .drawer-observer span {{
            color: #32cd32;
            font-weight: bold;
        }}

        .drawer-icon-btn {{
            background: transparent;
            border: none;
            font-size: 20px;
            cursor: pointer;
            transition: transform 0.2s;
            padding: 0 5px;
        }}

        .drawer-icon-btn:hover {{
            transform: scale(1.15);
        }}

        .bell-wrapper {{
            position: relative;
            display: inline-block;
        }}

        .bell-dot-mini {{
            position: absolute;
            top: 1px;
            right: 4px;
            width: 7px;
            height: 7px;
            background: #ff4500;
            border-radius: 50%;
        }}

        @media (max-width:480px) {{
            .side-drawer-container {{
                width: 260px;
                left: -260px;
            }}
        }}

        /* تنسيقات حقول الطوارئ بالتوالي */
        .step-container {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px dashed #00bfff;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            direction: rtl;
            text-align: right;
        }}
        .step-title {{
            color: #00bfff;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        .step-next-btn {{
            background: #00bfff;
            color: #000;
            border: none;
            padding: 6px 15px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }}
        </style>
        """)
    ),

    ui.HTML("""
    <div id="side_drawer" class="side-drawer-container">
        <button id="drawer_toggle" class="drawer-toggle-btn" onclick="toggleDrawer()">🡪</button>
        <button class="drawer-icon-btn" onclick="alert('⚙️ الإعدادات: التفاوت المسموح للزجاج مثبت على 0.03mm لتجنب عيوب الأبعاد.')">⚙️</button>
    </div>
    """),

    ui.HTML("""
    <script>
    function toggleDrawer() {
        var drawer = document.getElementById('side_drawer');
        var btn = document.getElementById('drawer_toggle');

        if (drawer.classList.contains('drawer-open')) {
            drawer.classList.remove('drawer-open');
            btn.innerHTML = '🡪';
        } else {
            drawer.classList.add('drawer-open');
            btn.innerHTML = '🡨';
        }
    }

    document.addEventListener('click', function(event) {
        var drawer = document.getElementById('side_drawer');
        var btn = document.getElementById('drawer_toggle');

        if (
            !drawer.contains(event.target) &&
            drawer.classList.contains('drawer-open')
        ) {
            drawer.classList.remove('drawer-open');
            btn.innerHTML = '🡪';
        }
    });
    </script>
    """),

    ui.HTML("""
    <div class="main-header-container">
        <div class="main-logo">
# ==============================================================================
# 🧠 3. منطق السيرفر والمزامنة الجلسية للخطط البديلة
# ==============================================================================

def server(input, output, session):

    from database import load_db, save_db
    from workflows import run_system_workflows, find_model_coords

    # تحميل قاعدة البيانات المحدثة من Supabase أو الملف المحلي
    db_data = reactive.value(load_db())

    # متغيرات تتبع جلسة الخطوات المتتالية للخطة 2 و 3
    current_step = reactive.value(1)  # 1: المقاس، 2: نوع الشاشة، 3: المستشعر، 4: النتيجة والتثبيت
    manual_size = reactive.value("")
    manual_panel = reactive.value("")
    manual_sensor = reactive.value("")

    # رصد أي تغيير في صندوق البحث لتصفير الخطوات تلقائياً في حال كتابة هاتف جديد
    @reactive.effect
    @reactive.event(input.free_smart_search_input_field)
    def reset_emergency_flow():
        current_step.set(1)
        manual_size.set("")
        manual_panel.set("")
        manual_sensor.set("")

    @reactive.calc
    def filtered_suggestions():
        query = input.free_smart_search_input_field().strip()

        if not query or len(query) < 2:
            return []

        base_dir = os.path.dirname(os.path.abspath(__file__))
        index_file = os.path.join(base_dir, "models_index.txt")

        paths_to_try = [
            index_file,
            "models_index.txt",
            "./models_index.txt",
            "/app/models_index.txt"
        ]

        models = []

        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        models = [
                            line.strip()
                            for line in f
                            if line.strip()
                        ]

                    if models:
                        break

                except Exception:
                    pass

        if not models:
            return []

        return [
            model
            for model in models
            if query.lower() in model.lower()
        ][:5]

    # ==========================================================================
    # الستارة الذكية للبحث السريع
    # ==========================================================================

    @render.ui
    def floating_suggestions_ui():
        suggestions = filtered_suggestions()
        query = input.free_smart_search_input_field().strip()

        if not suggestions or query in suggestions:
            return ui.HTML("")

        html = []
        html.append("<div class='curtain-dropdown-menu'>")
        html.append("<div class='curtain-title'>💡 الموديلات المقترحة القريبة:</div>")

        for item in suggestions:
            html.append(f"""
            <button
                class="suggestion-link-btn"
                onclick="
                    document.getElementById('free_smart_search_input_field').value='{item}';
                    Shiny.setInputValue('free_smart_search_input_field', '{item}');
                ">
                {item}
            </button>
            """)

        html.append("</div>")
        return ui.HTML("\n".join(html))

    # ==========================================================================
    # معالجة وعرض نتائج الخطة 1 الأساسية
    # ==========================================================================

    @render.ui
    def matched_results_ui():
        query = input.free_smart_search_input_field().strip()

        if not query or len(query) < 2:
            return ui.HTML("")

        suggestions = filtered_suggestions()

        try:
            html_result = run_system_workflows(query, db_data.get(), suggestions)
            return ui.HTML(html_result)
        except Exception as e:
            return ui.HTML(f"<div style='color:#ff4500; text-align:center; padding:10px;'>⚠️ خطأ نظام: {str(e)}</div>")

    # ==========================================================================
    # ⚙️ محرك توالي الخطة 2 و 3 في حال غياب الموديل عن قاعدة البيانات
    # ==========================================================================

    @render.ui
    def emergency_steps_flow_ui():
        query = input.free_smart_search_input_field().strip()
        if not query or len(query) < 2:
            return ui.HTML("")

        size_str, panel, sensor, real_name = find_model_coords(db_data.get(), query)
        is_exact_match = True if real_name and query.lower() == real_name.lower() else False

        if is_exact_match:
            return ui.HTML("")

        step = current_step.get()

        # 🔳 الخطة 2 - المرحلة 1: طلب مقاس الشاشة يدويًا
        if step == 1:
            return ui.div(
                ui.div("📏 الخطة 2 (المرحلة الأولى): حدد مقاس الشاشة المطلوب", class_="step-title"),
                ui.input_select("step_size_select", "اختر مقاس دقيق بالإنش:", 
                                choices=["6.40", "6.43", "6.50", "6.55", "6.67", "6.70", "6.78", "6.81"]),
                ui.input_action_button("go_to_step_2", "تأكيد المقاس والانتقال للشكل 🡨", class_="step-next-btn"),
                class_="step-container"
            )

        # 🔳 الخطة 2 - المرحلة 2: طلب شكل ونوع الشاشة
        elif step == 2:
            return ui.div(
                ui.div(f"📺 المقاس المعتمد: {manual_size.get()} | المرحلة الثانية: حدد شكل الشاشة", class_="step-title"),
                ui.input_select("step_panel_select", "اختر نوع وتصميم الشاشة الحالية:", 
                                choices=["Notch Screen", "Punch Hole", "Dynamic Island", "Curved Screen"]),
                ui.input_action_button("go_to_step_3", "تأكيد التصميم والانتقال للمستشعر 🡨", class_="step-next-btn"),
                class_="step-container"
            )

        # 🔳 الخطة 2 - المرحلة 3: طلب نوع مستشعر التقارب
        elif step == 3:
            return ui.div(
                ui.div(f"🔌 المقاس: {manual_size.get()} | الشاشة: {manual_panel.get()} | المرحلة الثالثة: المستشعر", class_="step-title"),
                ui.input_select("step_sensor_select", "اختر نوع مستشعر التقارب:", 
                                choices=["Hardware Sensor", "Virtual Sensor", "Under Display"]),
                ui.input_action_button("trigger_emergency_plan_3", "معالجة ومطابقة خطة الطوارئ النهائية 🔍", class_="step-next-btn"),
                class_="step-container"
            )

        # ⚠️ الخطة 3 - مرحلة الاستدلال والمطابقة وبث البيانات إلى Supabase
        elif step == 4:
            target_size = manual_size.get()
            target_panel = manual_panel.get()
            target_sensor = manual_sensor.get()

            matched_models = []
            current_db = db_data.get()
            if target_size in current_db and target_panel in current_db[target_size]:
                if target_sensor in current_db[target_size][target_panel]:
                    s_data = current_db[target_size][target_panel][target_sensor]
                    matched_models = s_data.get("models", []) if isinstance(s_data, dict) else s_data

            compatibles_html = ""
            if matched_models:
                models_buttons = "".join([f"<div style='background:rgba(0,255,204,0.1); border:1px solid #00ffcc; color:#00ffcc; padding:6px 12px; margin:5px; border-radius:4px; display:inline-block; font-weight:bold;'>{escape(m)}</div>" for m in matched_models])
                compatibles_html = f"""
                <div style='margin-top:15px; background:rgba(7,31,33,0.9); padding:12px; border-radius:8px; border:1px solid #00ffcc;'>
                    <span style='color:#00ffcc; font-weight:bold;'>🤖 هواتف بديلة متوافقة تماماً ومدرجة بنفس أبعادك:</span><br><br>
                    {models_buttons}
                </div>
                """
            else:
                compatibles_html = "<div style='color:#ff4500; font-weight:bold; margin-top:10px;'>⚠️ لا توجد موديلات مطابقة حالياً لهذه الأبعاد في النظام.</div>"

            return ui.div(
                ui.HTML(f"""
                <div style="font-size: 20px !important; font-weight: bold !important; color: #ffffff !important; margin-top: 10px !important; margin-bottom: 12px !important; text-align: right !important; direction: rtl !important;">
                    <span style="color:#ff4500; margin-left: 6px;">⚠️</span>نتائج خطة الطوارئ 3 الموحدة للأبعاد اليدوية:
                </div>
                <div class="flat-warning-card" style="background: linear-gradient(135deg, #26090b, #120405) !important; border: 2px solid #ff4500 !important; padding: 16px 20px !important; margin-bottom: 14px !important; border-radius: 12px !important; text-align: right !important; direction: rtl !important; box-shadow: 0px 4px 12px rgba(255, 69, 0, 0.3) !important;">
                    <div style="color: #ffb3b9 !important; font-size: 18px !important; font-weight: 700 !important; line-height: 1.6;">
                        الموديل المستهدف <b>({escape(query)})</b> غير مدرج بالأصل، ولكن تم حصر مواصفاته المرفوعة بنجاح:<br>
                        📌 المقاس المعتمد: <span style="color:#fff;">{escape(target_size)}</span> | 📌 الشاشة: <span style="color:#fff;">{escape(target_panel)}</span> | 📌 المستشعر: <span style="color:#fff;">{escape(target_sensor)}</span>
                    </div>
                    {compatibles_html}
                </div>
                """),
                ui.div(
                    ui.input_action_button("inject_into_supabase_btn", f"⚡ ربط وتوثيق {query} فوراً في قاعدة البيانات السحابية", 
                                            class_="btn btn-success", style="width:100%; font-weight:bold; margin-top:15px; padding:10px;"),
                    style="direction:rtl; text-align:right;"
                ),
                class_="step-container",
                style="border-style:solid; border-color:#ff4500;"
            )

    # ==========================================================================
