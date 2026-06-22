import os
import base64
from html import escape
from shiny import ui

_bg_cache = None


def inject_pwa_and_styles():
    global _bg_cache

    if _bg_cache is None:
        img = ""

        for p in [
            "phone_image.webp",
            "./phone_image.webp",
            "/app/phone_image.webp"
        ]:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    img = base64.b64encode(f.read()).decode()
                break

        _bg_cache = img

    return ui.HTML(f"""
    <style>

    html, body, .container-fluid {{
        background-color:#0a0e17 !important;
        background-image:
        linear-gradient(
        rgba(10,14,23,.20),
        rgba(10,14,23,.20)
        ),
        url('data:image/webp;base64,{_bg_cache}');

        background-size:92% auto !important;
        background-position:center !important;
        background-repeat:no-repeat !important;
        background-attachment:fixed !important;
        color:white;
        direction:rtl;
    }}


    .header-bar {{
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding:15px 25px;
        background:rgba(13,17,23,.55);
        backdrop-filter:blur(12px);
        border-bottom:1px solid rgba(0,191,255,.25);
    }}


    .search-box {{
        position:relative;
        width:90%;
        max-width:500px;
        margin:35px auto;
    }}


    .glass-card {{
        background:rgba(255,255,255,.06);
        backdrop-filter:blur(15px);
        border:1px solid rgba(0,191,255,.35);
        border-radius:20px;
        padding:20px;
        margin:15px auto;
        max-width:500px;
    }}


    .drawer {{
        position:fixed;
        top:0;
        right:-320px;
        width:290px;
        height:100%;
        background:rgba(22,27,34,.95);
        backdrop-filter:blur(20px);
        border-left:2px solid #00bfff;
        transition:.4s;
        z-index:20000;
        padding:30px;
    }}


    .drawer.open {{
        right:0;
    }}

    </style>
    """)



def draw_technical_coords(
    size_grp,
    panel_grp,
    sensor_grp,
    model_name=""
):

    return ui.HTML(f"""

    <div class="glass-card">

    <h3 style="color:#00bfff;">
    📱 {escape(str(model_name))}
    </h3>

    📏 <b>المقاس:</b> {escape(str(size_grp))}<br>

    📺 <b>نوع الشاشة:</b> {escape(str(panel_grp))}<br>

    👁️ <b>المستشعر:</b> {escape(str(sensor_grp))}

    </div>

    """)



def draw_neon_section(
    title=None,
    models_list=None,
    color_hex="#00bfff",
    badge_icon="📱"
):

    # دعم استدعاء:
    # draw_neon_section(list)

    if models_list is None and isinstance(title, list):

        models_list = title
        title = "الهواتف المتوافقة"



    if not models_list:
        return ui.div()



    cards = []


    cards.append(
        ui.h4(
            f"{badge_icon} {title}",
            style=f"
            color:{color_hex};
            text-align:right;
            direction:rtl;
            "
        )
    )


    for model in models_list:

        cards.append(
            ui.HTML(f"""

            <div style="
            background:rgba(10,14,23,.90);
            border:2px solid {color_hex};
            border-radius:12px;
            padding:14px;
            margin-bottom:10px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            direction:ltr;
            ">


            <div style="
            color:white;
            font-size:20px;
            font-weight:800;
            ">
            {escape(str(model))}
            </div>


            <div style="
            width:45px;
            height:45px;
            border-radius:8px;
            border:1px dashed #00bfff;
            ">
            📱
            </div>


            </div>

            """)
        )


    return ui.div(*cards)




def draw_control_panel(
    total_models=0,
    empty_groups_count=0
):

    return ui.div(

        ui.h3(
            "🛠️ لوحة التحكم",
            style="color:#00bfff;text-align:center;"
        ),


        ui.div(
            f"📱 الهواتف: {total_models}",
            class_="glass-card"
        ),


        ui.div(
            f"🧹 مراجعة: {empty_groups_count}",
            class_="glass-card"
        )

    )
