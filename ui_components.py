import os
import base64
from html import escape
from shiny import ui

_bg_cache = None

# ==========================================
# 🎨 الخلفية + التنسيق (تم إضافة الـ CSS للزجاج هنا)
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

    # إرجاع الـ ستايل المخصص ليتم حقنه في رأس واجهة Shiny لسرعة الأداء
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
    /* التعديل الجوهري: تأثير الزجاج الصافي */
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
# 📋 بطاقة الإحداثيات الفنية (تم التعديل لتتناسب مع التصميم)
# ==========================================
def draw_technical_coords(size_grp, panel_grp, sensor_grp, real_name=None):
    return f"""
    <div class="glass-window-card" style="background:rgba(15,23,42,.6); margin-top:15px;">
        <div style="direction:rtl; text-align:right; font-size:16px; line-height:1.7; color:white; width:100%;">
            {"🔍 <b>الموديل المتطابق:</b> " + escape(real_name) + "<br>" if real_name else ""}
            📏 <b>المقاس:</b> {escape(str(size_grp))} <br>
            📺 <b>نوع الشاشة:</b> {escape(str(panel_grp))} <br>
            👁️ <b>مستشعر التقارب:</b> {escape(str(sensor_grp))}
        </div>
    </div>
    """

# ==========================================
# 📱 بطاقات النتائج (تم الحفاظ على التوهج وتأثير الزجاج والـ Bold)
# ==========================================
def draw_neon_section(models_list, title="الأجهزة المتوافقة والمدعومة بالكامل وبنفس الأبعاد الصارمة:", color_hex="#00bfff", badge_icon="📱"):
    if not models_list:
        return ""

    html_cards = []
    html_cards.append(f"""
    <h4 style="color:{color_hex}; direction:rtl; text-align:right; margin:15px 0 8px 0; font-weight:bold;">
    {badge_icon} {title}
    </h4>
    """)

    for model in models_list:
        html_cards.append(f"""
        <div class="glass-window-card" style="border-left: 6px solid {color_hex}; background: {color_hex}25;">
            <div style="font-size: 18px; font-weight: 800; color: #ffffff; text-align: left; width:100%;">
                {escape(model)}
            </div>
        </div>
        """)
        
    return "\n".join(html_cards)

# ==========================================
# 🛠️ لوحة التحكم التفاعلية والمطابقة تماماً لـ Shiny
# ==========================================
def draw_control_panel(notifications=None, total_models=0, empty_groups_count=0):
    notifications = notifications or []
    
    # تحضير كود الإشعارات
    if notifications:
        notif_html = "".join([f"<div style='color:#ffc107; margin-bottom:5px;'>⚠️ {escape(n)}</div>" for n in notifications])
    else:
        notif_html = "<div style='color:#aaa; font-style:italic;'>لا توجد تنبيهات</div>"
        
    # توليد وضخ الألواح الجانبية التفاعلية بنظام Shiny الفاخر
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
