import os
import base64
import pandas as pd
from shiny import App, ui, render, reactive

# 1. تحويل صورة الخلفية المرفقة لترميز ويب آمن
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# 2. تصميم واجهة المستخدم (UI) بنمط النيون والبطاقات الزجاجية
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
    ui.row(
        ui.column(12,
            ui.output_ui("matched_results_ui"),
            class_="p-1"
        )
    ),
    ui.HTML('<button class="settings-floating-btn">⚙️</button>')
)

# 3. منطق السيرفر (Server Logic) لإدارة التفاعلات
def server(input, output, session):
    
    # استيراد محلي آمن للدوال لمنع الـ Circular Import أثناء إقلاع السيرفر
    from database import load_db
    from workflows import run_system_workflows, append_to_models_index
    
    # تحميل قاعدة البيانات
    db_data = load_db()

    # حساب الاقتراحات بناءً على المدخلات الحالية ونص البحث المستهدف
    @reactive.calc
    def filtered_suggestions():
        query = input.free_smart_search_input_field().strip()
        if not query or len(query) < 2:
            return []
        
        # قراءة كشاف الأسماء للتصفية الذكية السريعة للاقتراحات المقربة
        INDEX_FILE = "models_index.txt"
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                models = [line.strip() for line in f if line.strip()]
            return [m for m in models if query.lower() in m.lower()][:5]
        return []

    # رندرة قائمة الاقتراحات الطافية أثناء الكتابة
    @render.ui
    def floating_suggestions_ui():
        suggestions = filtered_suggestions()
        query = input.free_smart_search_input_field().strip()
        
        # إخفاء القائمة في حال اختيار الاسم المطابق تماماً
        if not suggestions or query in suggestions:
            return ui.div()
        
        buttons = []
        buttons.append(ui.div("💡 الموديلات المقترحة القريبة:", class_="floating-suggestions-box-title"))
        
        for item in suggestions:
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

    # رندرة النتائج النهائية الممررة من المحرك المركزي وخططه الثلاث
    @render.ui
    def matched_results_ui():
        query = input.free_smart_search_input_field().strip()
        if not query or len(query) < 2:
            return ui.div()
            
        suggestions = filtered_suggestions()
        
        # تشغيل محرك workflows المركزي لجلب الواجهات والمطابقات
        html_res = run_system_workflows(query, db_data, suggestions)
        
        # ضخ الهاتف المكتوب في الكشاف تلقائياً إذا تم استخدامه بنجاح
        if query:
            append_to_models_index(query)

        return ui.div(ui.HTML(html_res))

# 🚀 بناء التطبيق وتشغيله
app = App(app_ui, server)
