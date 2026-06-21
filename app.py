import os
import base64
from html import escape
from shiny import App, ui, render, reactive
from database import load_db, save_db
from workflows import run_system_workflows, find_model_coords
from ui_components import inject_pwa_and_styles

# ==============================================================================
# 1. تهيئة الموارد والصور
# ==============================================================================
def get_base64_image(image_path):
    """دالة تحويل صورة الخلفية إلى Base64 لضمان ظهورها دائماً"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded}"
    return ""

bg_img_base64 = get_base64_image("phone_image.webp")

# ==============================================================================
# 2. الواجهة الرسومية (UI) - هيكل كامل
# ==============================================================================
app_ui = ui.page_fluid(
    ui.head_content(
        ui.HTML(inject_pwa_and_styles()),
        ui.HTML(f"""
        <style>
            body {{ background: url('{bg_img_base64}') no-repeat center center fixed; background-size: cover; color: white; margin: 0; font-family: Arial; }}
            .drawer {{ position: fixed; top: 0; left: -300px; width: 280px; height: 100%; background: rgba(13,17,23,0.98); border-right: 2px solid #00bfff; transition: 0.5s; z-index: 9999; padding: 25px; box-shadow: 2px 0 10px rgba(0,0,0,0.5); }}
            .drawer.open {{ left: 0; }}
            .header-bar {{ display: flex; justify-content: space-between; padding: 15px; align-items: center; }}
            .icon-btn {{ cursor: pointer; font-size: 24px; color: #00bfff; transition: 0.3s; }}
            .step-container {{ background: rgba(13,17,23,0.9); border: 1px solid #00bfff; padding: 25px; border-radius: 15px; margin: 20px auto; width: 90%; max-width: 500px; box-shadow: 0 0 15px rgba(0,191,255,0.2); }}
            .neon-text {{ color: #00bfff; text-shadow: 0 0 5px #00bfff; }}
        </style>
        """)
    ),
    
    # النافذة المنسدلة (الدرج)
    ui.HTML("""
    <div id="drawer" class="drawer">
        <h3 class="neon-text">إعدادات النظام</h3>
        <p>⚙️ ضبط الإعدادات</p>
        <p>🔔 جرس الإشعارات</p>
        <p>🔇 المراقب الصامت</p>
        <hr style="border:0.5px solid #00bfff;">
        <p>📊 إجمالي الموديلات: <span id="model_count">364</span></p>
        <button onclick="document.getElementById('drawer').classList.remove('open')" style="width:100%;">إغلاق</button>
    </div>
    """),

    # شريط العنوان العلوي
    ui.div(
        ui.HTML('<div class="icon-btn" onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')">☰</div>'),
        ui.h2("ZEGAAR AMMAR", class_="neon-text", style="margin:0;"),
        ui.HTML('<div class="icon-btn">🔔</div>'),
        class_="header-bar"
    ),

    # منطقة البحث الرئيسية
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.output_ui("main_content_ui"),
        style="max-width: 600px; margin: auto; padding: 20px;"
    )
)

# ==============================================================================
# 3. منطق السيرفر (Server Logic)
# ==============================================================================
def server(input, output, session):
    # حالة قاعدة البيانات
    db = reactive.value(load_db())
    
    # تحميل منطق البحث وتدفق النتائج
    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query: return ui.div()
        
        # تنفيذ سير العمل (Workflows)
        try:
            results = run_system_workflows(query, db.get(), [])
            
            # إذا فشل البحث: عرض خطة الطوارئ بالتسلسل
            if not results:
                return ui.div(
                    ui.h4("لم يتم العثور على الموديل، المتابعة يدوياً:", class_="neon-text"),
                    ui.input_text("manual_size", "أدخل المقاس (اختياري)..."),
                    ui.input_select("panel_type", "نوع الشاشة:", ["Notch Screen", "Punch Hole", "Curved Screen"]),
                    ui.input_action_button("save_btn", "حفظ وتنشيط الموديل", style="width:100%; background:#00bfff;"),
                    class_="step-container"
                )
            return ui.HTML(results)
        except Exception as e:
            return ui.div(f"خطأ في معالجة البيانات: {str(e)}", style="color:red;")

    # منطق الحفظ عند إضافة موديل جديد
    @reactive.effect
    @reactive.event(input.save_btn)
    def _():
        if input.search_query():
            success = save_db(db.get(), input.search_query(), input.manual_size(), input.panel_type(), "Hardware Sensor")
            if success:
                db.set(load_db()) # تحديث القائمة
                # إضافة تنبيه بسيط (يمكن توسيعه لاحقاً)

app = App(app_ui, server)
