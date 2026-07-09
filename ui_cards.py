from shiny import ui


# ==========================================================
# PHONE TECHNICAL CARD
# ==========================================================

def draw_technical_coords(coords):

    if not coords:
        return None


    return ui.div(

        ui.h3(
            coords.get("real_name", ""),
            class_="phone-title"
        ),


        ui.div(
            f"المقاس : {coords.get('size','-')}",
            class_="coord-line"
        ),


        ui.div(
            f"نوع الشاشة : {coords.get('panel','-')}",
            class_="coord-line"
        ),


        ui.div(
            f"المستشعر : {coords.get('sensor','-')}",
            class_="coord-line"
        ),


        class_="glass-card neon-card"

    )



# ==========================================================
# NEON RESULTS SECTION
# ==========================================================

def draw_neon_section(
    title,
    models,
    color,
    icon,
    phone=""
):

    if not models:
        return None


    return ui.div(

        ui.div(

            ui.span(
                icon,
                class_="result-icon"
            ),

            ui.span(
                title,
                class_="result-title-text"
            ),

            class_="result-title",

            style=f"""
            color:{color};
            border-right:5px solid {color};
            box-shadow:0 0 15px {color};
            """

        ),


        *[

            ui.div(

                ui.div(
                    model,
                    class_="model-name"
                ),


                ui.div(
                    f"متوافق مع: {phone}",
                    class_="model-source"
                )
                if phone
                else None,


                class_="ammar-flat-card",

                style=f"""
                border:1px solid {color};
                box-shadow:0 0 18px {color};
                """

            )

            for model in models

        ],


        class_="glass-card neon-container"

    )



# ==========================================================
# WARNING CARD
# ==========================================================

def draw_warning_card(message):

    return ui.div(

        "⚠️ " + message,

        class_="flat-warning-card"

    )
