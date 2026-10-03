from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime

def get_settings(db: Session):
    """
    دریافت تنظیمات فعلی سیستم. اگر وجود نداشت یک رکورد خالی ایجاد می‌کند.
    """
    settings = db.query(models.SystemSettings).first()
    if not settings:
        settings = models.SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_settings(db: Session, update_data: dict):
    """
    بروزرسانی توکن‌ها و لینک‌های فوتر واتس‌اپ
    """
    settings = get_settings(db)
    for key, value in update_data.items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings

def create_sync_log(db: Session, telegram_message_id: str, status: str, error_details: str = None):
    """
    ثبت یک لاگ جدید برای تقویم و گزارشات پنل
    """
    db_log = models.SyncLog(
        telegram_message_id=telegram_message_id,
        status=status,
        error_details=error_details,
        created_at=datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs(db: Session, skip: int = 0, limit: int = 100):
    """
    دریافت لیست لاگ‌ها (برای نمایش در پنل ادمین)
    """
    return db.query(models.SyncLog).order_by(models.SyncLog.created_at.desc()).offset(skip).limit(limit).all()

def is_message_processed(db: Session, telegram_message_id: str) -> bool:
    """
    بررسی می‌کند که آیا این پیام قبلاً با موفقیت پردازش و در دیتابیس ثبت شده است یا خیر
    """
    return db.query(models.SyncLog).filter(
        models.SyncLog.telegram_message_id == telegram_message_id,
        models.SyncLog.status == "success"
    ).first() is not None