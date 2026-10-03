# استفاده از نسخه سبک پایتون
FROM python:3.11-slim

# تنظیم پوشه کاری داخل کانتینر
WORKDIR /app

# کپی کردن فایل نیازمندی‌ها و نصب آن‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن کل فایل‌های پروژه به داخل کانتینر
COPY . .

# دستوری که برنامه را اجرا می‌کند (روی پورت 8000)
CMD ["python", "run.py"]