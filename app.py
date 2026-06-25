import os
from shiny import App, ui, render, reactive
from supabase import create_client

# استدعاء ملفات المشروع الخاصة بك
from workflows import run_system_workflows, get_compatibles_strict
from ui_components import (
    inject_pwa_and_styles,
    draw_plan_2_modal,
    draw_plan_3_modal
)

# تهيئة Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app_ui = ui.page_fluid(
    inject_pwa_and_styles(),
    ui.tags.head(
        ui.tags.style("""
            /* استهداف حصري للبطاقات داخل منطقة النتائج للحفاظ على شفافيتها */
            .results-container .suggestion-row, 
            .results-container .card-result {
                background: rgba(255, 255, 255, 0.08) !important;
                backdrop-filter: blur(15px) !important;
                -webkit-backdrop-filter: blur(15px) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 20px !important;
                padding: 15px !important;
                margin-bottom: 12px !important;
                color: white !important;
                text-align: center !important;
                font-weight: bold !important;
            }
            /* ترك حقل البحث (search-box) بدون تأثيرات ليعمل الـ Autocomplete بامتياز */
        """),
        ui.tags.script("""
            Shiny.addCustomMessageHandler('toggle_drawer', function(msg){
                let d = document.getElementById('settings_drawer');
                if(d){ msg === 'open' ? d.classList.add('open') : d.classList.remove('open'); }
            });
        """)
    ),
    # هيكل الواجهة
    ui.div(
        ui.input_text("search_query", "", placeholder="🔍 ابحث عن موديل الهاتف..."),
        ui.output_ui("suggestions_curtain"),
        class_="search-box"
    ),
    ui.div(ui.output_ui("results_area"), class_="results-container"),
    ui.output_ui("modal_layer")
)
def convert_database(rows):
    db = {}
    for item in rows:
        if not isinstance(item, dict): continue
        size, panel, sensor, model = str(item.get("size") or "").strip(), str(item.get("panel") or "").strip(), str(item.get("sensor") or "").strip(), str(item.get("model_name") or "").strip()
        if not size or not model: continue
        db.setdefault(size, {}).setdefault(panel, {}).setdefault(sensor, {"models": []})
        if model not in db[size][panel][sensor]["models"]:
            db[size][panel][sensor]["models"].append(model)
    return db

def server(input, output, session):
    db_trigger = reactive.Value(0)

    @reactive.calc
    def cloud_rows():
        db_trigger()
        try: return supabase.table("phones").select("*").execute().data or []
        except: return []

    @render.ui
    def results_area():
        p = input.search_query().strip()
        if not p: return None
        
        db = convert_database(cloud_rows())
        target_size, target_sensor, target_panel = None, "", ""
        
        for r in cloud_rows():
            if str(r.get("model_name") or "").strip().lower() == p.lower():
                try: target_size = float(r.get("size") or 0)
                except: target_size = None
                target_sensor, target_panel = str(r.get("sensor") or ""), str(r.get("panel") or "")
                break
        
        # النتائج الأساسية
        html_out = run_system_workflows(p, db, target_sensor)
        
        # النتائج الحمراء (التحذيرية)
        red_matches = []
        if target_size is not None:
            for r in cloud_rows():
                r_name, r_sensor, r_panel = str(r.get("model_name") or ""), str(r.get("sensor") or ""), str(r.get("panel") or "")
                try: r_size = float(r.get("size") or 0)
                except: continue
                if r_name.lower() != p.lower() and r_panel == target_panel and r_sensor != target_sensor and abs(r_size - target_size) <= 0.035:
                    lbl = "مطابق" if abs(r_size - target_size) < 0.005 else (f"+{abs(r_size-target_size):.2f}" if r_size > target_size else f"-{abs(r_size-target_size):.2f}")
                    if r_name not in [x[0] for x in red_matches]: red_matches.append((r_name, lbl))
        
        # استخدام كلاس card-result ليأخذ التأثير الزجاجي
        red_html = "".join([f'<div class="card-result">{name} <span style="font-size:10px; background:rgba(0,0,0,0.2); padding:2px 5px; border-radius:5px;">{lbl}</span></div>' for name, lbl in red_matches])
        
        return ui.HTML(f"{html_out}<div style='margin-top:20px;'>{red_html}</div>")

# ربط التطبيق
app = App(app_ui, server)
