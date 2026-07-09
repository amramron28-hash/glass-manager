from shiny import ui


# ==========================================================
# SEARCH BOX
# ==========================================================

def draw_search_box():

    return ui.div(

        ui.input_text(

            "search_query",

            "",

            placeholder="ابحث عن موديل الهاتف..."

        ),


        ui.output_ui(

            "suggestions_curtain"

        ),


        class_="search-box"

    )



# ==========================================================
# AUTOCOMPLETE CURTAIN
# ==========================================================

def draw_suggestions_curtain(suggestions):

    if not suggestions:

        return None


    return ui.div(

        *[

            ui.div(

                ui.span(

                    "📱",

                    class_="suggestion-icon"

                ),

                ui.span(

                    model,

                    class_="suggestion-text"

                ),


                class_="suggestion-row"

            )


            for model in suggestions

        ],


        class_="suggestions-curtain glass-card"

    )
