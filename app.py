import os
from shiny import App, ui, render, reactive
from supabase import create_client

# إعداد الاتصال
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style(open("style.css", "r").read())
    ),
    
    # الدرج الجانبي (الإعدادات)
    ui.div(
        ui.h3("⚙️ الإعدادات", style="color:#00bfff;"),
        ui.div("🔔 جرس الإشعارات: نشط", class_="metric-box"),
        ui.div("🛡️ المراقب الصامت: يعمل", class_="metric-box"),
        ui.input_action_button("close_drawer", "إغلاق الدرج", class_="btn-neon"),
        id="settings_drawer", class_="drawer"
    ),
    
    # العنوان العلوي
    ui.div(
        ui.h2("GLASS MANAGER", style="color:#fff; margin:0;"),
        ui.input_action_button("btn_settings", "⚙️", style="background:transparent; border:none; color:#00bfff; font-size:24px;"),
        class_="header-bar"
    ),
    
    # صندوق البحث
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

    # منطق الدرج
    @reactive.effect
    @reactive.event(input.btn_settings)
    def _(): ui.update_tags("settings_drawer", class_="drawer open")
    @reactive.effect
    @reactive.event(input.close_drawer)
    def _(): ui.update_tags("settings_drawer", class_="drawer")

    # الاقتراحات (Autocomplete)
    @render.ui
    def suggestions_curtain():
        q = input.search_query().lower()
        if not q: return None
        matches = [d['model_name'] for d in fetch_data() if q in d['model_name'].lower()][:6]
        return ui.div(*[ui.div(m, class_="suggestion-row", onclick=f"Shiny.setInputValue('selected_model', '{m}');") for m in matches], class_="suggestions-curtain")

    @reactive.effect
    @reactive.event(input.selected_model)
    def _(): ui.update_text("search_query", value=input.selected_model())

    # عرض النتائج مع الفواصل والدوائر النيون
    @render.ui
    def results_area():
        q = input.search_query().strip().lower()
        if not q: return None
        data = fetch_data()
        target = next((d for d in data if d['model_name'].lower() == q), None)
        if not target: return None
        
        target_size = float(target['size'])
        
        # فرز البيانات
        exact, plus, minus = [], [], []
        for d in data:
            if d['sensor'] != target['sensor']: continue
            diff = round(float(d['size']) - target_size, 3)
            if diff == 0: exact.append(d)
            elif 0 < diff <= 0.03: plus.append(d)
            elif -0.03 <= diff < 0: minus.append(d)

        # دالة إنشاء الفاصل بالدائرة النيون
        def create_neon_header(label, color):
            return ui.div(
                ui.div(style=f"width:12px; height:12px; border-radius:50%; background:{color}; box-shadow:0 0 15px {color}; margin-left:10px;"),
                ui.span(label, style="color:white; font-weight:bold; font-size:16px;"),
                style="display:flex; align-items:center; margin:25px auto 10px auto; max-width:500px;"
            )

        # بناء الواجهة
        res = [ui.div(ui.h4(target['model_name'], style="color:#00bfff; margin:0;"), ui.p(f"📏 القياس: {target['size']} | 👁️ المستشعر: {target.get('sensor', '-')}"), class_="glass-card")]
        
        if exact:
            res.append(create_neon_header("هواتف مطابقة تماماً", "#2ecc71"))
            for d in exact: res.append(ui.div(ui.div("📱", class_="image-placeholder-box"), ui.div(d['model_name'], class_="flat-phone-text"), class_="glass-card flat-exact ammar-flat-card"))
        if plus:
            res.append(create_neon_header("هواتف أكبر قليلاً", "#3498db"))
            for d in plus: res.append(ui.div(ui.div("📱", class_="image-placeholder-box"), ui.div(d['model_name'], class_="flat-phone-text"), class_="glass-card flat-plus ammar-flat-card"))
        if minus:
            res.append(create_neon_header("هواتف أصغر قليلاً", "#e67e22"))
            for d in minus: res.append(ui.div(ui.div("📱", class_="image-placeholder-box"), ui.div(d['model_name'], class_="flat-phone-text"), class_="glass-card flat-minus ammar-flat-card"))
            
        return ui.div(*res)

app = App(app_ui, server)
def server(input, output, session):


    @reactive.calc
    def cloud_data():

        try:

            result = (
                supabase
                .table("phones")
                .select("*")
                .execute()
            )

            return result.data or []


        except Exception as e:

            print(e)

            return []




    @reactive.calc
    def local_db():

        return convert_database(
            cloud_data()
        )




    # ==============================
    # فتح وغلق الإعدادات
    # ==============================


    @reactive.effect
    @reactive.event(input.btn_settings)
    def open_settings():

        ui.update_element(
            "settings_drawer",
            class_="drawer open"
        )



    @reactive.effect
    @reactive.event(input.close_drawer)
    def close_settings():

        ui.update_element(
            "settings_drawer",
            class_="drawer"
        )




    # ==============================
    # الاقتراحات
    # ==============================


    @render.ui
    def suggestions_curtain():


        q = input.search_query().strip().lower()


        if not q:

            return None



        matches = []


        for row in cloud_data():

            name = str(
                row.get(
                    "model_name",
                    ""
                )
            )


            if q in name.lower():

                matches.append(name)



        matches = list(dict.fromkeys(matches))[:8]



        if not matches:

            return None



        return ui.div(

            *[

                ui.div(
                    name,
                    class_="suggestion-row",
                    onclick=f"""
                    Shiny.setInputValue(
                    'selected_model',
                    '{name}'
                    )
                    """
                )

                for name in matches

            ],

            class_="suggestions-curtain"

        )





    @reactive.effect
    @reactive.event(input.selected_model)
    def select_model():


        ui.update_text(
            "search_query",
            value=input.selected_model()
        )





    # ==============================
    # النتائج
    # ==============================


    @render.ui
    def results_area():


        phone = (
            input.search_query()
            .strip()
        )


        if not phone:

            return None



        html = run_system_workflows(

            phone,

            local_db(),

            None

        )



        if not html:

            return None



        return ui.HTML(html)





app = App(
    app_ui,
    server
        )
