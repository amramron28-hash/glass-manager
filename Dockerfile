# استخدام بيئة بايثون رسمية ومستقرة
FROM python:3.10-slim

# إعداد دليل العمل الأساسي داخل السيرفر
WORKDIR /code

# تثبيت الحزم والمكتبات المطلوبة باستخدام requirements.txt لضمان التوافق والإصدارات الصحيحة
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات مشروعك الذكية (workflows, logic_engine...) إلى السيرفر
COPY . .

# إنشاء مجلدات السجلات والبيانات المحلية مسبقاً لتجنب أخطاء الصلاحيات لاحقاً
RUN mkdir -p /code/logs /code/www && \
    chown -R 1000:1000 /code

# إنشاء مستخدم غير جذري لتشغيل التطبيق بأمان (أفضل من chmod 777)
RUN useradd -m -u 1000 appuser
USER appuser

ENV HOME=/home/appuser \
    PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# المنفذ الخاص الذي يقرأه موقع Hugging Face لتشغيل التطبيق
EXPOSE 7860

# الأمر النهائي والمسؤول عن تشغيل تطبيق Shiny فائق السرعة
CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
