import os
from html import escape
from shiny import App, ui, render, reactive
from supabase import create_client, Client
from dotenv import load_dotenv

# ==========================================================
# 1) إعداد Supabase
# ==========================================================

load_dotenv()

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://mgmphimlcdchtbiyhhbt.supabase.co"
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "ضع_مفتاحك_هنا"
)

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ربط workflows
try:
    from workflows import run_system_workflows
except Exception:
    def run_system_workflows(model, data, db):
        return f"""
        <div class='glass-card'>
        <h3 class='neon-text'>{model}</h3>
        <p>لم يتم تحميل workflows.py</p>
        </div>
        """


# ==========================================================
# 2) الواجهة
# ==========================================================

app_ui = ui.page_fluid(

    ui.head_content(

        ui.tags.style("""

        body {
            background:#0d1117;
            color:white;
            font-family:'Segoe UI',sans-serif;
        }


        .header-bar {

            display:flex;
            justify-content:space-between;
            align-items:center;

            padding:15px 25px;

            background:rgba(13,17,23,.55);
            backdrop-filter:blur(12px);

            border-bottom:1px solid rgba(0,191,255,.25);

            position:relative;
            z-index:10000;
        }


        .drawer {

            position:fixed;

            top:0;
            left:-320px;

            width:290px;
            height:100%;

            background:rgba(22,27,34,.95);

            backdrop-filter:blur(20px);

            border-right:2px solid #00bfff;

            transition:.4s;

            z-index:20000;

            padding:30px;

        }


        .drawer.open {

            left:0;

        }


        .glass-card {

            background:rgba(255,255,255,.05);

            backdrop-filter:blur(15px);

            border:1px solid rgba(0,191,255,.3);

            border-radius:20px;

            padding:25px;

            margin:25px auto;

            max-width:500px;

        }



        .search-box {

            max-width:500px;

            margin:auto;

            position:relative;

            z-index:500;

        }


        #custom_suggestions {


            position:absolute;

            width:100%;


            background:rgba(22,27,34,.95);


            border:1px solid #00bfff;


            border-radius:10px;


            display:none;


            max-height:250px;


            overflow:auto;


            z-index:9999;

        }


        .suggestion-item {


            padding:12px;


            cursor:pointer;

        }


        .suggestion-item:hover {


            background:rgba(0,191,255,.15);


        }


        .btn-neon {


            width:100%;

            padding:12px;

            border-radius:10px;

            border:none;

            background:#00bfff;

            font-weight:bold;

        }


        .neon-text {

            color:#00bfff;

        }


        """)


        ,

        ui.tags.script("""

        function toggleDrawer(){

            document
            .getElementById("drawer")
            .classList.toggle("open");

        }


        function selectModel(m){

            document
            .getElementById("search_query")
            .value=m;


            document
            .getElementById("custom_suggestions")
            .style.display="none";


            Shiny.setInputValue(
            "search_query",
            m,
            {priority:"event"}
            );

        }


        """)

    ),



    ui.HTML('<div id="drawer" class="drawer">'),

    ui.h3("⚙️ Supabase",class_="neon-text"),

    ui.p(
        "📱 عدد الموديلات: ",
        ui.output_text("model_count")
    ),


    ui.p(
        "🔇 المراقب الصامت: نشط"
    ),


    ui.HTML("</div>"),



    ui.div(

        ui.HTML(
            '<div onclick="toggleDrawer()" '
            'style="font-size:28px;cursor:pointer;color:#00bfff">☰</div>'
        ),


        ui.h2(
            "ZEGAAR AMMAR",
            style="color:#00bfff"
        ),


        class_="header-bar"

    ),



    ui.div(

        ui.input_text(
            "search_query",
            "",
            placeholder="ابحث عن موديل الهاتف..."
        ),


        ui.HTML(
            '<div id="custom_suggestions"></div>'
        ),


        ui.output_ui(
            "main_content_ui"
        ),


        class_="search-box"

    )

)
# ==========================================================
# 3) السيرفر
# ==========================================================

def server(input, output, session):

    trigger_refresh = reactive.value(0)
    current_step = reactive.value(0)

    # ------------------------------------------------------
    # جلب قاعدة البيانات من Supabase مع إصلاح صياغة الحقول
    # ------------------------------------------------------
    @reactive.calc
    def cloud_database():
        trigger_refresh()
        try:
            # تم تعديل الاستعلام ليكون متوافقاً ومستقراً مع كافة إصدارات السحاب
            response = supabase.table("phones").select("*").execute()
            data = response.data if hasattr(response, 'data') else response
            
            if data and isinstance(data, list):
                return data
            return []
        except Exception as e:
            print("SUPABASE ERROR:", e)
            return []

    # ------------------------------------------------------
    # عداد الموديلات
    # ------------------------------------------------------
    @render.text
    def model_count():
        try:
            db = cloud_database()
            return str(len(db))
        except:
            return "0"

    # ------------------------------------------------------
    # Auto Complete الفوري والمحمي هندسياً من التداخل البصري
    # ------------------------------------------------------
    @reactive.effect
    def suggestions():
        q = input.search_query().strip()
        if not q:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display='none';")
            return

        db = cloud_database()
        names = [x["model_name"] for x in db if isinstance(x, dict) and x.get("model_name")]
        result = [m for m in names if q.lower() in m.lower()]

        html = ""
        for m in result[:20]:
            html += f"<div class='suggestion-item' onclick=\"selectModel('{escape(m)}')\">{m}</div>"

        if html:
            ui.update_html("custom_suggestions", content=html)
            ui.run_javascript("document.getElementById('custom_suggestions').style.display='block';")
        else:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display='none';")

    # ------------------------------------------------------
    # عرض النتائج والخطوات (معزولة ومستقرة تماماً ولا تختفي)
    # ------------------------------------------------------
    @render.ui
    def main_content_ui():
        query = input.search_query().strip()
        if not query:
            return ui.div()

        db = cloud_database()
        phone = next((x for x in db if isinstance(x, dict) and x.get("model_name") == query), None)

        # إذا كان الهاتف موجود في السحاب يعرض الـ workflow
        if phone:
            ui.run_javascript("document.getElementById('custom_suggestions').style.display='none';")
            return ui.HTML(run_system_workflows(query, phone, db))

        # في حالة هاتف جديد - تشغيل معالج خطوات الطوارئ
        if current_step() == 0:
            current_step.set(1)

        step = current_step()

        if step == 1:
            return ui.div(
                ui.h4("📏 الخطوة 1: أدخل المقاس", class_="neon-text"),
                ui.input_text("v1", "المقاس"),
                ui.input_action_button("next1", "التالي ➡️", class_="btn-neon"),
                class_="glass-card"
            )

        if step == 2:
            return ui.div(
                ui.h4("📺 الخطوة 2: شكل الشاشة", class_="neon-text"),
                ui.input_select("v2", "الشاشة", ["Notch Screen", "Punch Screen", "Curved Screen"]),
                ui.input_action_button("next2", "التالي ➡️", class_="btn-neon"),
                class_="glass-card"
            )

        if step == 3:
            return ui.div(
                ui.h4("🔌 الخطوة 3: المستشعر", class_="neon-text"),
                ui.input_select("v3", "المشعر", ["hardware", "under_display", "virtual"]),
                ui.input_action_button("save", "حفظ في Supabase", class_="btn-neon"),
                class_="glass-card"
            )
        return ui.div()

    # ------------------------------------------------------
    # التنقل والتحكم بالخطوات
    # ------------------------------------------------------
    @reactive.effect
    @reactive.event(input.next1)
    def step2():
        current_step.set(2)

    @reactive.effect
    @reactive.event(input.next2)
    def step3():
        current_step.set(3)

    # ------------------------------------------------------
    # الحفظ السحابي المباشر للأعمدة الصحيحة
    # ------------------------------------------------------
    @reactive.effect
    @reactive.event(input.save)
    def save_phone():
        try:
            data = {
                "model_name": input.search_query().strip(),
                "size": input.v1().strip() if "v1" in input else "",
                "panel": input.v2() if "v2" in input else "Notch Screen",
                "sensor": input.v3() if "v3" in input else "hardware"
            }

            supabase.table("phones").insert(data).execute()
            trigger_refresh.set(trigger_refresh() + 1)
            current_step.set(0)
            ui.run_javascript("alert('تم الحفظ بنجاح في Supabase السحابي!');")
        except Exception as e:
            print(e)
            ui.run_javascript(f"alert('خطأ أثناء الحفظ: {escape(str(e))}')")

# ==========================================================
# 4) تشغيل التطبيق السحابي المتكامل
# ==========================================================
app = App(app_ui, server)

