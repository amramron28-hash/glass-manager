import os
import requests
from html import escape
from database import load_db, save_db
from logic_engine import find_model_coords, get_compatibles_strict
from ui_components import draw_technical_coords, draw_neon_section

def local_check_existing_size_group(db, target_size, target_panel):
    """فحص وتدقيق مجموعات الأبعاد والشاشات المسجلة"""
    matched_models = []
    if target_size in db and target_panel in db[target_size]:
        for sensor, s_data in db[target_size][target_panel].items():
            models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
            for m in models_list:
                matched_models.append(m)
    return matched_models

def ai_background_global_verify(phone_name):
    """التحقق الذكي عبر الـ API العالمي في الخلفية"""
    try:
        url = f"https://vercel.app{requests.utils.quote(phone_name)}"
        res = requests.get(url, timeout=1.5).json()
        if res and "specs" in res:
            return {
                "size": str(res["specs"].get("display_size", "")),
                "panel": str(res["specs"].get("display_type", "")),
                "sensor": str(res["specs"].get("proximity_type", ""))
            }
    except:
        pass
    return None

def append_to_models_index(phone_name):
    """ضخ الاسم الجديد تلقائياً في ملف المساعدة الستاري لتسريع المرات القادمة"""
    INDEX_FILE = "models_index.txt"
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            current_models = [line.strip() for line in f if line.strip()]
        if phone_name not in current_models:
            with open(INDEX_FILE, "a", encoding="utf-8") as f:
                f.write(f"{phone_name}\n")

def run_system_workflows(phone, db_data, suggestions):
    """المحرك المركزي لإدارة الخطط الثلاث بالتناغم الكامل لبيئة Shiny"""
    size_str, panel, sensor, real_name = find_model_coords(db_data, phone) if phone else (None, None, None, None)
    is_exact_match = True if real_name and phone.lower() == real_name.lower() else False
    
    # مصفوفة لتجميع مخرجات الواجهة كـ HTML بدلاً من st.markdown
    html_output = []

    if is_exact_match:
        # توليد كود الـ HTML الخاص بالإحداثيات الفنية عند التطابق التام
        coords_html = draw_technical_coords(size_str, panel, sensor, real_name)
        if coords_html:
            html_output.append(str(coords_html))
            
        # جلب الهواتف المتوافقة
        compatibles = get_compatibles_strict(db_data, size_str, panel, sensor, real_name)
        compat_html = draw_neon_section(compatibles)
        if compat_html:
            html_output.append(str(compat_html))
            
    elif phone:
        # في حال عدم التطابق التام (البحث الجاري أو عدم الوجود)
        html_output.append(f"""
            <div style='padding: 15px; background: rgba(255, 165, 0, 0.1); border-left: 4px solid #ffa500; border-radius: 4px; margin-top: 15px;'>
                <span style='color: #ffa500; font-weight: bold;'>🔍 جاري فحص ومطابقة الموديل المستهدف:</span> {escape(phone)}
            </div>
        """)

    # إرجاع مخرجات الواجهة مجمعة ليتم حقنها مباشرة في الـ app.py
    return "\n".join(html_output)
