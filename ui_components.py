import os
import base64

from html import escape
from shiny import ui


_bg_cache = None



def inject_pwa_and_styles():

    global _bg_cache


    if _bg_cache is None:

        for p in [
            "phone_image.webp",
            "./phone_image.webp",
            "/app/phone_image.webp"
        ]:

            if os.path.exists(p):

                with open(p, "rb") as f:

                    _bg_cache = base64.b64encode(
                        f.read()
                    ).decode()

                break



    if _bg_cache:

        bg_style = f"""
        background-image:
        linear-gradient(
        rgba(10,14,23,.20),
        rgba(10,14,23,.20)
        ),
        url(
        'data:image/webp;base64,{_bg_cache}'
        );
        """

    else:

        bg_style = "background-image:none;"



    return ui.HTML(f"""

<style>


html, body, .container-fluid {{

    background-color:#0a0e17 !important;

    {bg_style}

    background-size:92% auto !important;

    background-position:center center !important;

    background-repeat:no-repeat !important;

    background-attachment:fixed !important;

    color:white !important;

    direction:rtl !important;

    font-family:"Segoe UI",sans-serif !important;

}}



.header-bar {{

    display:flex;

    justify-content:space-between;

    align-items:center;

    padding:12px 25px;

    background:
    rgba(13,17,23,.55);

    backdrop-filter:blur(12px);

    border-bottom:
    1px solid rgba(0,191,255,.25);

}}



.brand-neon-title {{

    text-align:right;

    display:flex;

    flex-direction:column;

    gap:4px;

}}



.brand-neon-main {{

    color:#00bfff;

    font-size:28px;

    font-weight:900;

    text-shadow:
    0 0 5px rgba(0,191,255,.7),
    0 0 15px rgba(0,191,255,.5);

}}



.brand-neon-sub {{

    color:#87ceeb;

    font-size:16px;

    font-weight:700;

    letter-spacing:2px;

}}



.search-box {{

    position:relative;

    width:90%;

    max-width:500px;

    margin:30px auto;

}}



input[type="text"],
input[type="number"],
select {{

    width:100% !important;

    background:
    rgba(17,24,39,.90) !important;

    color:white !important;

    border:
    1px solid #00bfff !important;

    border-radius:14px !important;

    padding:14px !important;

    direction:ltr !important;

    text-align:left !important;

}}



.suggestions-curtain {{

    position:absolute;

    top:60px;

    right:0;

    left:0;

    background:
    rgba(22,27,34,.96);

    border:
    1px solid #00bfff;

    border-radius:12px;

    max-height:240px;

    overflow-y:auto;

    z-index:99999;

}}



.suggestion-row {{

    padding:12px;

    color:white;

    cursor:pointer;

    border-bottom:
    1px solid rgba(255,255,255,.08);

    direction:ltr !important;

    text-align:left;

}}



.suggestion-row:hover {{

    background:
    rgba(0,191,255,.18);

}}



.glass-card {{

    background:
    rgba(255,255,255,.06);

    backdrop-filter:blur(15px);

    border:
    1px solid rgba(0,191,255,.35);

    border-radius:20px;

    padding:20px;

    margin:20px auto;

    max-width:500px;

}}



.ammar-flat-card {{

    padding:16px 24px;

    margin-bottom:14px;

    border-radius:24px;

    width:100%;

}}



.flat-exact {{

background:
linear-gradient(
135deg,
rgba(76,187,85,.45),
rgba(34,111,41,.60)
);

}}



.flat-plus {{

background:
linear-gradient(
135deg,
rgba(41,98,255,.50),
rgba(13,50,163,.60)
);

}}



.flat-minus {{

background:
linear-gradient(
135deg,
rgba(255,165,0,.45),
rgba(230,126,34,.60)
);

}}



.flat-warning-card {{

background:
rgba(255,82,82,.45);

border-radius:12px;

padding:18px;

color:white;

font-weight:bold;

text-align:center;

}}



.flat-phone-text {{

color:white;

font-size:20px;

font-weight:800;

direction:ltr;

text-align:left;

}}



.drawer {{

position:fixed;

top:0;

right:-290px;

width:290px;

height:100%;

background:
rgba(22,27,34,.95);

transition:.4s;

z-index:200000;

padding:30px;

}}



.drawer.open {{

right:0;

}}



.metric-box {{

background:
rgba(255,255,255,.05);

padding:10px;

border-radius:8px;

margin-bottom:10px;

text-align:center;

}}



.custom-modal-backdrop {{

position:fixed;

top:0;

left:0;

width:100%;

height:100%;

background:
rgba(0,0,0,.75);

z-index:999999;

display:flex;

justify-content:center;

align-items:center;

}}


</style>

""")
def draw_warning_card(message):
    return ui.HTML(f"""
    <div class="flat-warning-card">
        ⚠️ {escape(str(message))}
    </div>
    """)


def draw_merge_confirm_modal(phone_name):
    return ui.div(
        ui.div(
            ui.div(
                ui.h3(
                    f"🔗 دمج الهاتف {phone_name}",
                    style="color:#00bfff;text-align:center;"
                ),

                ui.p(
                    "سيتم إضافة الهاتف داخل المجموعة الحالية بعد التأكيد.",
                    style="text-align:center;color:white;"
                ),

                ui.input_action_button(
                    "btn_merge",
                    "✅ تأكيد الدمج والتعلم",
                    class_="btn-neon",
                    style="""
                    width:100%;
                    background:#2ecc71;
                    color:white;
                    padding:12px;
                    border-radius:10px;
                    border:none;
                    """
                ),

                ui.modal_button(
                    "إلغاء"
                ),

                class_="glass-card",
                style="""
                width:90%;
                max-width:500px;
                background:rgba(22,27,34,.98);
                border:1px solid #00bfff;
                """
            ),

            class_="custom-modal-backdrop"
        )
    )


def draw_database_status(total):
    return ui.div(

        ui.div(
            f"📊 قاعدة البيانات: {total} هاتف",
            class_="metric-box"
        )

    )


def draw_simple_result(title, models, icon="📱"):

    if not models:
        return ui.div()

    items = [
        ui.h4(
            f"{icon} {title}",
            style="""
            color:#00bfff;
            text-align:right;
            direction:rtl;
            """
        )
    ]

    for model in models:

        items.append(

            ui.HTML(
                f"""
                <div class="ammar-flat-card flat-exact">

                    <div class="flat-phone-text">
                        {escape(str(model))}
                    </div>

                </div>
                """
            )

        )

    return ui.div(*items)


def draw_empty_database():

    return ui.HTML(
        """
        <div class="flat-warning-card">
            ⚠️ قاعدة البيانات فارغة
        </div>
        """
        )
def draw_merge_confirm_modal(phone_name):

    return ui.div(

        ui.div(

            ui.div(

                ui.h3(
                    f"🔗 تأكيد دمج {escape(str(phone_name))}",
                    style="""
                    color:#00bfff;
                    text-align:center;
                    """
                ),

                ui.p(
                    "سيتم إضافة الهاتف إلى قاعدة البيانات بعد التأكيد.",
                    style="""
                    color:white;
                    text-align:center;
                    """
                ),

                ui.input_action_button(
                    "btn_merge",
                    "✅ تأكيد الدمج والتعلم",
                    class_="btn-neon",
                    style="""
                    width:100%;
                    padding:12px;
                    background:#2ecc71;
                    color:white;
                    border:none;
                    border-radius:10px;
                    """
                ),

                ui.modal_button(
                    "إغلاق"
                ),

                class_="glass-card",

                style="""
                width:90%;
                max-width:500px;
                background:rgba(22,27,34,.98);
                border:1px solid #00bfff;
                """

            ),

            class_="custom-modal-backdrop"

        )

    )


def draw_database_stats(total):

    return ui.div(

        ui.div(
            f"📊 عدد السجلات: {total}",
            class_="metric-box"
        )

    )


def draw_empty_search():

    return ui.HTML(
        """
        <div class="flat-warning-card">
            ⚠️ لم يتم العثور على نتائج
        </div>
        """
)
