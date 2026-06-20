import os
import base64
from shiny import App, ui, render, reactive
import pandas as pd

# استيراد كافة الدوال والمكونات الفنية لنظامك الحالي
from app_init import initialize_system_data
from workflows import run_system_workflows
from ui_components import draw_control_panel, inject_pwa_and_styles

# 1. تهيئة البيانات الأساسية وقفل قراءة الـ Auto-complete من ملفك النصي
(
    db_data, 
    unique_models_init, 
    total_models, 
    empty_groups_count, 
    brand_counts, 
    all_available_sizes, 
    all_available_panels, 
    all_available_sensors
) = initialize_system_data()

INDEX_FILE = "models_index.txt"
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        unique_models = sorted(list(set([line.strip() for line in f if line.strip()])))
else:
    unique_models = unique_models_init

# تحويل صورة الخلفية برمجياً لترميز آمن ومضمون
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# 🎨 تصميم واجهة المستخدم الشاملة والحاضنة لكل أكواد الـ CSS والـ PWA الخاصة بك
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML(f"""
        <style>
        body, .container-fluid {{
            background-image: url("{bg_img_base64}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-color: #0d1117;
            color: white;
            font-family: sans-serif;
            direction: rtl;
        }}
        .main-header-container {{
            width: 100%;
            text-align: center;
            margin-top: 20px;
            margin-bottom: 25px;
            padding: 5px;
            background: rgba(13, 17, 23, 0.7);
            border-radius: 8px;
        }}
        .main-logo {{
            font-size: 32px; 
            font-weight: 900; 
            color: #00bfff; 
            text-shadow: 0 0 15px rgba(0,191,255,0.8);
            line-height: 1.2;
        }}
        .main-subtitle {{
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            opacity: 0.95;
            margin-top: 8px;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
        }}
        .shiny-input-container input {{
            background: rgba(255, 255, 255, 0.07) !important;
            color: white !important;
            border: 1px solid rgba(0, 191, 255, 0.3) !important;
            border-radius: 6px;
            padding: 10px;
            width: 100%;
            text-align: right;
        }}
        .floating-suggestions-box-title {{
            padding: 10px 15px 5px 15px; 
            background: rgba(13, 17, 23, 0.95) !important; 
            border-top: 1px solid #00bfff !important;
            border-left: 1px solid #00bfff !important;
            border-right: 1px solid #00bfff !important;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-top: 5px;
            box-shadow: 0 -5px 15px rgba(0,191,255,0.2);
        }}
        .floating-suggestions-box-end {{
            background: rgba(13, 17, 23, 0.95) !important; 
            border-bottom: 1px solid #00bfff !important;
            border-left: 1px solid #00bfff !important;
            border-right: 1px solid #00bfff !important;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            margin-bottom: 15px;
            padding-bottom: 5px;
            box-shadow: 0 10px 15px rgba(0,191,255,0.2);
        }}
        .suggestion-link-btn {{
            background: transparent;
            color: #ffffff;
            border: none;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            width: 100%;
            text-align: right;
            padding: 8px 15px;
            font-size: 16px;
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        .suggestion-link-btn:hover {{
            background-color: rgba(0, 191, 255, 0.15);
            color: #00bfff;
            padding-right: 25px;
        }}
        .system-card-container {{
            background: rgba(13, 17, 23, 0.8);
            border: 1px solid rgba(0, 191, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
        }}
        </style>
        """)
    ),
    
    # حقن الـ Header العلوي الثابت لنظامك
    ui.HTML("""
    <div class="main-header-container">
        <div class="main-logo">ZEGAAR AMMAR<br>GLASS MANAGER</div>
        <div class="main-subtitle">النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>
    </div>
    """),
    
    # صندوق الإدخال التفاعلي مع دعم الستارة العائمة
    ui.row(
        ui.column(12,
            ui.div(
                ui.input_text("free_smart_search_input_field", "", placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة...", width="100%"),
                ui.output_ui("floating_suggestions_ui"),
                class_="p-2"
            )
        )
    ),
    
    # منطقة المخرجات المركزية لتشغيل تدفق الفحص والمطابقة الهندسي
    ui.row(
        ui.column(12,
            ui.div(
                ui.output_ui("workflow_results_ui"),
                class_="system-card-container"
            )
        )
    ),
    
    # دمج مركزي للوحة التحكم بأسفل التطبيق
    ui.row(
        ui.column(12,
            ui.output_ui("control_panel_ui"),
            style="margin-top: 30px; margin-bottom: 20px;"
        )
    )
)

# 3. محرك التشغيل ومعالجة الذكاء الفوري (Server)
def server(input, output, session):
    
    # حقن أنماط الـ PWA عند بدء التشغيل
    inject_pwa_and_styles()
    
    # متغير تفاعلي للتحكم في قيمة حقل البحث لتمكين الأزرار من تعبئته فوراً باللمس
    search_value = reactive.Value("")
    
    # مراقبة وتحديث قيمة صندوق البحث المباشر
    @reactive.effect
    @reactive.event(input.free_smart_search_input_field)
    def _():
        search_value.set(input.free_smart_search_input_field().strip())

    # محرك جلب الاقتراحات اللحظية الفلاشية من ملف الأسماء
    @reactive.calc
    def get_suggestions():
        phone = search_value()
        if not phone:
            return []
        term = phone.lower().strip()
        starts_with = [m for m in unique_models if m.lower().startswith(term)]
        contains = [m for m in unique_models if term in m.lower() and m not in starts_with]
        return (starts_with + contains)[:10]

    # بناء وتحديث الستارة التفاعلية الحية بالاقتراحات المساعدة
    @render.ui
    def floating_suggestions_ui():
        phone = search_value()
        sugs = get_suggestions()
        
        if phone and sugs:
            is_fully_matched = any(phone.lower() == s.lower() for s in sugs)
            if not is_fully_matched:
                # إنشاء الأزرار بشكل تفاعلي يحقن القيمة مباشرة باللمس وبلمح البصر
                buttons_html = []
                for idx, item in enumerate(sugs):
                    buttons_html.append(
                        ui.input_action_button(
                            f"sug_btn_{idx}", 
                            f"🔍 {item}", 
                            class_="suggestion-link-btn"
                        )
                    )
                
                return ui.div(
                    ui.HTML("<div class='floating-suggestions-box-title'><span style='color:#00bfff; font-weight:bold; font-size:16px;'>💡 اقتراحات البحث المساعدة لتسريع الكتابة:</span></div>"),
                    ui.div(*buttons_html, class_="floating-suggestions-box-end")
                )
        return ui.div()

    # الاستماع لضغطات أزرار الستارة لتعبئة الحقل برمشة عين (تأثير اللمس السريع المستقر)
    def make_suggestion_linker(idx):
        @reactive.effect
        @reactive.event(getattr(input, f"sug_btn_{idx}", None))
        def _():
            sugs = get_suggestions()
            if idx < len(sugs):
                target_item = sugs[idx]
                search_value.set(target_item)
                ui.update_text("free_smart_search_input_field", value=target_item)

    # تفعيل المستمعين لكل الأزرار العشرة المحتملة في الستارة
    for idx in range(10):
        make_suggestion_linker(idx)

    # تشغيل والتحام ملف العمليات المركزي وتمرير البيانات له بسلاسة فائقة
    @render.ui
    def workflow_results_ui():
        phone = search_value()
        sugs = get_suggestions()
        
        # استدعاء دالة نظامك الأساسية وتمرير البيانات لها
        # نظام Shiny يعزل التشغيل ليعمل بكفاءة مطلقة في الخلفية
        with reactive.isolate():
            try:
                run_system_workflows(
                    phone=phone,
                    db_data=db_data,
                    suggestions=sugs
                )
            except Exception as e:
                pass
                
        if not phone:
            return ui.HTML("<p style='color: #aaa; text-align: center; font-size: 16px;'>برجاء كتابة اسم الهاتف لبدء فحص ومطابقة زجاج الحماية...</p>")
            
        return ui.HTML(f"<div style='color: #00ffcc; font-weight: bold; font-size: 16px;'>🔍 تم استدعاء فحص وتدقيق الموديل الحركي: {phone}</div>")

    # تشغيل ورسم لوحة التحكم المركزية بأسفل الشاشة
    @render.ui
    def control_panel_ui():
        with reactive.isolate():
            try:
                # استدعاء لوحة التحكم الخاصة بمكونات واجهتك
                draw_control_panel(
                    notifications=[],
                    total_models=total_models,
                    empty_groups_count=empty_groups_count
                )
            except Exception as e:
                pass
        return ui.div()

app = App(app_ui, server)

