import os
from shiny import App, ui, render, reactive
from supabase import create_client

# إعداد الاتصال بالسحابة
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.link(rel="manifest", href="manifest.json"),
        ui.tags.style(open("style.css", "r").read())
    ),
    
    # الدرج الجانبي للإعدادات
    ui.div(
        ui.h3("⚙️ إعدادات النظام", style="color:#00bfff;"),
        ui.div(f"📱 إجمالي الموديلات المتوفرة في القاعدة", class_="metric-box"),
        ui.input_action_button("close_drawer", "إغلاق"),
        id="settings_drawer", class_="drawer"
    ),
    
    # الهيدر العلوي
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
    
    # منطقة النتائج
    ui.output_ui("results_area")
)

def server(input, output, session):
    # جلب البيانات من Supabase
    @reactive.calc
    def fetch_data(): return supabase.table("phones").select("*").execute().data

    # منطق فتح وإغلاق الدرج الجانبي
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _(): ui.update_tags("settings_drawer", class_="drawer open")

    @reactive.effect
    @reactive.event(input.close_drawer)
    def _(): ui.update_tags("settings_drawer", class_="drawer")

    # منطق اقتراحات البحث
    @render.ui
    def suggestions_curtain():
        q = input.search_query().lower()
        if not q: return None
        matches = [d['model_name'] for d in fetch_data() if q in d['model_name'].lower()][:6]
        return ui.div(*[ui.div(m, class_="suggestion-row", onclick=f"Shiny.setInputValue('selected_model', '{m}')") for m in matches], class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model)
    def _(): ui.update_text("search_query", value=input.selected_model())

    # عرض النتائج بالهوية البصرية المطلوبة
    @render.ui
    def results_area():
        q = input.search_query().strip().lower()
        if not q: return None
        data = fetch_data()
        target = next((d for d in data if d['model_name'].lower() == q), None)
        if not target: return ui.div("الموديل غير موجود.", class_="glass-card")
        
        target_size = float(target['size'])
        
        # البطاقة التعريفية (Header Card)
        header_card = ui.div(
            ui.h3(target['model_name'], style="margin:0; color:#fff;"),
            ui.div(f"📏 القياس: {target['size']} | 🖼️ الشاشة: {target.get('panel', 'غير محدد')}", style="margin:5px 0;"),
            ui.div(f"👁️ المستشعر: {target.get('sensor', 'غير محدد')}"),
            class_="glass-card"
        )
        
        res = [header_card]
        
        for d in data:
            if d['sensor'] != target['sensor']:
                res.append(ui.div(ui.div("تحذير حساس", class_="flat-phone-text"), class_="glass-card flat-warning-card"))
                continue
            
            diff = round(float(d['size']) - target_size, 3)
            # اختيار الكلاس بناءً على النتيجة
            card_class = "flat-exact" if diff == 0 else ("flat-plus" if 0 < diff <= 0.03 else "flat-minus")
            
            res.append(ui.div(
                ui.div(ui.div("📱", style="font-size:20px;"), class_="image-placeholder-box"),
                ui.div(d['model_name'], class_="flat-phone-text"),
                class_=f"glass-card {card_class} ammar-flat-card"
            ))
        return ui.div(*res)

app = App(app_ui, server)
