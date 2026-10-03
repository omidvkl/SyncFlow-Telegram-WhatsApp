# SyncFlow: Telegram to WhatsApp Channel Synchronizer 🔄

<div align="center">
  <a href="#english">🇬🇧 English</a> | <a href="#فارسی-persian">🇮🇷 فارسی</a>
</div>

---

<div id="english">

## 🇬🇧 English

**SyncFlow** is a powerful, automated bridge designed to seamlessly forward messages, media, and albums from a Telegram Channel to a WhatsApp Channel in real-time. Equipped with a sleek web-based Admin Panel, it allows you to easily configure settings, monitor sync logs, and manage API integrations on the fly.

### ✨ Features
* **Real-time Synchronization:** Instantly forwards text, images, videos, audio, and documents.
* **Smart Album Handling:** Automatically groups and forwards Telegram media albums as cohesive messages on WhatsApp.
* **Admin Dashboard:** A beautiful, responsive web interface built with FastAPI, Jinja2, and TailwindCSS for monitoring logs and toggling the sync process.
* **Format Preservation:** Strips unwanted Telegram footers and applies clean formatting (with custom footer links) for WhatsApp.
* **Docker Ready:** Easy deployment using `docker-compose`.
* **Secure:** Password-protected dashboard with JWT authentication and brute-force protection (Captcha).

### 🛠️ Tech Stack
* **Backend:** Python 3.11, FastAPI, Aiogram 3 (Telegram Bot API)
* **WhatsApp API:** Whapi.cloud
* **Database:** SQLite (SQLAlchemy ORM)
* **Frontend:** Jinja2 Templates, TailwindCSS

### 🚀 Installation & Deployment

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/syncflow.git
cd syncflow
```

#### 2. Configuration
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```
*Edit the `.env` file to add your `TELEGRAM_BOT_TOKEN`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and a strong `SECRET_KEY`.*

#### 3. Run with Docker (Recommended)
```bash
docker-compose up -d --build
```
The application will start, and the Admin Panel will be available at `http://localhost:8001`.

#### 4. Run Locally (Without Docker)
```bash
pip install -r requirements.txt
python run.py
```

### 🔐 Security Note
For production deployment, always run the FastAPI web server behind a reverse proxy (like Nginx) equipped with SSL/TLS (HTTPS). Never expose the raw HTTP port to the public web.

</div>

---

<div id="فارسی-persian" dir="rtl">

## 🇮🇷 فارسی

**پروژه SyncFlow** یک ربات و ابزار قدرتمند برای همگام‌سازی و انتقال خودکار پیام‌ها از کانال تلگرام به کانال واتس‌اپ است. این سیستم به همراه یک پنل مدیریت تحت وب زیبا ارائه می‌شود که به شما اجازه می‌دهد وضعیت ربات را کنترل کرده، لاگ‌ها را بررسی کنید و تنظیمات API را به راحتی تغییر دهید.

### ✨ امکانات و ویژگی‌ها
* **همگام‌سازی در لحظه (Real-time):** انتقال سریع متن، عکس، ویدیو، صدا و فایل.
* **پشتیبانی از آلبوم (Album):** تشخیص و ارسال گروهیِ مدیاهای تلگرام به شکل یکپارچه در واتس‌اپ.
* **داشبورد مدیریت تحت وب:** رابط کاربری مدرن طراحی شده با FastAPI و TailwindCSS برای مشاهده لاگ‌های موفق/ناموفق و تغییر تنظیمات.
* **مدیریت فرمت متن:** حذف فوترها و لینک‌های اختصاصی تلگرام و جایگزین کردن آن‌ها با فوتر و لینک‌های تنظیم‌شده برای واتس‌اپ (پاک‌سازی هوشمند متن).
* **اجرای آسان با Docker:** نصب و راه‌اندازی سریع روی سرور با `docker-compose`.
* **امنیت بالا:** ورود دو مرحله‌ای به پنل ادمین همراه با سیستم کپچا (Captcha) و احراز هویت با توکن‌های JWT.

### 🛠️ تکنولوژی‌های استفاده شده
* **بک‌اند:** Python 3.11, FastAPI, Aiogram 3
* **رابط واتس‌اپ:** Whapi.cloud API
* **پایگاه داده:** SQLite (SQLAlchemy)
* **فرانت‌اند:** Jinja2, TailwindCSS

### 🚀 نحوه نصب و اجرا

#### ۱. دریافت پروژه
```bash
git clone https://github.com/yourusername/syncflow.git
cd syncflow
```

#### ۲. تنظیمات اولیه
فایل نمونه متغیرهای محیطی را کپی کرده و اطلاعات خود را وارد کنید:
```bash
cp .env.example .env
```
*فایل `.env` را باز کرده و توکن ربات تلگرام، نام کاربری و رمز عبور ادمین، و یک `SECRET_KEY` امن را وارد کنید.*

#### ۳. اجرا با داکر (روش پیشنهادی)
```bash
docker-compose up -d --build
```
پروژه اجرا شده و پنل ادمین روی آدرس `http://localhost:8001` در دسترس خواهد بود.

#### ۴. اجرای محلی (بدون داکر)
```bash
pip install -r requirements.txt
python run.py
```

### 🔐 نکات امنیتی دیپلوی
برای اجرای پروژه در محیط عملیاتی (Production)، حتماً پنل مدیریت را پشت یک Reverse Proxy مانند Nginx قرار دهید و از گواهینامه SSL (مانند Let's Encrypt) استفاده کنید تا اطلاعات لاگین شما در بستر اینترنت رمزنگاری شوند.

</div>