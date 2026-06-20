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

# 2. تصميم واجهة المستخدم (UI) الموحدة بكروت النيون الخضراء واللوحة المنبثقة
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML('<link rel="manifest" href="/manifest.json">'),
        ui.HTML('<link rel="apple-touch-icon" href="/AMMAR.jpg">'),
        ui.HTML('<meta name="theme-color" content="#00bfff">'),
        ui.HTML('<meta name="apple-mobile-web-app-capable" content="yes">'),
        ui.HTML("""
        <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/service-worker.js')
            .then(reg => console.log('PWA Active'))
            .catch(err => console.log('PWA Failed', err));
        }
        </script>
        """),
        
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
        
        /* 🟢 تنسيق نيون الشاشات المتوافقة المتقطعة والمنفصلة تماماً كما بالصورة المرفقة */
        .glass-card-grid {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 15px;
            padding: 5px;
            width: 100%;
        }}
        .glass-card-item {{
            background: rgba(12, 53, 27, 0.6) !important; 
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 2px solid #32cd32 !important; 
            box-shadow: 0 0 12px rgba(50, 205, 50, 0.4);
            padding: 16px 20px;
            border-radius: 12px !important; 
            text-align: center;
            font-size: 20px !important; 
            font-weight: 800 !important;
            color: #ffffff !important; 
            transition: all 0.25s ease;
            cursor: pointer;
            width: 100%;
            letter-spacing: 0.5px;
        }}
        .glass-card-item:hover {{
            background: rgba(50, 205, 50, 0.25) !important;
            box-shadow: 0 0 20px rgba(50, 205, 50, 0.7);
            transform: scale(1.01);
        }}

        /* 🚪 لوحة الأفقية المنبثقة المخفية في أقصى اليسار */
        .side-drawer-container {{
            position: fixed;
            top: 15px;
            left: -290px;
            width: 290px;
            height: auto;
            background: rgba(13, 17, 23, 0.95);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid #00bfff;
            box-shadow: 0 0 25px rgba(0, 191, 255, 0.4);
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
            transition: left 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
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
            background: rgba(13, 17, 23, 0.95);
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
            box-shadow: 5px 0 15px rgba(0, 191, 255, 0.3);
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
        @media (max-width: 480px) {{
            .side-drawer-container {{
                width: 260px;
                left: -260px;
            }}
        }}
        </style>
        """)
    ),
    
    # 🗲 لوحة الإظهار الجانبية المنبثقة أفقياً باليسار
    ui.HTML("""
    <div id="side_drawer" class="side-drawer-container">
        <button id="drawer_toggle" class="drawer-toggle-btn" onclick="toggleDrawer()">🡪</button>
        <button class="drawer-icon-btn" onclick="alert('⚙️ الإعدادات: التفاوت المسموح للزجاج مثبت على 0.05mm لتجنب عيوب الأبعاد.')">⚙️</button>
        <div class="bell-wrapper">
            <button class="drawer-icon-btn" onclick="alert('🔔 نظام الإشعارات: خوادم PWA مستقرة ومتصلة بقاعدة البيانات التلقائية.')">🔔<span class="bell-dot-mini"></span></button>
        </div>
        <div class="drawer-observer">
            👁️ السيرفر الصامت: <span>مستقر</span>
        </div>
    </div>

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
        if (!drawer.contains(event.target) && drawer.classList.contains('drawer-open')) {
            drawer.classList.remove('drawer-open');
            btn.innerHTML = '🡪';
        }
    });
    </script>
    """),
    
    ui.HTML("""
    <div class="main-header-container">
        <div class="main-logo">ZEGAAR AMMAR<br>GLASS MANAGER</div>
        <div class="main-subtitle">النظام السطار الذكي الموحد لفحص ومطابقة حماية الشاشات</div>
    </div>
    """),
    ui.row(
        ui.column(12,
            ui.div(
                ui.input_text("free_smart_search_input_field", "", placeholder="اكتب اسم الهاتف هنا بحرية وسرعة...", width="100%"),
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
    )
)

# ==============================================================================
# 🧠 منطق السيرفر (Server Logic) لإدارة التفاعلات والمخرجات دون تعارض جوهري
# ==============================================================================
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

# 🚀 تشغيل التطبيق السحابي الموحد بكامل كفاءته البرمجية لـ GLASS MANAGER
app = App(app_ui, server)
