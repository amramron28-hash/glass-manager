from shiny import App, ui, render, reactive
from database import load_db

# تحميل البيانات عند التشغيل
db_data = load_db()

app_ui = ui.page_fluid(
    ui.head_content(ui.HTML("""
        <style>
            :root { --neon-blue: #00bfff; --bg-dark: #060e1c; }
            body { background-color: var(--bg-dark); color: white; font-family: sans-serif; }
            .step-container { 
                background: rgba(11, 26, 51, 0.8); 
                border: 2px solid var(--neon-blue); 
                padding: 25px; 
                margin: 20px auto; 
                width: 90%;
                border-radius: 15px; 
                box-shadow: 0 0 15px rgba(0, 191, 255, 0.3);
            }
            .step-title { color: var(--neon-blue); font-size: 1.4rem; font-weight: bold; margin-bottom: 20px; text-shadow: 0 0 8px var(--neon-blue); text-align: center; }
            .result-card {
                border: 1px solid var(--neon-blue);
                padding: 20px;
                margin-bottom: 25px;
                border-radius: 12px;
                background: rgba(0, 0, 0, 0.3);
                box-shadow: 0 0 12px rgba(0, 191, 255, 0.2);
                text-align: center;
                font-size: 1.1rem;
            }
            .btn-neon { background: var(--neon-blue); border: none; padding: 10px 20px; border-radius: 5px; color: white; cursor: pointer; width: 100%; margin-top: 10px; }
        </style>
    """)),
    ui.output_ui("emergency_steps_flow_ui")
)

def server(input, output, session):
    current_step = reactive.value(1)
    
    @render.ui
    def emergency_steps_flow_ui():
        step = current_step.get()
        
        # الخطوة 1: المقاس
        if step == 1:
            return ui.div(
                ui.div("📏 حدد مقاس الشاشة", class_="step-title"),
                ui.input_text("manual_size", "اكتب المقاس (اختياري)...", ""),
                ui.input_action_button("go_2", "التالي", class_="btn-neon"),
                class_="step-container"
            )
        
        # الخطوة 2: الشكل
        elif step == 2:
            return ui.div(
                ui.div("📺 اختر شكل الشاشة", class_="step-title"),
                ui.input_select("panel", "الشكل:", ["Notch Screen", "Punch Hole", "Curved Screen"]),
                ui.input_action_button("go_3", "التالي", class_="btn-neon"),
                class_="step-container"
            )
            
        # الخطوة 3: المستشعر والنتيجة النهائية
        elif step == 3:
            return ui.div(
                ui.div("✅ نتائج البحث المعتمدة", class_="step-title"),
                ui.div("الجهاز المطابق: OPPO RENO 2", class_="result-card"),
                ui.div(f"المقاس المعتمد: {input.manual_size() or 'غير محدد'}", class_="result-card"),
                ui.div(f"نوع الشاشة: {input.panel()}", class_="result-card"),
                ui.input_action_button("reset", "بحث جديد", class_="btn-neon", style="background:#ff4757;"),
                class_="step-container"
            )

    @reactive.effect
    @reactive.event(input.go_2)
    def _(): current_step.set(2)

    @reactive.effect
    @reactive.event(input.go_3)
    def _(): current_step.set(3)

    @reactive.effect
    @reactive.event(input.reset)
    def _(): current_step.set(1)

app = App(app_ui, server)
