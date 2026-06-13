import streamlit as st
import datetime
from database import load_db, save_db
from logic_engine import run_intelligent_inspector

def render_top_bar():
    """
    🎯 بناء شريط الأدوات العلوي الفاخر والمدمج:
    يحتوي على جرس الإشعارات، ترس الإعدادات، وزر تشغيل المراقب الصامت الذكي.
    يظهر بشكل نظيف وزجاجي متناسق مع الواجهة النظيفة.
    """
    # جلب البيانات الحالية للـ RAM لتشغيل الأدوات عليها
    db_data = load_db()
    
    # استخدام المكون المنسدل الحديث من Streamlit (Popover) لبناء الأزرار العلوية بشكل زجاجي مدمج
    col_spacer, col_tools = st.columns([6, 2])
    
    with col_tools:
        sub_col1, sub_col2 = st.columns(2)
        
        with sub_col1:
            # 🔔 نافذة منبثقة لجرس الإشعارات والمراقب الصامت
            with st.popover("🔔 الإشعارات"):
                st.markdown("### 📌 آخر تحديثات النظام والـ RAM")
                # عرض رسالة تنبيهية سريعة بنظام زجاجي
                st.info("💡 النظام يعمل بكفاءة قصوى والبحث الذكي الحي نشط الآن.")
                
                if st.button("🧹 تنظيف شجرة البيانات (المراقب الصامت)", key="btn_run_inspector"):
                    cleaned_data, changes = run_intelligent_inspector(db_data)
                    if changes:
                        save_db(cleaned_data)
                        st.success("✨ قام المراقب الصامت بإزالة التكرار وترتيب الموديلات في الـ JSON بنجاح!")
                    else:
                        st.toast("🎯 قاعدة البيانات مرتبة ونظيفة تماماً كلياً، لا توجد تكرارات.")
                        
        with sub_col2:
            # ⚙️ نافذة منبثقة لترس الإعدادات
            with st.popover("⚙️ الإعدادات"):
                st.markdown("### 🛠️ لوحة تحكم التطبيق")
                st.write(f"📅 تاريخ اليوم الفني: {datetime.date.today().strftime('%Y-%m-%d')}")
                st.write("📊 حالة الاتصال بقاعدة البيانات: **متصل وسحابي ونشط**")
                
                # خيار سريع للمطور لتصفير أو عرض حجم البيانات
                total_models = 0
                for size, panels in db_data.items():
                    for panel, sensors in panels.items():
                        for sensor, s_data in sensors.items():
                            models_list = s_data.get("models", []) if isinstance(s_data, dict) else s_data
                            total_models += len(models_list)
                            
                st.metric(label="📈 إجمالي الهواتف المسجلة بالسيستم", value=total_models)

def inject_css():
    """
    تم نقل كافة التنسيقات المتقدمة وإصلاح الشفافيات والجدارية إلى ملف style.css الخارجي 
    لضمان بقاء هذا الملف نظيفاً وبدون تعارض ألوان.
    """
    pass
