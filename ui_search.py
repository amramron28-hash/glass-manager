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

    rows = []

    for model in suggestions:

        rows.append(

            ui.div(

                ui.div(

                    "📱",

                    class_="suggestion-icon"

                ),

                ui.div(

                    model,

                    class_="suggestion-text"

                ),

                class_="suggestion-row",

                **{
                    "data-value": model
                }

            )

        )

    return ui.div(

        *rows,

        class_="suggestions-curtain"

    )
