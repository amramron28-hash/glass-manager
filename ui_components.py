import os
import base64
from html import escape
from shiny import ui

_bg_cache = None

# ==========================================
# 🎨 الخلفية + التنسيق الفني المطور للبطاقات واللوحة المنبثقة
# ==========================================
def inject_pwa_and_styles():
    global _bg_cache
    if _bg_cache is None:
        paths = ["phone_image.webp", "./phone_image.webp", "/app/phone_image.webp"]
        img = ""
        for p in paths:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    img = base64.b64encode(f.read()).decode()
                break
        _bg_cache = img

    return f"""
    <style>
    html, body, .container-fluid {{
        background-color: #0a0e17 !important;
        background-image: linear-gradient(rgba(10,14,23,.20), rgba(10,14,23,.20)), url('data:image/webp;base64,{_bg_cache}');
        background-size: 92% auto !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    
    /* 🎨 تصميم البطاقات الزجاجية المتقطعة والمنفصلة بالكامل (طابق حجم ونمط صورتك) */
    .glass-card-item-exact {{
        background: rgba(12, 53, 27, 0.65) !important; /* لون أخضر داكن زجاجي مبطن */
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 2px solid #32cd32 !important; /* إطار نيون أخضر مضيء ومستقر */
        box-shadow: 0 0 14px rgba(50, 205, 50, 0.35); /* توهج نيون أخضر فاصل */
        padding: 16px 20px !important; /* نفس الارتفاع الممتد في صورتك */
        border-radius: 14px !important; /* حواف دائرية أنيقة ومتقنة */
        text-align: center !important; /* توسط الموديل في منتصف البطاقة */
        font-size: 20px !important; /* خط كبير وعريض */
        font-weight: 800 !important; /* Bold سميك */
        color: #ffffff !important; /* نص أبيض ناصع وثابت */
        margin-bottom: 14px !important; /* مسافة فاصلة عمودية تضمن الانفصال التام */
        width: 100%;
        box-sizing: border-box;
        transition: all 0.25s ease;
    }}
    .glass-card-item-exact:hover {{
        background: rgba(50, 205, 50, 0.25) !important;
        box-shadow: 0 0 20px rgba(50, 205, 50, 0.65);
        transform: translateY(-2px);
    }}

    .glass-window-card {{
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .shiny-split-layout {{
        gap: 15px !important;
    }}
    .sidebar-title {{
        text-align: center; 
        color: #00bfff; 
        margin-bottom: 20px;
        font-weight: bold;
    }}
    .metric-box {{
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 10px;
        text-align: center;
        border: 1px solid rgba(0,191,255,0.2);
    }}
    </style>
    """

# ==========================================
# 📋 بطاقة الإحداثيات الفنية للموديل الفعلي
# ==========================================
def draw_technical_coords(size_grp, panel_grp, sensor_grp, real_name=None):
    return f"""
    <div class="glass-window-card" style="background:rgba(15,23,42,.6); margin-top:15px; border: 1px solid #00bfff; box-shadow: 0 0 10px rgba(0,191,255,0.2);">
        <div style="direction:rtl; text-align:right; font-size:16px; line-height:1.7; color:white; width:100%;">
            {"🔍 <b>الموديل المتطابق:</b> " + escape(real_name) + "<br>" if real_name else ""}
            📏 <b>المقاس:</b> {escape(str(size_grp))} <br>
            📺 <b>نوع الشاشة:</b> {escape(str(panel_grp))} <br>
            👁️ <b>مستشعر التقارب:</b> {escape(str(sensor_grp))}
        </div>
    </div>
    """

# ==========================================
# 📱 بطاقات النتائج المتقطعة والمنفصلة (النيون الأخضر الزجاجي البولد)
# ==========================================
def draw_neon_section(models_list, title="هواتف مطابقة تماماً في الأبعاد والقص (Exact 0.00):", color_hex="#32cd32", badge_icon="🟢"):
    if not models_list:
        return ""

    html_cards = []
    # عنوان القسم العلوي متوافق تماماً مع لقطة الشاشة
    html_cards.append(f"""
    <h4 style="color:#ffffff; direction:rtl; text-align:right; margin:20px 0 12px 0; font-weight:bold; font-size:19px; display:flex; align-items:center; gap:8px;">
        <span style="color:{color_hex};">{badge_icon}</span> {title}
    </h4>
    <div style="display: flex; flex-direction: column; width:100%;">
    """)

    # تكرار ضخ الهواتف البديلة في بطاقات منفصلة ومتقطعة ذات حجم عريض ونقي
    for model in models_list:
        html_cards.append(f"""
        <div class="glass-card-item-exact">
            {escape(model)}
        </div>
        """)
        
    html_cards.append("</div>")
    return "\n".join(html_cards)

# ==========================================
# 🛠️ لوحة التحكم التفاعلية المدمجة لـ Shiny
# ==========================================
def draw_control_panel(notifications=None, total_models=0, empty_groups_count=0):
    notifications = notifications or []
    
    if notifications:
        notif_html = "".join([f"<div style='color:#ffc107; margin-bottom:5px;'>⚠️ {escape(n)}</div>" for n in notifications])
    else:
        notif_html = "<div style='color:#aaa; font-style:italic;'>لا توجد تنبيهات</div>"
        
    panel_ui = ui.sidebar(
        ui.HTML('<h3 class="sidebar-title">🛠️ لوحة التحكم</h3>'),
        
        ui.accordion(
            ui.accordion_panel(
                "🔔 الإشعارات",
                ui.HTML(notif_html)
            ),
            ui.accordion_panel(
                "⚙️ الإعدادات",
                ui.input_checkbox("silent_monitor_checkbox", "تفعيل المراقب الصامت", value=True)
            ),
            ui.accordion_panel(
                "🛡️ المراقب الصامت",
                ui.HTML(f"""
                    <div class="metric-box">
                        <div style="color:#aaa; font-size:14px;">📱 الهواتف</div>
                        <div style="color:#00bfff; font-size:24px; font-weight:bold;">{total_models}</div>
                    </div>
                    <div class="metric-box">
                        <div style="color:#aaa; font-size:14px;">🧹 مراجعة</div>
                        <div style="color:#ff4500; font-size:24px; font-weight:bold;">{empty_groups_count}</div>
                    </div>
                    <div style="color:#32cd32; text-align:center; font-size:12px; margin-top:5px;">● المراقب يعمل الآن بنجاح</div>
                """),
                open=True
            )
        ),
        position="left"
    )
    return panel_ui
