import os
import json
from shiny import App, ui, render, reactive
from dotenv import load_dotenv
from database import load_db, save_db
from ui_components import inject_pwa_and_styles, draw_control_panel, draw_technical_coords, draw_neon_section
from workflows import run_system_workflows

load_dotenv()

# --- الواجهة (UI) ---
app_ui = ui.page_fluid(
    ui.HTML(inject_pwa_and_styles()), # حقن الـ PWA والـ CSS
    ui.div(
        ui.h2("ZEGAAR AMMAR", style="color:#00bfff; text-align:center; margin-top:20px;"),
        ui.p("GLASS MANAGER", style="color:white; text-align:center;"),
        class_="header-bar"
    ),
    ui.output_ui("control_panel"),
    ui.div(
        ui.input_text("search_query", "", placeholder="ابحث عن موديل الهاتف..."),
        ui.output_ui("suggestions_curtain_ui"),
        ui.input_action_button("btn_search", "افحص الهاتف 🔍", class_="btn-neon"),
        ui.output_ui("main_content_ui"),
        class_="search-box"
    )
)

# --- السيرفر (Server) ---
def server(input, output, session):
    # حالات التطبيق (States)
    refresh_trigger = reactive.value(0)
    current_plan = reactive.value(0)
    wizard_step = reactive.value(1)
    show_suggestions = reactive.value(False)

    @reactive.calc
    def cloud_database():
        refresh_trigger.get()
        return load_db()

    @render.ui
    def control_panel():
        return draw_control_panel(total_models=len(cloud_database()))

    @reactive.effect
    @reactive.event(input.search_query)
    def _(): show_suggestions.set(len(input.search_query().strip()) > 0)

    @render.ui
    def suggestions_curtain_ui():
        if not show_suggestions(): return None
        q = input.search_query().strip().lower()
        db = cloud_database()
        found = []
        for sz in db:
            for p in db[sz]:
                for s in db[sz][p]:
                    found.extend([m for m in db[sz][p][s]["models"] if q in m.lower()])
        found = list(set(found))[:8]
        items = [ui.div(f"📱 {m}", class_="suggestion-row", 
                 onclick=f"Shiny.setInputValue('selected_model', '{m}', {{priority:'event'}})") for m in found]
        return ui.div(*items, class_="suggestions-curtain") if items else None

    @reactive.effect
    @reactive.event(input.selected_model)
    def _():
        ui.update_text("search_query", value=input.selected_model())
        show_suggestions.set(False)

    @reactive.effect
    @reactive.event(input.btn_search)
    def _():
        db = cloud_database()
        q = input.search_query().strip()
        # المنطق: إذا وجد الموديل نذهب للخطة 1، إذا لا نذهب للخطة 2 (Wizard)
        found = False
        for sz in db:
            for p in db[sz]:
                for s in db[sz][p]:
                    if any(q.lower() == m.lower() for m in db[sz][p][s]["models"]):
                        found = True
        current_plan.set(1 if found else 2)
        if not found: wizard_step.set(1)

    @render.ui
    def main_content_ui():
        plan = current_plan()
        q = input.search_query().strip()
        if plan == 1:
            return ui.HTML(run_system_workflows(q, cloud_database(), []))
        
        if plan == 2:
            step = wizard_step()
            if step == 1: return ui.div(ui.h4("📏 المقاس"), ui.input_text("v1", ""), ui.input_action_button("next1", "التالي"))
            if step == 2: return ui.div(ui.h4("📺 الشاشة"), ui.input_select("v2", "", ["Notch", "Punch"]), ui.input_action_button("next2", "التالي"))
            if step == 3: return ui.div(ui.h4("🔌 الحساس"), ui.input_select("v3", "", ["hardware", "under_display"]), ui.input_action_button("check_spec_match", "فحص"))
        return None

    # معالجات الـ Wizard
    @reactive.effect
    @reactive.event(input.next1)
    def _(): wizard_step.set(2)
    
    @reactive.effect
    @reactive.event(input.next2)
    def _(): wizard_step.set(3)

    @reactive.effect
    @reactive.event(input.check_spec_match)
    def _():
        # هنا يتم حفظ الموديل الجديد باستخدام save_db من database.py
        success = save_db(None, input.search_query(), input.v1(), input.v2(), input.v3())
        if success:
            ui.notification_show("تم الحفظ بنجاح!", type="message")
            refresh_trigger.set(refresh_trigger() + 1)
            current_plan.set(1)

app = App(app_ui, server)
