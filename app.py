import os
import base64
import pandas as pd
from shiny import App, ui, render, reactive
from ui_components import inject_pwa_and_styles  

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# 🎨 واجهة المستخدم الحاضنة لهندسة الستارة وكروت الطوارئ المتقطعة
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
            background: rgba(13, 17, 23, 0.7);
            border-radius: 8px;
        }}
        .main-logo {{
            font-size: 24px !important; 
            font-weight: 900 !important;
            color: #00bfff !important;
            text-shadow: 0 0 10px rgba(0, 191, 255, 0.6), 0 0 20px rgba(0, 191, 255, 0.4) !important;
            line-height: 1.4 !important;
        }}
        .main-subtitle {{
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            opacity: 0.9;
            margin-top: 8px;
        }}
        
        /* 🔍 حاوية صندوق البحث التوسيطية */
        .search-wrapper-box {{
            width: 100% !important;
            max-width: 85% !important;
            margin: 0 auto !important;
            position: relative !important; /* هام جداً لارتكاز الستارة المنسدلة */
        }}
        .shiny-input-container {{
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .shiny-input-container input {{
            background: rgba(255, 255, 255, 0.07) !important;
            color: white !important;
            border: 1px solid rgba(0, 191, 255, 0.3) !important;
            border-radius: 6px;
            padding: 12px;
            width: 100% !important;
            text-align: left !important;
            direction: ltr !important;
        }}
        
        /* 🪟 هندسة الستارة المنسدلة الأنيقة أسفل شريط البحث مباشرة (Curtain Dropdown) */
        .curtain-dropdown-menu {{
            position: absolute !important;
            top: 100% !important;
            left: 0 !important;
            width: 100% !important;
            background: rgba(10, 14, 23, 0.98) !important;
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border-left: 1px solid #00bfff !important;
            border-right: 1px solid #00bfff !important;
            border-bottom: 1px solid #00bfff !important;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            z-index: 99999 !important;
            box-shadow: 0 10px 25px rgba(0, 191, 255, 0.35) !important;
            padding: 5px 0;
            margin-top: 2px;
        }}
        .curtain-title {{
            padding: 8px 15px;
            font-size: 13px;
            color: #00bfff;
            font-weight: bold;
            border-bottom: 1px solid rgba(0, 191, 255, 0.15);
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
            background-color: rgba(0, 191, 255, 0.15);
            color: #00bfff;
            padding-left: 22px;
        }}
        
        /* فك تكثيف الحاويات لـ Shiny لضمان فرد الكروت بالكامل */
        .row, .col-12, .p-1, .p-2, .shiny-output-ui {{
            width: 100% !important;
            max-width: 100% !important;
            display: block !important;
            clear: both !important;
            float: none !important;
            padding: 0 !important;
            margin: 0 !important;
            box-sizing: border-box !important;
        }}

        /* 🚪 اللوحة الجانبية المنبثقة من اليسار */
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
                # وضع حقل البحث والستارة المخرجة داخل حاوية التوسيط الذكية المخصصة
                ui.div(
                    ui.input_text("free_smart_search_input_field", "", placeholder="Search Phone Here...", width="100%"),
                    ui.output_ui("floating_suggestions_ui"),
                    class_="search-wrapper-box"
                ),
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
# 🧠 3. منطق السيرفر السحابي (Server Logic) لبناء الستارة وتفريغ الكروت
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

    # 1. رندرة وتفعيل الستارة المنسدلة الستارية الأنيقة أسفل شريط البحث (Curtain Dropdown)
    @render.ui
    def floating_suggestions_ui():
        suggestions = filtered_suggestions()
        query = input.free_smart_search_input_field().strip()
        
        if not suggestions or query in suggestions:
            return ui.HTML("")
        
        # بناء هيكل الستارة المنسدلة الصافي من كلاس الـ CSS المعرف
        html = []
        html.append("<div class='curtain-dropdown-menu'>")
        html.append("   <div class='curtain-title'>💡 الموديلات المقترحة القريبة:</div>")
        
        for item in suggestions:
            html.append(f"""
                <button class="suggestion-link-btn" onclick="
                    document.getElementById('free_smart_search_input_field').value='{item}'; 
                    Shiny.setInputValue('free_smart_search_input_field', '{item}');
                ">{item}</button>
            """)
            
        html.append("</div>")
        return ui.HTML("\n".join(html))

    # 2. رندرة النتائج والخطط الثلاث بحقن HTML صافي مطلق لمنع الانضغاط والتكدس
    @render.ui
    def matched_results_ui():
        query = input.free_smart_search_input_field().strip()
        if not query or len(query) < 2:
            return ui.HTML("")
            
        suggestions = filtered_suggestions()
        html_res = run_system_workflows(query, db_data, suggestions)
        return ui.HTML(html_res)

# ==============================================================================
# 🚀 4. الإقلاع والتشغيل الفوري لـ GLASS MANAGER
# ==============================================================================
app = App(app_ui, server)
