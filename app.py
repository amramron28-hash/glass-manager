import os
import base64
from shiny import App, ui, render, reactive
from database import load_db, save_db
from workflows import run_system_workflows
from ui_components import inject_pwa_and_styles

# ==============================================================================
# 1. تهيئة الموارد والصور
# ==============================================================================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return f"data:image/webp;base64,{base64.b64encode(f.read()).decode()}"
    return ""

bg_img = get_base64_image("phone_image.webp")

# ==============================================================================
# 2. الواجهة الرسومية (UI) - بتصميم زجاجي شفاف
# ==============================================================================
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML(inject_pwa_and_styles()),
        ui.HTML(f"""
        <style>
            body {{ 
                background: url('{bg_img}') no-repeat center center fixed; 
                background-size: cover; color: white; margin: 0; font-family: 'Segoe UI', sans-serif;
            }}
            /* النافذة الجانبية الزجاجية */
            .drawer {{ 
                position: fixed; top: 0; left: -300px; width: 280px; height: 100%; 
                background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px);
                border-right: 1px solid rgba(255, 255, 255, 0.2); transition: 0.5s; z-index: 9999; padding: 25px; 
            }}
            .drawer.open {{ left: 0; }}
            
            /* شريط العنوان */
            .header-bar {{ 
                display: flex; justify-content: space-between; padding: 20px; align-items: center; 
                background: rgba(0, 0, 0, 0.2); backdrop-filter: blur(5px);
            }}
            .icon-btn {{ cursor: pointer; font-size: 24px; color: #00bfff; }}
            
            /* تصميم البطاقات الزجاجية الملونة */
            .result-card {{
                margin: 15px auto; padding: 20px; border-radius: 20px; width: 90%; max-width: 550px;
                backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); transition: 0.3s;
                position: relative; overflow: hidden;
            }}
            /* ألوان المجموعات الزجاجية */
            .card-green {{ background: rgba(46, 204, 113, 0.25); border-left: 5px solid #2ecc71; }}
            .card-blue {{ background: rgba(52, 152, 219, 0.25); border-left: 5px solid #3498db; }}
            .card-orange {{ background: rgba(230, 126, 34, 0.25); border-left: 5px solid #e67e22; }}
            
            /* مؤشر النسبة والدقة */
            .status-tag {{
                position: absolute; top: 10px; right: 15px; font-size: 0.85rem;
                font-weight: bold; padding: 4px 10px; border-radius: 10px; background: rgba(0,0,0,0.3);
            }}
            
            .neon-text {{ color: #00bfff; text-shadow: 0 0 10px #00bfff; }}
            .search-container {{ position: relative; max-width: 600px; margin: auto; padding: 20px; }}
            input[type="text"] {{ 
                background: rgba(255,255,255,0.1) !important; border: 1px solid #00bfff !important; 
                color: white !important; border-radius: 10px !important;
            }}
        </style>
        """)
    ),
    
    # الدرج المنزلق
    ui.HTML("""
    <div id="drawer" class="drawer">
        <h3 class="neon-text">الاعدادات</h3>
        <p>⚙️ ضبط النظام</p>
        <p>🔔 الاشعارات</p>
        <p>🔇 المراقب الصامت</p>
        <hr style="border:0.5px solid rgba(255,255,255,0.2);">
        <p>📊 إجمالي الموديلات: 364</p>
        <button onclick="document.getElementById('drawer').classList.remove('open')" 
                style="width:100%; background:#00bfff; border:none; padding:10px; border-radius:5px; font-weight:bold;">اغلاق</button>
    </div>
    """),

    # الشريط العلوي
    ui.div(
        ui.HTML('<div class="icon-btn" onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')">☰</div>'),
        ui.h2("ZEGAAR AMMAR", class_="neon-text", style="margin:0;"),
        ui.HTML('<div class="icon-btn">🔔</div>'),
        class_="header-bar"
    ),

    # منطقة البحث
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.output_ui("autocomplete_ui"),
        ui.output_ui("main_content_ui"),
        class_="search-container"
    )
)

# ==============================================================================
# 3. السيرفر (Server Logic)
# ==============================================================================
def server(input, output, session):
    db = reactive.value(load_db())
    current_step = reactive.value(0)
    
    @render.ui
    def autocomplete_ui():
        all_models = []
        for s in db.get().values():
            for p in s.values():
                for sen in p.values():
                    all_models.extend(sen.get("models", []))
        options = "".join([f"<option value='{m}'>" for m in set(all_models)])
        return ui.HTML(f"<datalist id='models_list'>{options}</datalist>"
                       "<script>document.getElementById('search_query').setAttribute('list', 'models_list');</script>")

    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query: 
            current_step.set(0)
            return ui.div()
        
        # استدعاء نتائج البحث الأصلية
        results = run_system_workflows(query, db.get(), [])
        
        if results:
            # هنا نقوم بتغليف النتائج بتنسيق "الزجاج الشفاف" مع المؤشرات المطلوبة
            # ملاحظة: في النسخة الواقعية، سيتم تمرير الـ HTML من workflows، 
            # لكننا هنا سنطبق القالب الجمالي الذي طلبته:
            
            output_cards = []
            # مثال لتوليد البطاقات بالألوان المطلوبة والمؤشرات (تمام/ناقص/زايد)
            states = [
                {"cls": "card-green", "label": "تمـام", "val": "100%"},
                {"cls": "card-blue", "label": "ناقـص", "val": "-0.03"},
                {"cls": "card-orange", "label": "زايـد", "val": "+0.03"}
            ]
            
            # سيتم تكرار البطاقات بناءً على بيانات الموديل الحقيقية
            for state in states:
                card = ui.HTML(f"""
                <div class="result-card {state['cls']}">
                    <div class="status-tag">{state['label']} (±0.03)</div>
                    <h3 style="margin-top:0;">نتائج القياس: {state['val']}</h3>
                    <p style="margin-bottom:0; font-size:0.9rem; opacity:0.8;">بيانات الموديل: {query}</p>
                </div>
                """)
                output_cards.append(card)
            
            return ui.div(*output_cards)
        
        else:
            # تدفق خطة الطوارئ اليدوية
            if current_step() == 0: current_step.set(1)
            
            if current_step() == 1:
                return ui.div(ui.h4("📏 الخطوة 1: أدخل المقاس", class_="neon-text"),
                              ui.input_text("val_size", "المقاس:"),
                              ui.input_action_button("next1", "التالي", style="width:100%; background:#00bfff;"), 
                              class_="result-card card-blue")
            # ... تكملة الخطوات 2 و 3 ...

    @reactive.effect
    @reactive.event(input.next1)
    def _(): current_step.set(2)

app = App(app_ui, server)
