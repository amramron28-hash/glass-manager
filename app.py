import os
from shiny import App, ui, render, reactive
from supabase import create_client

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.link(rel="manifest", href="manifest.json"),
        ui.tags.style(open("style.css", "r").read())
    ),
    
    # الدرج الجانبي (المصحح)
    ui.div(
        ui.h3("⚙️ إعدادات النظام", style="color:#00bfff; padding:10px;"),
        ui.div(f"🛡️ الحالة: نشط", class_="metric-box"),
        ui.input_action_button("close_drawer", "إغلاق الدرج", class_="btn-neon"),
        id="settings_drawer", class_="drawer"
    ),
    
    # الهيدر (المربوط بفتح الدرج)
    ui.div(
        ui.h2("GLASS MANAGER", style="color:#00bfff; margin:0;"),
        ui.input_action_button("btn_settings", "⚙️"),
        class_="header-bar"
    ),
    
    # مربع البحث
    ui.div(
        ui.input_text("search_query", "", placeholder="🔍 ابحث عن الموديل..."),
        ui.output_ui("suggestions_curtain"),
        class_="search-box"
    ),
    
    ui.output_ui("results_area")
)

def server(input, output, session):
    @reactive.calc
    def fetch_data(): return supabase.table("phones").select("*").execute().data

    # إصلاح عمل نافذة الإعدادات (الدرج)
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _(): ui.update_tags("settings_drawer", class_="drawer open")

    @reactive.effect
    @reactive.event(input.close_drawer)
    def _(): ui.update_tags("settings_drawer", class_="drawer")

    # إصلاح اختفاء الستارة بعد الاختيار
    @render.ui
    def suggestions_curtain():
        q = input.search_query().lower()
        if not q: return None
        matches = [d['model_name'] for d in fetch_data() if q in d['model_name'].lower()][:6]
        # إضافة إخفاء الستارة عند النقر على الموديل
        return ui.div(*[ui.div(m, class_="suggestion-row", onclick=f"Shiny.setInputValue('selected_model', '{m}');") for m in matches], class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model)
    def _(): 
        ui.update_text("search_query", value=input.selected_model())
        # إخفاء الستارة يتم عبر إفراغ البحث في الـ render التالي

    @render.ui
    def results_area():
        q = input.search_query().strip().lower()
        if not q: return None
        data = fetch_data()
        target = next((d for d in data if d['model_name'].lower() == q), None)
        if not target: return None # لا نظهر أي شيء إذا لم يوجد تطابق
        
        target_size = float(target['size'])
        
        # البطاقة التعريفية الرئيسية (تظهر دائماً عند البحث الصحيح)
        header_card = ui.div(
            ui.h3(target['model_name'], style="color:#00bfff; margin:0;"),
            ui.div(f"📏 القياس: {target['size']} | 🖼️ الشاشة: {target.get('panel', 'غير محدد')}", style="color:#fff;"),
            class_="glass-card"
        )
        
        res = [header_card]
        
        # تصنيف وتصفية النتائج
        for d in data:
            if d['sensor'] != target['sensor']: continue # تجاوز النتائج غير المتوافقة
            
            diff = round(float(d['size']) - target_size, 3)
            card_class = "flat-exact" if diff == 0 else ("flat-plus" if 0 < diff <= 0.03 else "flat-minus")
            
            # منع البطاقات الفارغة
            if d['model_name']:
                res.append(ui.div(
                    ui.div("📱", class_="image-placeholder-box"),
                    ui.div(d['model_name'], class_="flat-phone-text"),
                    class_=f"glass-card {card_class} ammar-flat-card"
                ))
        return ui.div(*res)

app = App(app_ui, server)
