import base64
import os
from html import escape
from shiny import App, render, ui, reactive

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

custom_css = f"""
body {{
    background-image: url("{bg_img_base64}");
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-color: #0d1117 !important;
}}
.container-fluid {{ padding: 20px !important; }}
.main-header-container {{
    width: 100%; text-align: center; margin-top: 10px; margin-bottom: 25px; padding: 15px;
    background: rgba(13, 17, 23, 0.7); border-radius: 8px;
}}
.main-logo {{
    font-size: 32px; font-weight: 900; color: #00bfff; 
    text-shadow: 0 0 15px rgba(0,191,255,0.8); line-height: 1.2;
}}
.main-subtitle {{ font-size: 18px; font-weight: 600; color: #ffffff; opacity: 0.95; margin-top: 8px; }}
input[type="text"] {{ background: rgba(255, 255, 255, 0.07) !important; color: white !important; border: 1px solid rgba(0, 191, 255, 0.3) !important; }}
.floating-suggestions-box-title {{ padding: 10px 15px 5px 15px; background: rgba(13, 17, 23, 0.95) !important; border-top: 1px solid #00bfff !important; border-radius: 8px 8px 0 0; }}
.floating-suggestions-box-end {{ background: rgba(13, 17, 23, 0.95) !important; border-bottom: 1px solid #00bfff !important; border-radius: 0 0 8px 8px; margin-bottom: 15px; padding: 10px; display: flex; flex-direction: column; gap: 5px; }}
.suggestion-live-btn {{ background-color: transparent !important; color: #ffffff !important; border: none !important; width: 100% !important; text-align: right !important; padding: 8px 15px !important; transition: all 0.2s ease !important; }}
.suggestion-live-btn:hover {{ background-color: rgba(0, 191, 255, 0.15) !important; color: #00bfff !important; }}
"""

# الصياغة القياسية الصحيحة والمضمونة لواجهة Shiny لمنع خطأ الـ TypeError
app_ui = ui.page_sidebar(
    # تثبيت حاوية الشريط الجانبي هندسياً في الواجهة لتقبلها منصة Shiny
    ui.sidebar(
        ui.output_ui("sidebar_content_inner_render"),
        title="🛠️ لوحة التحكم بالتطبيق",
        position="left",
        bg="rgba(15, 23, 42, 0.85)"
    ),
    
    # محتويات الشاشة الرئيسية المنتصفية
    ui.head_content(
        ui.tags.style(custom_css),
        ui.tags.title("ZEGAAR AMMAR GLASS MANAGER")
    ),
    ui.HTML("""
        <div class="main-header-container">
            <div class="main-logo">ZEGAAR AMMAR<br>GLASS MANAGER</div>
            <div class="main-subtitle">النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>
        </div>
    """),
    
    # حقل البحث الحر الثابت والظاهر دائماً للمستخدمين
    ui.input_text("free_smart_search_input_field", label="", value="", placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة..."),
    
    # حاوية النتائج والبطاقات الزجاجية الملونة
    ui.output_ui("dynamic_cards_render")
)

def server(input, output, session):
    from app_init import initialize_system_data
    from workflows import run_system_workflows
    from ui_components import draw_control_panel
    from logic_engine import run_intelligent_inspector, detect_self_conflicts

    # تشغيل عين ويد المراقب الصامت للتطهير الأمني التلقائي
    cleaned_db_data, changes_were_made = run_intelligent_inspector()
    conflict_alerts = detect_self_conflicts()
    
    system_notifications = []
    if changes_were_made:
        system_notifications.append("المراقب الصامت: تم العثور على أسطر تالفة أو مكررة وقام النظام بتطهيرها وحذفها تلقائياً.")
    for alert in conflict_alerts:
        system_notifications.append(f"تنبيه تعارض ذاتي: الهاتف '{alert['phone']}' مسجل بمستشعرات متعددة {alert['sensors']}")

    (db_data, _initial_unique_models, total_models, empty_groups_count, _, _, _, _) = initialize_system_data()
    
    if changes_were_made and cleaned_db_data:
        db_data = cleaned_db_data

    unique_models = _initial_unique_models
    INDEX_FILE = "models_index.txt"
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            unique_models = sorted(list(set([line.strip() for line in f if line.strip()])))

    def fast_phone_search(searchterm):
        if not searchterm: return []
        term = searchterm.lower().strip()
        starts_with = [m for m in unique_models if m.lower().startswith(term)]
        contains = [m for m in unique_models if term in m.lower() and m not in starts_with]
        return (starts_with + contains)[:10]

    search_val = reactive.Value("")

    @reactive.Effect
    @reactive.event(input.free_smart_search_input_field)
    def update_reactive_input():
        search_val.set(input.free_smart_search_input_field().strip())

    # 1. ضخ محتويات لوحة التحكم العميقة (المراقب، الإعدادات، الجرس) داخل حاوية الشريط المستقر
    @output
    @render.ui
    def sidebar_content_inner_render():
        sidebar_object = draw_control_panel(
            notifications=system_notifications, 
            total_models=total_models, 
            empty_groups_count=empty_groups_count
        )
        # استخراج المكونات الداخلية الصافية وحقنها لمنع تكرار الحاويات
        return ui.div(*sidebar_object.children)

    # 2. ضخ الستارة التفاعلية للمساعدة والبطاقات الزجاجية في الشاشة المنتصفية
    @output
    @render.ui
    def dynamic_cards_render():
        phone = search_val()
        suggestions = fast_phone_search(phone) if phone else []
        ui_elements = []
        
        if phone and suggestions:
            is_fully_matched = any(phone.lower() == s.lower() for s in suggestions)
            if not is_fully_matched:
                ui_elements.append(ui.HTML("<div class='floating-suggestions-box-title'><span style='color:#00bfff; font-weight:bold;'>💡 اقتراحات البحث المساعدة:</span></div>"))
                btn_list = []
                for idx, item in enumerate(suggestions):
                    btn_id = f"sug_btn_{idx}"
                    btn_list.append(ui.input_action_button(btn_id, f"🔍 {item}", class_="suggestion-live-btn"))
                    
                    @reactive.Effect
                    @reactive.event(input[btn_id], ignore_none=True)
                    def make_click_handler(target_item=item):
                        ui.update_text("free_smart_search_input_field", value=target_item)
                        search_val.set(target_item)
                ui_elements.append(ui.div(*btn_list, class_="floating-suggestions-box-end"))
        
        workflow_output = run_system_workflows(phone=phone, db_data=db_data, suggestions=suggestions)
        if workflow_output:
            ui_elements.append(ui.HTML(str(workflow_output)))
            
        return ui.div(*ui_elements)

app = App(app_ui, server)
