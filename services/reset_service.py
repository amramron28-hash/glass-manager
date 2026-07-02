from shiny import ui


def reset_ui(
    session,
    current_phone,
    show_curtain,
    suggestions_list,
    plan_results,
    current_plan_type,
    active_modal,
    plan_inputs,
    invalidate_workflow,
):
    ui.update_text(session, "search_query", value="")

    current_phone.set("")
    show_curtain.set(False)
    suggestions_list.set([])

    plan_results.set(None)
    current_plan_type.set(None)
    active_modal.set(None)

    for key in plan_inputs:
        plan_inputs[key].set("")

    invalidate_workflow()
