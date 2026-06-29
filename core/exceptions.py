class AppError(Exception):
    """الاستثناء الأساسي للتطبيق"""
    pass

class DatabaseError(AppError):
    """يُطلق عند فشل الاتصال بـ Supabase أو قراءة الملفات المحلية"""
    pass

class SearchError(AppError):
    """يُطلق عند حدوث مشكلة في فهرسة أو بحث الإكمال التلقائي"""
    pass

class PlanError(AppError):
    """يُطلق عند فشل منطق المطابقة الفنية (Plan 2/3)"""
    pass
