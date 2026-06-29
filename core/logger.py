import logging
import sys
from pathlib import Path

# إعداد مجلد السجلات
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """
    إنشاء Logger مخصص لكل وحدة (Module) في المشروع.
    يقوم بالتسجيل في ملف وفي الكونسول بنفس الوقت.
    """
    logger = logging.getLogger(name)
    
    # منع إضافة معالجات (Handlers) متعددة إذا تم استدعاء الدالة أكثر من مرة
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # تنسيق السجل: [التاريخ] [المستوى] اسم_الملف: الرسالة
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Handler للملف (لتخزين الأخطاء والتنبيهات)
        fh = logging.FileHandler(LOG_DIR / f"{name}.log", encoding="utf-8")
        fh.setFormatter(formatter)
        
        # Handler للـ Console (للمتابعة المباشرة أثناء التطوير)
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger
