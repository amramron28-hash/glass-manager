import os
import base64
from shiny import App, ui, render, reactive
import pandas as pd

# تحويل صورة الخلفية المرفقة في ملفاتك لترميز ويب آمن
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# 🎨 واجهة المستخدم الحاضنة للخلفية الثابتة، الـ PWA، وأنماط النيون والبطاقات الزجاجية
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
        }}
        .shiny-input-container input {{
            background: rgba(255, 255, 255, 0.07) !important;
            color: white !important;
            border: 1px solid rgba(0, 191, 255, 0.3) !important;
            border-radius: 6px;
            padding: 12px;
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
        }}
        .floating-suggestions-box-end {{
            background: rgba(13, 17, 23, 0.95) !important; 
            border-bottom: 1px solid #00bfff !important;
            border-left: 1px solid #00bfff !important;
            border-right: 1px solid #00bfff !important;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            margin-bottom: 15px;
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
            cursor: pointer;
        }}
        .suggestion-link-btn:hover {{
            background-color: rgba(0, 191, 255, 0.15);
            color: #00bfff;
            padding-right: 25px;
        }}
        .neon-section {{
            margin-top: 20px !important;
            padding: 20px !important;
            border-radius: 12px !important;
            background: rgba(13, 17, 23, 0.85);
            border: 1px solid #00bfff;
            box-shadow: 0 0 15px rgba(0, 191, 255, 0.3);
        }}
        .glass-card-matched {{
            background: rgba(0, 255, 204, 0.07);
            border: 1px solid #00ffcc;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.2);
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }}
        .tolerance-badge {{
            background: rgba(255, 191, 0, 0.15);
            color: #ffbf00;
            border: 1px solid #ffbf00;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: bold;
        }}
        .settings-floating-btn {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: #00bfff;
            color: black;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            box-shadow: 0 0 15px rgba(0,191,255,0.5);
            z-index: 9999;
        }}
        </style>
        """)
    ),
    ui.HTML("""
    <div class="main-header-container">
        <div class="main-logo">ZEGAAR AMMAR<br>GLASS MANAGER</div>
        <div class="main-subtitle">النظام السحابي الذكي الموحد لفحص ومطابقة حماية الشاشات</div>
    </div>
    """),
    ui.row(
        ui.column(12,
            ui.div(
                ui.input_text("free_smart_search_input_field", "", placeholder="اكتب اسم الهاتف المستهدف هنا بحرية وسرعة...", width="100%"),
                ui.output_ui("floating_suggestions_ui"),
                class_="p-2"
            )
        )
    ),
        # تابع لواجهة المستخدم (إغلاق الحاويات المفتوحة وإضافة حاويات العرض وزر الإعدادات)
        ui.output_ui("matched_results_ui"),
        class_="p-1"
    ),
    # زر عائم للإعدادات أسفل الشاشة كما هو معرف في الـ CSS
    ui.HTML('<button class="settings-floating-btn">⚙️</button>')
)

# 🧠 منطق الخادم (Server Logic) لإدارة البحث والاقتراحات الذكية
def server(input, output, session):
    
    # محاكاة لقاعدة بيانات الهواتف (استبدلها بقاعدتك أو بالملف المستورد)
    # ملاحظة لحل مشكلة Circular Import: تأكد أن ملف logic_engine لا يستورد من app.py
    try:
        from logic_engine import find_model_coords, get_compatibles_strict
    except ImportError:
        # دالة بديلة مؤقتة لحين إصلاح الاستيراد الدائري في ملف logic_engine.py
        def find_model_coords(search_text):
            # قاعدة بيانات تجريبية سريعة
            mock_data = ["iPhone 13", "iPhone 14 Pro", "Samsung S23", "Samsung S24 Ultra"]
            return [m for m in mock_data if search_text.lower() in m.lower()]
        
        def get_compatibles_strict(model_name):
            return {"model": model_name, "tolerance": "0.1mm", "alternatives": ["شاشة متوافقة A", "شاشة متوافقة B"]}

    # تفاعل ديناميكي عند الكتابة في حقل البحث
    @reactive.calc
    def filtered_suggestions():
        query = input.free_smart_search_input_field()
        if not query or len(query) < 2:
            return []
        # استدعاء دالة البحث من محرك المنطق
        return find_model_coords(query)

    # 1. عرض قائمة الاقتراحات العائمة أثناء الكتابة
    @render.ui
    def floating_suggestions_ui():
        suggestions = filtered_suggestions()
        if not suggestions:
            return ui.div()
        
        # بناء قائمة الخيارات المقترحة داخل التصميم المعرف مسبقاً
        buttons = []
        buttons.append(ui.div("💡 الموديلات المقترحة القريبة:", class_="floating-suggestions-box-title"))
        
        for idx, item in enumerate(suggestions):
            buttons.append(
                ui.tags.button(
                    item, 
                    class_="suggestion-link-btn", 
                    onclick=f"document.getElementById('free_smart_search_input_field').value='{item}'; "
                            f"Shiny.setInputValue('free_smart_search_input_field', '{item}');"
                )
            )
        
        buttons.append(ui.div(class_="floating-suggestions-box-end"))
        return ui.div(*buttons)

    # 2. عرض نتائج المطابقة النهائية (البطاقات الزجاجية والنيون)
    @render.ui
    def matched_results_ui():
        query = input.free_smart_search_input_field()
        suggestions = filtered_suggestions()
        
        # إذا كان النص المكتوب يطابق تماماً أحد الخيارات أو تم اختياره
        if query in suggestions or (len(suggestions) == 1 and query.lower() == suggestions[0].lower()):
            target_model = suggestions[0]
            details = get_compatibles_strict(target_model)
            
            return ui.div(
                ui.div(
                    ui.HTML(f"<h3>📱 النتيجة المتطابقة: {details['model']}</h3>"),
                    ui.p("تم العثور على القياسات الدقيقة لحماية الزجاج بنجاح."),
                    class_="glass-card-matched"
                ),
                ui.div(
                    ui.HTML("<h4>🛠️ بدائل الحماية المتوافقة:</h4>"),
                    ui.tags.ul(
                        *[ui.tags.li(alt) for alt in details.get('alternatives', [])]
                    ),
                    ui.HTML(f'<span class="tolerance-badge">نسبة التفاوت المسموح: {details.get("tolerance", "0.0mm")}</span>'),
                    class_="neon-section"
                )
            )
        return ui.div()

# 🚀 تشغيل التطبيق السحابي الموحد
app = App(app_ui, server)
