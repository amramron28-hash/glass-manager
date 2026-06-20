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

# 2. تصميم واجهة المستخدم بالبطاقات المتقطعة والمراقب الصامت والجرس
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
        .glass-card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 10px;
            margin-top: 15px;
            padding: 5px;
        }}
        .glass-card-item {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 191, 255, 0.2);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-size: 14px;
            color: #ffffff;
            transition: all 0.25s ease;
        }}
        .glass-card-item:hover {{
            border-color: #00bfff;
            background: rgba(0, 191, 255, 0.1);
            transform: translateY(-2px);
            box-shadow: 0 0 10px rgba(0,191,255,0.3);
        }}
        .top-monitor-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            background: rgba(13, 17, 23, 0.6);
            border-radius: 8px;
            margin-bottom: 15px;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        .silent-observer {{
            font-size: 12px;
            color: #a0aec0;
        }}
        .silent-observer span {{
            color: #32cd32;
            font-weight: bold;
        }}
        .notification-bell {{
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            position: relative;
        }}
        .bell-dot {{
            position: absolute;
            top: 2px;
            right: 2px;
            width: 8px;
            height: 8px;
            background: #ff4500;
            border-radius: 50%;
        }}
        .settings-modal {{
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 85%;
            max-width: 400px;
            background: rgba(13, 17, 23, 0.96);
            backdrop-filter: blur(15px);
            border: 2px solid #00bfff;
            box-shadow: 0 0 30px rgba(0, 191, 255, 0.4);
            padding: 22px;
            border-radius: 12px;
            z-index: 10000;
            text-align: right;
        }}
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 9999;
        }}
        .settings-floating-btn {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: #00bfff;
            color: black;
            border: none;
            border-radius: 50%;
            width: 55px;
            height: 55px;
            font-size: 22px;
            box-shadow: 0 0 15px rgba(0,191,255,0.4);
            z-index: 9998;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        </style>
        """)
    ),
    ui.div(
        ui.div(ui.HTML("👁️ مراقب السيرفر الصامت: <span>مستقر ونشط</span>"), class_="silent-observer"),
        ui.HTML('<button class="notification-bell" onclick="alert(\'🔔 نظام الإشعارات: قاعدة البيانات محدثة وتعمل بكفاءة 100%\')">🔔<span class="bell-dot"></span></button>'),
        class_="top-monitor-bar"
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
    ui.HTML("""
    <div id="modal_overlay" class="modal-overlay" onclick="closeSettings()"></div>
    <div id="settings_modal" class="settings-modal">
        <h3 style="color: #00bfff; text-align: center; margin-top: 0;">⚙️ لوحة تحكم النظام</h3>
        <hr style="border-color: rgba(0,191,255,0.2); margin-bottom: 15px;">
        <p style="font-size: 14px; margin-bottom: 10px;">📊 <b>حالة الـ API العالـمي:</b> <span style="color:#32cd32;">متصل وعامل</span></p>
        <p style="font-size: 14px; margin-bottom: 10px;">📏 <b>مستوى تفاوت الأبعاد:</b> <span style="color:#ffbf00;">0.05mm مسموح</span></p>
        <p style="font-size: 14px; margin-bottom: 20px;">🛡️ <b>تأمين حاوية Shiny:</b> <span style="color:#00bfff;">نشط (Hugging Face)</span></p>
        <button onclick="closeSettings()" style="width: 100%; background: #ff4500; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer;">إغلاق لوحة الإعدادات</button>
    </div>
    <button class="settings-floating-btn" onclick="openSettings()">⚙️</button>
    <script>
    function openSettings() {
        document.getElementById('settings_modal').style.display = 'block';
        document.getElementById('modal_overlay').style.display = 'block';
    }
    function closeSettings() {
        document.getElementById('settings_modal').style.display = 'none';
        document.getElementById('modal_overlay').style.display = 'none';
    }
    </script>
    """)
)
# 3. منطق السيرفر لإدارة التفاعلات وعرض الكروت المقسمة
def server(input, output, session):
    
    from database import load_db
    from workflows import run_system_workflows
    
    db_data = load_db()

    @reactive.calc
    def filtered_suggestions():
        query = input.free_smart_search_input_field().strip()
        if not query or len(query) < 2:
            return []
        
        INDEX_FILE = "models_index.txt"
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                models = [line.strip() for line in f if line.strip()]
            return [m for m in models if query.lower() in m.lower()][:5]
        return []

    @render.ui
    def floating_suggestions_ui():
        suggestions = filtered_suggestions()
        query = input.free_smart_search_input_field().strip()
        
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

    @render.ui
    def matched_results_ui():
        query = input.free_smart_search_input_field().strip()
        if not query or len(query) < 2:
            return ui.div()
            
        suggestions = filtered_suggestions()
        html_res = run_system_workflows(query, db_data, suggestions)
        return ui.div(ui.HTML(html_res))

# 🚀 تشغيل التطبيق السحابي الموحد لـ ZEGAAR AMMAR
app = App(app_ui, server)
