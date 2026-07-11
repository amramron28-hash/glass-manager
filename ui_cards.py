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
            f"📐 المقاس : {coords.get('size','-')}",
            class_="coord-line"
        ),

        ui.div(
            f"🖥 نوع الشاشة : {coords.get('panel','-')}",
            class_="coord-line"
        ),

        ui.div(
            f"📡 المستشعر : {coords.get('sensor','-')}",
            class_="coord-line"
        ),

        class_="glass-card neon-card"

    )


# ==========================================================
# RESULT SECTION
# ==========================================================

def draw_neon_section(
    title,
    models,
    color="#00e5ff",
    icon="📱",
    phone="",
    section_type="exact"
):

    if not models:
        return None

    cards = []

    for model in models:

        cards.append(

            ui.div(

                ui.div(
                    model,
                    class_="model-name"
                ),

                class_=f"glass-result-card {section_type}"

            )

        )

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

            class_=f"result-title {section_type}"

        ),

        *cards,

        class_="neon-container"

    )


# ==========================================================
# WARNING CARD
# ==========================================================

def draw_warning_card(message):

    return ui.div(

        ui.span(
            "⚠️",
            class_="result-icon"
        ),

        ui.span(
            message,
            class_="result-title-text"
        ),

        class_="glass-result-card warn"

    )

