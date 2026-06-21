from shiny import App, ui, render, reactive
from database import load_db

db_data = load_db()

app_ui = ui.page_fluid(
    ui.head_content(ui.HTML("""
        <style>
            :root { --neon-blue: #00bfff; }
            body { background-color: #060e1c; color: white; }
            .search-wrapper { margin: 20px auto; width: 90%; text-align: center; }
            .step-container { background: rgba(11, 26, 51, 0.8); border: 2px solid var(--neon-blue); padding: 20px; margin: 15px auto; width: 90%; border-radius: 15px; }
            .step-title { color: var(--neon-blue); font-weight: bold; margin-bottom: 15px; }
            .btn-neon { background: var(--neon-blue); border: none; padding: 8px 15px; border-radius: 5px; color: white; cursor: pointer; margin: 5px; }
            .btn-add { background: #2ecc71; border: none; padding: 5px 10px; border-radius: 3px; color: white; font-size: 0.8rem; }
        </style>
    """)),
    ui.div(ui.h2("ZEGAAR AMMAR", style="color:#00bfff; text-align:center;"), 
           ui.input_text("search", "", placeholder="ابحث عن موديل الهاتف..."), class_="search-wrapper"),
    ui.output_ui("flow_ui")
)

def server(input, output, session):
    step = reactive.value(1)
    show_add_panel = reactive.value(False)
    show_add_sensor = reactive.value(False)

    @render.ui
    def flow_ui():
        # المنطق: إذا لم يوجد نص بحث، نعرض الخطوات
        if not input.search():
            if step() == 1:
                return ui.div(ui.div("📏 حدد المقاس", class_="step-title"), 
                              ui.input_text("size", "المقاس..."), 
                              ui.input_action_button("next1", "التالي", class_="btn-neon"), class_="step-container")
            
            elif step() == 2:
                items = [ui.div("📺 شكل الشاشة", class_="step-title"),
                         ui.input_select("panel", "", ["Notch", "Punch Hole", "Curved"]),
                         ui.input_action_button("add_p", "+ إضافة جديد", class_="btn-add")]
                if show_add_panel(): items.append(ui.input_text("new_p", "أدخل الشكل الجديد..."))
                items.append(ui.input_action_button("next2", "التالي", class_="btn-neon"))
                return ui.div(*items, class_="step-container")
            
            elif step() == 3:
                items = [ui.div("🔌 المستشعر", class_="step-title"),
                         ui.input_select("sensor", "", ["Hardware", "Virtual"]),
                         ui.input_action_button("add_s", "+ إضافة جديد", class_="btn-add")]
                if show_add_sensor(): items.append(ui.input_text("new_s", "أدخل المستشعر الجديد..."))
                items.append(ui.input_action_button("finish", "إتمام", class_="btn-neon"))
                return ui.div(*items, class_="step-container")

    @reactive.effect
    @reactive.event(input.next1)
    def _(): step.set(2)
    
    @reactive.effect
    @reactive.event(input.next2)
    def _(): step.set(3)
    
    @reactive.effect
    @reactive.event(input.add_p)
    def _(): show_add_panel.set(not show_add_panel())
    
    @reactive.effect
    @reactive.event(input.add_s)
    def _(): show_add_sensor.set(not show_add_sensor())

app = App(app_ui, server)
