# استخدام بيئة بايثون رسمية ومستقرة
FROM python:3.10-slim

# إعداد دليل العمل الأساسي داخل السيرفر
WORKDIR /code

# تثبيت الحزم والمكتبات المطلوبة لتطبيقك مباشرة في السحاب
RUN pip install --no-cache-dir --upgrade shiny supabase pandas python-dotenv requests

# نسخ باقي ملفات مشروعك الذكية (workflows, logic_engine...) إلى السيرفر
COPY . .

# منح صلاحيات كاملة للمجلد لضمان سلاسة قراءة وتعديل الملفات
RUN chmod -R 777 /code

# منح صلاحيات كاملة للمستخدم الافتراضي لتشغيل النظام بأمان وضمان عدم توقفه
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# المنفذ الخاص الذي يقرأه موقع Hugging Face لتشغيل التطبيق
EXPOSE 7860

# الأمر النهائي والمسؤول عن تشغيل تطبيق Shiny فائق السرعة
CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
