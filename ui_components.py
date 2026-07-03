import os
import base64
from html import escape
from shiny import ui

# 1. أولاً: تعريف دالة inject_pwa_and_styles
_bg_cache = None

def inject_pwa_and_styles():
    global _bg_cache
    if _bg_cache is None:
        for p in ["phone_image.webp", "./phone_image.webp", "/app/phone_image.webp"]:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    _bg_cache = base64.b64encode(f.read()).decode()
                break
    
    bg_style = f"background-image:linear-gradient(rgba(10,14,23,.20),rgba(10,14,23,.20)),url('data:image/webp;base64,{_bg_cache}');" if _bg_cache else "background-image:none;"
    
    return ui.HTML(f"""<style>
    /* ... (نفس الستايل الخاص بك دون تغيير) ... */
    html, body, .container-fluid {{ background-color:#0a0e17 !important; {bg_style} }}
    .drawer {{ position:fixed; top:0; right:-310px; width:300px; height:100%; background:rgba(15,22,36,.98); backdrop-filter:blur(20px); border-left:1px solid rgba(0,191,255,.3); transition:.4s ease-in-out; z-index:200000; padding:30px; }}
    .drawer.open {{ right:0 !important; }}
    </style>""")

# 2. ثانياً: تعريف دوال الرسم (Draw functions)
def draw_technical_coords(size_grp, panel_grp, sensor_grp, model_name=""):
    return ui.HTML(f'<div class="glass-card">...</div>') # (نفس الكود الخاص بك)

# ... (ضع باقي دوال draw_... هنا) ...

# 3. ثالثاً: تعريف app_ui في نهاية الملف بعد تعريف جميع الدوال
app_ui = ui.page_fluid(
    inject_pwa_and_styles(),  # الآن هذه الدالة معرفة وموجودة!
    ui.tags.head(
        ui.tags.script("""
        Shiny.addCustomMessageHandler('toggle_drawer', function(msg){
            let d = document.getElementById('settings_drawer');
            if(d){ if(msg === 'open') d.classList.add('open'); else d.classList.remove('open'); }
        });
        """)
    ),
    # ... (باقي مكونات الواجهة) ...
)
