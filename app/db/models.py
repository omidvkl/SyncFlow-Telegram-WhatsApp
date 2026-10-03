from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from app.db.database import Base

class SystemSettings(Base):
    """
    جدول ذخیره تنظیمات کارفرما شامل توکن‌ها، کانال‌ها و وضعیت ربات
    """
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # تنظیمات API و کانال‌ها
    whapi_token = Column(String, nullable=True)
    whatsapp_channel_id = Column(String, nullable=True)
    telegram_channel_id = Column(String, nullable=True)
    is_sync_active = Column(Boolean, default=True) # سوییچ فعال/غیرفعال بودن ربات
    
    # مدیریت لینک‌های فوتر واتس‌اپ
    link1_title = Column(String, nullable=True)
    link1_url = Column(String, nullable=True)
    link2_title = Column(String, nullable=True)
    link2_url = Column(String, nullable=True)
    link3_title = Column(String, nullable=True)
    link3_url = Column(String, nullable=True)
    link4_title = Column(String, nullable=True)
    link4_url = Column(String, nullable=True)

class SyncLog(Base):
    """
    جدول ثبت تاریخچه انتقال‌ها برای نمایش در داشبورد و آمارگیری
    """
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    telegram_message_id = Column(String, index=True)
    status = Column(String)  # مقدار 'success' یا 'error'
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)