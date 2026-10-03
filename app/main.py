from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.api import web_routes
from app.db.database import engine, Base
from app.core.config import settings
import os

# ایجاد خودکار جداول دیتابیس در زمان اجرای برنامه
Base.metadata.create_all(bind=engine)

# غیرفعال کردن مسیرهای داکیومنت پیش‌فرض FastAPI برای امنیت بیشتر
app = FastAPI(title="SyncFlow Bot Panel", docs_url=None, redoc_url=None, openapi_url=None)

# اضافه شدن Session برای مدیریت ساخت و بررسی کپچای ریاضی
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# اعمال هدرهای امنیتی ضد ایندکس برای تمامی صفحات و ریکوئست‌ها
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# ایجاد پوشه‌های استاتیک و تمپلیت
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# متصل کردن روت‌های مربوط به پنل ادمین
app.include_router(web_routes.router)