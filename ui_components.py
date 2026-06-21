import os
import base64
from html import escape
from shiny import ui

_bg_cache = None

# ==============================================================================
# 🎨 الخلفية وحقن ملف الـ CSS الأصلي الخاص بك ليعمل بكفاءة داخل Shiny
# ==============================================================================
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
    
    /* 🎯 رفع شريط البحث للثلث العلوي */
    .container-fluid {{
        padding-top: 35px !important; 
    }}

    /* 🎯 العربية أقصى اليمين: عناوين فئات التوافق ملتصقة باليمين بالكامل */
    .section-title {{
        font-size: 20px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        margin-top: 25px !important;
        margin-bottom: 12px !important;
        text-align: right !important;
        direction: rtl !important;
    }}

    /* 🎯 هندسة كروت النيون الفاخرة ثنائية اللغة (تطبيق كود الـ CSS الأصلي الخاص بك ليفصل الكروت) */
    .ammar-flat-card, .flat-warning-card {{
        padding: 14px 18px !important;
        margin-bottom: 14px !important; /* مسافة فاصلة عمودية صارمة تمنع التكدس نهائياً */
        border-radius: 12px !important;
        display: flex !important;
        align-items: center !important;
        /* التوزيع الذكي الأصلي: الاسم الإنجليزي أقصى اليسار وصندوق الصورة أقصى اليمين */
        justify-content: space-between !important; 
        direction: ltr !important; /* لضمان دفع المحتوى الإنجليزي لليسار بصورة طبيعية */
        width: 100% !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.35) !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease;
    }}
    .ammar-flat-card:hover, .flat-warning-card:hover {{
        transform: translateY(-2px);
    }}

    /* الألوان والحدود النيونية الصارمة من ملفك */
    .flat-exact {{ background: linear-gradient(135deg, #0d1f13, #07120b) !important; border: 2px solid #2ecc71 !important; }}
    .flat-plus {{ background: linear-gradient(135deg, #0b1a33, #060e1c) !important; border: 2px solid #3498db !important; }}
    .flat-minus {{ background: linear-gradient(135deg, #2b1807, #140b03) !important; border: 2px solid #e67e22 !important; }}
    .flat-warning-card {{ background: linear-gradient(135deg, #26090b, #120405) !important; border: 2px solid #ff4a5a !important; }}

    /* 🎯 الإنجليزية أقصى اليسار: أسماء الهواتف والبراندات ملتصقة أقصى اليسار تماماً */
    .flat-phone-text {{ 
        color: #ffffff !important; 
        font-size: 21px !important; 
        font-weight: 800 !important;
        text-align: left !important;
        display: block !important;
        margin: 0 !important;
    }}

    /* 🎯 حجز مساحة لصور الهواتف تلقائياً: مربع نيون فخم أقصى اليمين في الجهة المقابلة للاسم تماماً */
    .image-placeholder-box {{
        width: 55px !important;
        height: 55px !important;
        min-width: 55px !important;
        border-radius: 8px !important;
        background-color: rgba(10, 14, 23, 0.8) !important;
        border: 1px dashed rgba(0, 191, 255, 0.4) !important;
        box-shadow: inset 0px 0px 8px rgba(0, 191, 255, 0.15) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
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

# ==============================================================================
# 📋 بطاقة الإحداثيات الفنية للموديل الفعلي
# ==============================================================================
def draw_technical_coords(size_grp, panel_grp, sensor_grp, real_name=None):
    return f"""
    <div class="glass-window-card" style="background:rgba(15,23,42,.7); margin-top:15px; border: 1px solid #00bfff; box-shadow: 0 0 10px rgba(0,191,255,0.2); direction:rtl;">
        <div style="text-align:right; font-size:16px; line-height:1.7; color:white; width:100%;">
            {"🔍 <b>الموديل المتطابق:</b> " + escape(real_name) + "<br>" if real_name else ""}
            📏 <b>المقاس:</b> {escape(str(size_grp))} <br>
            📺 <b>نوع الشاشة:</b> {escape(str(panel_grp))} <br>
            👁️ <b>مستشعر التقارب:</b> {escape(str(sensor_grp))}
        </div>
    </div>
    """

# ==============================================================================
# 📱 بطاقات النتائج المتقطعة والمنفصلة كلياً بنظام نيون هندسة اللغات الأصلي الخاص بك
# ==============================================================================
def draw_neon_section(models_list, title="هواتف مطابقة تماماً في الأبعاد والقص (Exact 0.00):", color_hex="#2ecc71", badge_icon="🟢"):
    if not models_list:
        return ""

    html_cards = []
    # 🎯 العربية أقصى اليمين كعنوان فئة رئيسية ملتصق تماماً باليمين كما بملف الـ CSS
    html_cards.append(f"""
    <div class="section-title">
        <span style="color:{color_hex}; margin-left: 6px;">{badge_icon}</span>{title}
    </div>
    <div style="display: flex; flex-direction: column; width:100%; box-sizing: border-box;">
    """)

    # بناء كروت منفصلة ومتقطعة باستخدام كلاسات الـ CSS الصارمة لملف التنسيق الأصلي الخاص بك
    for model in models_list:
        html_cards.append(f"""
        <div class="ammar-flat-card flat-exact">
            <!-- 🎯 الإنجليزية أقصى اليسار تماماً وبخط عريض وبولد عالي الوضوح وحجم كبير -->
            <div class="flat-phone-text">{escape(model)}</div>
            
            <!-- 🎯 حجز مساحة لصور الهواتف تلقائياً أقصى اليمين في الجهة المقابلة للاسم تماماً -->
            <div class="image-placeholder-box">
                <span style="color: rgba(0, 191, 255, 0.4); font-size: 11px; font-weight: bold;">🖼️</span>
            </div>
        </div>
        """)
        
    html_cards.append("</div>")
    return "\n".join(html_cards)

# ==============================================================================
# 🛠️ لوحة التحكم الجانبية التفاعلية لـ Shiny
# ==============================================================================
def draw_control_panel(notifications=None, total_models=0, empty_groups_count=0):
    notifications = notifications or []
    if notifications:
        notif_html = "".join([f"<div style='color:#ffc107; margin-bottom:5px;'>⚠️ {escape(n)}</div>" for n in notifications])
    else:
        notif_html = "<div style='color:#aaa; font-style:italic;'>لا توجد تنبيهات</div>"
        
    panel_ui = ui.sidebar(
        ui.HTML('<h3 class="sidebar-title">🛠️ لوحة التحكم</h3>'),
        ui.accordion(
            ui.accordion_panel("🔔 الإشعارات", ui.HTML(notif_html)),
            ui.accordion_panel("⚙️ الإعدادات", ui.input_checkbox("silent_monitor_checkbox", "تفعيل المراقب الصامت", value=True)),
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
