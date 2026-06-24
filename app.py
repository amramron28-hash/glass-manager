import os
from shiny import App, ui, render, reactive
from supabase import create_client

from workflows import run_system_workflows, get_compatibles_strict
from ui_components import (
    inject_pwa_and_styles,
    draw_plan_2_modal,
    draw_plan_3_modal
)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def convert_database(rows):
    db = {}
    for item in rows:
        if not isinstance(item, dict): continue
        size = str(item.get("size") or "").strip()
        panel = str(item.get("panel") or "").strip()
        sensor = str(item.get("sensor") or "").strip()
        model = str(item.get("model_name") or "").strip()
        if not size or not model: continue
        db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})
        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)
    return db

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.tags.head(
        ui.tags.style("""
            /* تطبيق مظهر النيون الزجاجي على أي عنصر يظهر في منطقة النتائج */
            .results-container div, .suggestion-row, .card-result {
                background: rgba(255, 255, 255, 0.05) !important;
                backdrop-filter: blur(15px) !important;
                border: 1px solid rgba(0, 191, 255, 0.4) !important;
                box-shadow: 0 0 15px rgba(0, 191, 255, 0.2) !important;
                color: #00e5ff !important;
                border-radius: 15px !important;
                padding: 12px !important;
                margin-bottom: 10px !important;
                text-align: center !important;
                font-weight: bold !important;
            }
            .neon-red-card {
                border: 1px solid rgba(255, 0, 85, 0.6) !important;
                box-shadow: 0 0 20px rgba(255, 0, 85, 0.4) !important;
                color: #ff4d4d !important;
            }
        """),
        ui.tags.script("""
            Shiny.addCustomMessageHandler('toggle_drawer', function(msg){
                let d = document.getElementById('settings_drawer');
                if(d){ msg === 'open' ? d.classList.add('open') : d.classList.remove('open'); }
            });
        """)
    ),
    ui.div(
        ui.h3("⚙️ الإعدادات", style="color:#00bfff;text-align:right;margin-bottom:25px;"),
        ui.div(ui.input_switch("switch_notif", "🔔 تفعيل جرس الإشعارات", value=True), class_="metric-box"),
        ui.div(ui.input_switch("switch_monitor", "🛡️ تشغيل المراقب الصامت", value=True), class_="metric-box"),
        ui.output_ui("drawer_status_area"),
        ui.input_action_button("close_drawer", "إغلاق الترس", class_="btn-neon", style="width:100%;"),
        id="settings_drawer", class_="drawer"
    ),
    ui.div(
        ui.div(ui.div("ZEGAAR AMMAR", class_="brand-neon-main"), ui.div("GLASS MANAGER", class_="brand-neon-sub"), class_="brand-neon-title"),
        ui.input_action_button("btn_settings", "⚙️", class_="btn-neon", style="font-size:20px;padding:10px 15px;"),
        class_="header-bar"
    ),
    ui.div(
        ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."),
        ui.output_ui("suggestions_curtain"),
        class_="search-box"
    ),
    ui.div(ui.output_ui("results_area"), class_="results-container"),
    ui.output_ui("modal_layer")
)
def server(input, output, session):
    db_trigger = reactive.Value(0)
    current_search_phone = reactive.Value("")
    show_curtain = reactive.Value(False)
    active_modal = reactive.Value(None)
    custom_panels = reactive.Value([])
    custom_sensors = reactive.Value([])
    is_programmatic_update = reactive.Value(False)

    @reactive.calc
    def cloud_rows():
        db_trigger()
        try:
            result = supabase.table("phones").select("*").execute()
            return result.data or []
        except Exception: return []

    @reactive.calc
    def database(): return convert_database(cloud_rows())

    @reactive.effect
    @reactive.event(input.btn_settings)
    async def open_drawer(): await session.send_custom_message("toggle_drawer", "open")

    @reactive.effect
    @reactive.event(input.close_drawer)
    async def close_drawer(): await session.send_custom_message("toggle_drawer", "close")

    @render.ui
    def results_area():
        p = input.search_query().strip()
        if not p: return None
        
        target_size, target_sensor, target_panel = None, "", ""
        for r in cloud_rows():
            if str(r.get("model_name") or "").strip().lower() == p.lower():
                try: target_size = float(r.get("size") or 0)
                except: target_size = None
                target_sensor, target_panel = str(r.get("sensor") or ""), str(r.get("panel") or "")
                break
        
        # النتائج الأساسية (تتأثر بالـ CSS الجديد تلقائياً)
        html_out = run_system_workflows(p, database(), target_sensor)
        
        # النتائج الحمراء (التنبيهية) مع الكلاس الخاص بها
        red_matches = []
        if target_size is not None:
            for r in cloud_rows():
                r_name, r_sensor, r_panel = str(r.get("model_name") or ""), str(r.get("sensor") or ""), str(r.get("panel") or "")
                try: r_size = float(r.get("size") or 0)
                except: continue
                if r_name.lower() != p.lower() and r_panel == target_panel and r_sensor != target_sensor and abs(r_size - target_size) <= 0.035:
                    lbl = "مطابق" if abs(r_size - target_size) < 0.005 else (f"+{abs(r_size-target_size):.2f}" if r_size > target_size else f"-{abs(r_size-target_size):.2f}")
                    if r_name not in [x[0] for x in red_matches]: red_matches.append((r_name, lbl))
        
        red_html = "".join([f'<div class="neon-red-card">{name} <span style="font-size:10px;background:rgba(255,0,0,0.2);padding:2px 5px;border-radius:5px;">{lbl}</span></div>' for name, lbl in red_matches])
        
        return ui.HTML(f"{html_out}<div style='margin-top:20px;'>{red_html}</div>")

app = App(app_ui, server)
