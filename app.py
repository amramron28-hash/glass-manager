import os
import base64
from html import escape
from shiny import App, ui, render, reactive
from database import load_db, save_db
from workflows import run_system_workflows
from ui_components import inject_pwa_and_styles

# ==============================================================================
# 1. تهيئة الموارد والصور
# ==============================================================================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            return f"data:image/webp;base64,{base64.b64encode(image_file.read()).decode()}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# ==============================================================================
# 2. الواجهة الرسومية (UI) - كاملة ومعالجة
# ==============================================================================
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML(inject_pwa_and_styles()),
        ui.HTML(f"""
        <style>
            body {{ background: url('{bg_img_base64}') no-repeat center center fixed; background-size: cover; color: white; margin: 0; font-family: sans-serif; }}
            .drawer {{ position: fixed; top: 0; left: -300px; width: 280px; height: 100%; background: rgba(13,17,23,0.98); border-right: 2px solid #00bfff; transition: 0.5s; z-index: 9999; padding: 25px; }}
            .drawer.open {{ left: 0; }}
            .header-bar {{ display: flex; justify-content: space-between; padding: 20px; align-items: center; background: rgba(0,0,0,0.3); }}
            .icon-btn {{ cursor: pointer; font-size: 24px; color: #00bfff; }}
            .step-container {{ background: rgba(13,17,23,0.9); border: 2px solid #00bfff; padding: 25px; border-radius: 15px; margin: 20px auto; width: 90%; max-width: 500px; box-shadow: 0 0 15px rgba(0,191,255,0.3); }}
            .neon-text {{ color: #00bfff; text-shadow: 0 0 5px #00bfff; }}
            .btn-neon {{ background: #00bfff; border: none; padding: 10px; border-radius: 5px; color: black; width: 100%; margin-top: 10px; font-weight: bold; cursor: pointer; }}
        </style>
        """)
    ),
    
    # النافذة المنسدلة (الدرج)
    ui.HTML("""
    <div id="drawer" class="drawer">
        <h3 class="neon-text">الإعدادات</h3>
        <p>⚙️ إعدادات النظام</p>
        <p>🔔 جرس الإشعارات</p>
        <p>🔇 المراقب الصامت</p>
        <hr style="border:0.5px solid #00bfff;">
        <p>📊 إجمالي الموديلات: <span id="model_count">364</span></p>
        <button onclick="document.getElementById('drawer').classList.remove('open')" class="btn-neon">إغلاق</button>
    </div>
    """),

    # الشريط العلوي
    ui.div(
        ui.HTML('<div class="icon-btn" onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')">☰</div>'),
        ui.h2("ZEGAAR AMMAR", class_="neon-text", style="margin:0;"),
        ui.HTML('<div class="icon-btn">🔔</div>'),
        class_="header-bar"
    ),

    # منطقة البحث مع حقن الـ Auto-complete يدوياً لتجنب خطأ attributes
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.HTML('<datalist id="models_list"></datalist>'),
        ui.tags.script("document.getElementById('search_query').setAttribute('list', 'models_list');"),
        ui.output_ui("main_content_ui"),
        style="max-width: 600px; margin: auto; padding: 20px;"
    )
)

# ==============================================================================
# 3. منطق السيرفر (Server Logic)
# ==============================================================================
def server(input, output, session):
    db = reactive.value(load_db())
    current_step = reactive.value(0)
    
    # مراقبة نص البحث وعزل تعديل الخطوات لمنع الـ Infinite Loop
    @reactive.effect
    @reactive.event(input.search_query)
    def _():
        query = input.search_query().strip()
        if not query:
            current_step.set(0)
        else:
            results = run_system_workflows(query, db.get(), [])
            if not results and current_step() == 0:
                current_step.set(1)

    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query: 
            return ui.div()
        
        results = run_system_workflows(query, db.get(), [])
        
        # إذا وُجدت نتائج اعرضها مباشرة
        if results:
            return ui.HTML(results)
            
        # إذا لم توجد نتيجة، نبدأ نظام المعالج التفاعلي (Wizard)
        step = current_step()
        
        if step == 1:
            return ui.div(
                ui.h4("📏 الخطوة 1: أدخل المقاس", class_="neon-text"),
                ui.input_text("val_size", "المقاس:", value=input.val_size() if "val_size" in input else ""),
                ui.input_action_button("next1", "التالي", class_="btn-neon"),
                class_="step-container"
            )
        elif step == 2:
            return ui.div(
                ui.h4("📺 الخطوة 2: شكل الشاشة", class_="neon-text"),
                ui.input_select("val_panel", "الشكل:", ["Notch", "Punch", "Curved"], selected=input.val_panel() if "val_panel" in input else "Notch"),
                ui.input_action_button("next2", "التالي", class_="btn-neon"),
                class_="step-container"
            )
        elif step == 3:
            return ui.div(
                ui.h4("🔌 الخطوة 3: المستشعر", class_="neon-text"),
                ui.input_select("val_sensor", "المستشعر:", ["Hardware", "Virtual"], selected=input.val_sensor() if "val_sensor" in input else "Hardware"),
                ui.input_action_button("save_all", "إتمام وحفظ", class_="btn-neon"),
                class_="step-container"
            )
        return ui.div()

    # التنقل بين الخطوات
    @reactive.effect
    @reactive.event(input.next1)
    def _(): 
        current_step.set(2)
    
    @reactive.effect
    @reactive.event(input.next2)
    def _(): 
        current_step.set(3)

    # الحفظ النهائي الآمن والقراءة الصحيحة للمدخلات المهدومة من الـ UI
    @reactive.effect
    @reactive.event(input.save_all)
    def _():
        size = input.val_size() if "val_size" in input else ""
        panel = input.val_panel() if "val_panel" in input else "Notch"
        sensor = input.val_sensor() if "val_sensor" in input else "Hardware"
        
        # حفظ البيانات المستخرجة بنجاح
        save_db(db.get(), input.search_query(), size, panel, sensor)
        
        # إعادة التصفير وتحديث قاعدة البيانات التفاعلية
        db.set(load_db())
        current_step.set(0)

app = App(app_ui, server)
