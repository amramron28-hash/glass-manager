import os
import base64
from html import escape

from shiny import App, ui, render, reactive
from ui_components import inject_pwa_and_styles


# ==========================================================
# تحويل صورة الخلفية إلى Base64
# ==========================================================

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            return f"data:image/webp;base64,{encoded}"
    return ""


bg_img_base64 = get_base64_image("phone_image.webp")


# ==========================================================
# واجهة التطبيق
# ==========================================================

app_ui = ui.page_fluid(

    ui.head_content(

        ui.HTML("""
        <link rel="manifest" href="/manifest.json">
        <meta name="theme-color" content="#00bfff">
        """),

        ui.HTML("""
        <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/service-worker.js')
            .then(() => console.log("PWA Connected"))
            .catch(() => console.log("PWA Failed"));
        }
        </script>
        """),

        ui.HTML(inject_pwa_and_styles()),


        ui.HTML("""
<style>


.main-header-container {
    width:100%;
    text-align:center;
    margin-top:20px;
    margin-bottom:25px;
    padding:5px;
    background:rgba(13,17,23,0.7);
    border-radius:8px;
}


.main-logo {
    font-size:24px !important;
    font-weight:900 !important;
    color:#00bfff !important;
}


.main-subtitle {
    color:white;
    font-size:16px;
}


.search-wrapper-box {

    width:100%;
    max-width:85%;
    margin:auto;
    position:relative;

}


.shiny-input-container {

    width:100% !important;

}


.shiny-input-container input {

    background:rgba(255,255,255,0.07) !important;
    color:white !important;

    border:1px solid rgba(0,191,255,0.3) !important;

    border-radius:6px;

    padding:12px;

    width:100% !important;

}


.curtain-dropdown-menu {


    position:absolute !important;

    top:100%;

    left:0;

    width:100%;

    background:rgba(10,14,23,0.98);

    border:1px solid #00bfff;

    border-radius:8px;

    z-index:99999;

    padding:5px 0;

}


.curtain-title {

    padding:8px;

    color:#00bfff;

    font-weight:bold;

    text-align:right;

}



.suggestion-link-btn {


    width:100%;

    background:none;

    border:none;

    color:white;

    text-align:left;

    padding:10px 15px;

    cursor:pointer;

    font-size:16px;


}



.suggestion-link-btn:hover {


    background:rgba(0,191,255,0.15);

    color:#00bfff;


}




.side-drawer-container {

    position:fixed;

    top:15px;

    left:-290px;

    width:290px;

    background:rgba(13,17,23,.95);

    border:1px solid #00bfff;

    transition:.4s;

    padding:15px;

    z-index:9999;


}


.drawer-open {

    left:0 !important;

}


.drawer-toggle-btn {


    position:absolute;

    right:-35px;

    top:50%;

    width:35px;

    height:45px;

    cursor:pointer;

}



.step-container {


    background:rgba(255,255,255,.05);

    border:1px dashed #00bfff;

    padding:15px;

    margin-top:15px;


}


.step-title {


    color:#00bfff;

    font-weight:bold;


}



.step-next-btn {


    background:#00bfff;

    border:none;

    padding:6px 15px;

    margin-top:10px;

    cursor:pointer;


}



</style>
        """)
    ),



    # ======================================================
    # القائمة الجانبية
    # ======================================================


    ui.HTML("""
<div id="side_drawer" class="side-drawer-container">

<button id="drawer_toggle"
class="drawer-toggle-btn"
onclick="toggleDrawer()">

🡪

</button>


<button onclick="alert('الإعدادات')">
⚙️
</button>


</div>



<script>

function toggleDrawer(){

let d=document.getElementById("side_drawer");

let b=document.getElementById("drawer_toggle");


if(d.classList.contains("drawer-open")){

d.classList.remove("drawer-open");

b.innerHTML="🡪";

}else{


d.classList.add("drawer-open");

b.innerHTML="🡨";


}

}

</script>
"""),




# ======================================================
# العنوان
# ======================================================


ui.HTML("""
<div class="main-header-container">

<div class="main-logo">

ZEGAAR AMMAR

</div>


<div class="main-subtitle">

GLASS MANAGER

</div>

</div>
"""),



# ======================================================
# البحث
# ======================================================


ui.div(

    ui.input_text(
        "free_smart_search_input_field",
        "",
        placeholder="ابحث عن موديل الهاتف..."
    ),


    ui.output_ui(
        "floating_suggestions_ui"
    ),


    class_="search-wrapper-box"

),



ui.output_ui(
    "matched_results_ui"
),



ui.output_ui(
    "emergency_steps_flow_ui"
)

)
# ==========================================================
# 3. منطق السيرفر والمزامنة الجلسية
# ==========================================================


def server(input, output, session):

    from database import load_db
    from workflows import run_system_workflows, find_model_coords


    # تحميل قاعدة البيانات

    db_data = reactive.value(load_db())


    # متغيرات خطة الطوارئ

    current_step = reactive.value(1)

    manual_size = reactive.value("")

    manual_panel = reactive.value("")

    manual_sensor = reactive.value("")



    # إعادة ضبط الخطة عند تغيير البحث

    @reactive.effect

    @reactive.event(input.free_smart_search_input_field)

    def reset_emergency_flow():

        current_step.set(1)

        manual_size.set("")

        manual_panel.set("")

        manual_sensor.set("")




    # ======================================================
    # البحث الذكي والاقتراحات
    # ======================================================


    @reactive.calc

    def filtered_suggestions():


        query = input.free_smart_search_input_field().strip()


        if not query or len(query) < 2:

            return []



        index_file = os.path.join(

            os.path.dirname(os.path.abspath(__file__)),

            "models_index.txt"

        )


        models=[]


        if os.path.exists(index_file):

            with open(index_file,"r",encoding="utf-8") as f:

                models=[

                    line.strip()

                    for line in f

                    if line.strip()

                ]



        return [

            m for m in models

            if query.lower() in m.lower()

        ][:5]





    # ======================================================
    # ستارة الاقتراحات - مصححة
    # ======================================================


    @render.ui

    def floating_suggestions_ui():


        suggestions = filtered_suggestions()

        query = input.free_smart_search_input_field().strip()



        if not suggestions:

            return ui.HTML("")



        html=[]



        html.append(

        "<div class='curtain-dropdown-menu'>"

        )



        html.append(

        "<div class='curtain-title'>💡 الموديلات المقترحة:</div>"

        )



        for item in suggestions:


            safe_item = escape(item)


            html.append(f"""

<button

class="suggestion-link-btn"

onclick="selectModelSuggestion('{safe_item}')">


{safe_item}


</button>

""")



        html.append("</div>")



        return ui.HTML("\n".join(html))







    # ======================================================
    # جافاسكربت اختيار الاقتراح
    # ======================================================


    @render.ui

    def suggestion_script():


        return ui.HTML("""


<script>


function selectModelSuggestion(value){


document.getElementById(
'free_smart_search_input_field'
).value=value;


Shiny.setInputValue(
'free_smart_search_input_field',
value,
{priority:'event'}
);


}


</script>


""")





    # ======================================================
    # نتائج الخطة الأولى
    # ======================================================


    @render.ui

    def matched_results_ui():


        query=input.free_smart_search_input_field().strip()


        if not query:

            return ui.HTML("")



        try:


            result = run_system_workflows(

                query,

                db_data.get(),

                filtered_suggestions()

            )


            return ui.HTML(result)



        except Exception as e:


            return ui.HTML(

            f"""

            <div style='color:red'>

            خطأ النظام:

            {escape(str(e))}

            </div>

            """

            )





    # ======================================================
    # خطة الطوارئ 2 و 3
    # ======================================================


    @render.ui

    def emergency_steps_flow_ui():


        query=input.free_smart_search_input_field().strip()



        if not query:

            return ui.HTML("")



        size_str,panel,sensor,real_name = find_model_coords(

            db_data.get(),

            query

        )



        if real_name and query.lower()==real_name.lower():

            return ui.HTML("")



        step=current_step.get()



        if step==1:


            return ui.div(


                ui.div(

                "📏 حدد مقاس الشاشة",

                class_="step-title"

                ),



                ui.input_select(

                "step_size_select",

                "المقاس:",

                choices=[

                "6.40",

                "6.43",

                "6.50",

                "6.55",

                "6.67",

                "6.70"

                ]

                ),



                ui.input_action_button(

                "go_to_step_2",

                "التالي",

                class_="step-next-btn"

                ),


                class_="step-container"


            )



        elif step==2:


            return ui.div(


            ui.div(

            "📺 اختر نوع الشاشة",

            class_="step-title"

            ),



            ui.input_select(

            "step_panel_select",

            "الشكل:",

            choices=[

            "Notch Screen",

            "Punch Hole",

            "Dynamic Island",

            "Curved Screen"

            ]

            ),



            ui.input_action_button(

            "go_to_step_3",

            "التالي",

            class_="step-next-btn"

            ),



            class_="step-container"


            )





        elif step==3:


            return ui.div(


            ui.div(

            "🔌 اختر المستشعر",

            class_="step-title"

            ),


            ui.input_select(

            "step_sensor_select",

            "المستشعر:",

            choices=[

            "Hardware Sensor",

            "Virtual Sensor",

            "Under Display"

            ]

            ),



            ui.input_action_button(

            "trigger_emergency_plan_3",

            "بحث",

            class_="step-next-btn"

            ),



            class_="step-container"


            )



    # ======================================================
    # تشغيل التطبيق
    # ======================================================


app = App(

    app_ui,

    server

            )
