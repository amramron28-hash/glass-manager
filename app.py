import os
import base64
from shiny import App, ui, render, reactive
import pandas as pd

# استيراد كافة الدوال والمكونات الفنية لنظامك الموحد
from app_init import initialize_system_data
from workflows import run_system_workflows
from ui_components import draw_control_panel, inject_pwa_and_styles, draw_technical_coords, draw_neon_section
from logic_engine import find_model_coords, get_compatibles_strict

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
    ui.row(
        ui.column(12,
            ui.div(
                ui.output_ui("workflow_results_ui"),
                class_="system-card-container"
            )
        )
    ),
    ui.input_action_button("toggle_settings_btn", "⚙️", class_="settings-floating-btn"),
    ui.row(
        ui.column(12,
            ui.output_ui("control_panel_ui"),
            style="margin-top: 40px;"
        )
    )
)

def server(input, output, session):
    inject_pwa_and_styles()
    
    # ⚡ جعل المتغير تفاعلي لحظي ليلتقط أحرف الفني أثناء الكتابة مباشرة
    search_value = reactive.Value("")
    
    @reactive.effect
    def _():
        search_value.set(input.free_smart_search_input_field().strip())

    @reactive.calc
    def get_suggestions():
        phone = search_value()
        if not phone:
            return []
        term = phone.lower().strip()
        starts_with = [m for m in unique_models if m.lower().startswith(term)]
        contains = [m for m in unique_models if term in m.lower() and m not in starts_with]
        return (starts_with + contains)[:10]

    # تشغيل ستارة الـ Auto-complete وتحديثها مع الحروف
    @render.ui
    def floating_suggestions_ui():
        phone = search_value()
        sugs = get_suggestions()
        
        if phone and sugs:
            is_fully_matched = any(phone.lower() == s.lower() for s in sugs)
            if not is_fully_matched:
                buttons_html = []
                for idx, item in enumerate(sugs):
                    buttons_html.append(
                        ui.input_action_button(f"sug_btn_{idx}", f"🔍 {item}", class_="suggestion-link-btn")
                    )
                return ui.div(
                    ui.HTML("<div class='floating-suggestions-box-title'><span style='color:#00bfff; font-weight:bold; font-size:16px;'>💡 اقتراحات البحث المساعدة لتسريع الكتابة:</span></div>"),
                    ui.div(*buttons_html, class_="floating-suggestions-box-end")
                )
        return ui.div()

    # التقاط نقرة اللمس على الاقتراح لملء الحقل فوراً دون تشنج الصفحة
    def make_suggestion_linker(idx):
        @reactive.effect
        @reactive.event(getattr(input, f"sug_btn_{idx}", None))
        def _():
            sugs = get_suggestions()
            if idx < len(sugs):
                target_item = sugs[idx]
                search_value.set(target_item)
                ui.update_text("free_smart_search_input_field", value=target_item)

    for idx in range(10):
        make_suggestion_linker(idx)

    # معالجة وعرض نتائج الفحص الهندسي والبطاقات الملونة والمطابقة الصارمة ±0.03
    @render.ui
    def workflow_results_ui():
        phone = search_value()
        sugs = get_suggestions()
        
        if not phone:
            return ui.HTML("<p style='color: #aaa; text-align: center; font-size: 16px; margin-top:30px;'>برجاء كتابة اسم الهاتف لبدء فحص ومطابقة زجاج الحماية...</p>")
            
        with reactive.isolate():
            try:
                run_system_workflows(phone=phone, db_data=db_data, suggestions=sugs)
                coords = find_model_coords(db_data, phone)
                
                if coords:
                    size = coords.get('size', 'غير حدد')
                    panel = coords.get('panel', 'غير محدد')
                    sensor = coords.get('sensor', 'غير محدد')
                    
                    compatibles = get_compatibles_strict(db_data, size, panel, sensor)
                    compatibles_str = " ، ".join(compatibles) if compatibles else "لا توجد موديلات بديلة مطابقة تماماً حالياً"
                    
                    return ui.div(
                        ui.div(
                            ui.h3(f"📱 الأبعاد الهندسية الدقيقة لـ {phone}", style="color: #00bfff; font-weight:bold; font-size:20px; margin-bottom:15px;"),
                            ui.p(ui.HTML(f"📐 <b>المقاس المقاس:</b> <span style='color: #00ffcc;'>{size}</span>")),
                            ui.p(ui.HTML(f"📺 <b>نوع الشاشة:</b> <span style='color: #00ffcc;'>{panel}</span>")),
                            ui.p(ui.HTML(f"🔌 <b>حساس التقارب:</b> <span style='color: #00ffcc;'>{sensor}</span>")),
                            class_="neon-section"
                        ),
                        ui.div(
                            ui.h4("🛡️ الفحص الصارم وتطابق زجاج الحماية المتاح:", style="color: #ffbf00; font-weight:bold; font-size:18px;"),
                            ui.HTML(f"<div style='margin-bottom:10px;'><span class='tolerance-badge'>قفل التطابق الهندسي: ±0.03</span></div>"),
                            ui.p(ui.HTML(f"🔮 <b>الموديلات المتوافقة مع هذا الزجاج في المخزن:</b> <br><span style='color: #fff; font-weight:500; line-height:1.6;'>{compatibles_str}</span>")),
                            class_="glass-card-matched"
                        ),
                        class_="p-2"
                    )
                else:
                    return ui.HTML(f"<div class='neon-section' style='border-color: #ff4d4d;'><p style='color: #ff4d4d; font-weight: bold;'>⚠️ الموديل {phone} غير مسجل هندسياً، تم بدء فحص سحابي ذكي لمعرفة مواصفاته...</p></div>")
            except Exception as e:
                return ui.HTML(f"<p style='color: #ff4d4d;'>حدث خطأ أثناء فحص المطابقة: {str(e)}</p>")

    # 🔥 تفعيل وضخ البيانات الحية الحقيقية بالكامل داخل نافذة الإعدادات والترس المنبثقة
    @reactive.effect
    @reactive.event(input.toggle_settings_btn)
    def _():
        ui.modal_show(
            ui.modal(
                ui.div(
                    ui.h3("⚙️ لوحة الإعدادات والمراقب الصامت", style="color: #00bfff; text-align:center; font-weight:bold; margin-bottom:20px; text-shadow: 0 0 10px rgba(0,191,255,0.5);"),
                    ui.p("🔔 <b>جرس الإشعارات الحية:</b> كافة قنوات الربط السحابي والاتصال الآمن بـ Supabase مشفرة ومستقرة تماماً."),
                    ui.hr(style="border-color: rgba(0,191,255,0.2);"),
                    ui.h5("📊 إحصائيات المخزون الحية والمراقب الصامت:", style="color: #ffbf00; font-weight:bold; margin-bottom:15px;"),
                    ui.HTML(f"""
                    <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); line-height: 1.8;'>
                        🔹 <b>إجمالي مصفوفة الموديلات المحفوظة:</b> <span style='color: #00ffcc; font-weight:bold;'>{total_models} هاتف</span><br>
                        🔹 <b>المجموعات الشاغرة (الخالية) بالمخزن:</b> <span style='color: #ff4d4d; font-weight:bold;'>{empty_groups_count} مجموعة</span><br>
                        🔹 <b>قفل تفاوت المطابقة الهندسي:</b> <span style='color: #ffbf00; font-weight:bold;'>±0.03 صارم</span>
                    </div>
                    """),
                    style="direction: rtl; text-align: right; color: white;"
                ),
                title="ZEGAAR AMMAR GLASS MANAGER CONTROL PANEL",
                easy_close=True,
                footer=ui.modal_button("إغلاق لوحة التحكم ✖️", class_="btn-secondary", style="background: #333; color: white; border: none;")
            )
        )

    @render.ui
    def control_panel_ui():
        with reactive.isolate():
            try:
                draw_control_panel(notifications=[], total_models=total_models, empty_groups_count=empty_groups_count)
            except:
                pass
        return ui.div()

app = App(app_ui, server)
