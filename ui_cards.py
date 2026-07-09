from shiny import ui


# ==========================================================
# PHONE TECHNICAL CARD
# ==========================================================

def draw_technical_coords(coords):

    if not coords:
        return None


    return ui.div(

        ui.h3(

            coords.get(
                "real_name",
                ""
            ),

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
# NEON RESULTS CARD
# ==========================================================

def draw_neon_section(
        title,
        models,
        cls
):

    if not models:
        return None


    return ui.div(

        ui.div(

            title,

            class_="result-title"

        ),


        *[

            ui.div(

                model,

                class_=f"ammar-flat-card {cls}"

            )

            for model in models

        ],


        class_="glass-card neon-container"

    )



# ==========================================================
# WARNING CARD (FUTURE USE)
# ==========================================================

def draw_warning_card(message):

    return ui.div(

        message,

        class_="flat-warning-card"

    )
