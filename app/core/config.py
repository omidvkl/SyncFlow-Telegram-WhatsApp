from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SyncFlow Telegram to WhatsApp"
    SECRET_KEY: str = "fallback_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 
    
    # مقادیر زیر صرفاً پیش‌فرض (Fallback) هستند.
    # Pydantic به صورت خودکار مقادیر قوی‌تر را از فایل .env در داکر می‌خواند و جایگزین می‌کند.
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    
    DATABASE_URL: str = "sqlite:///./syncflow.db"
    
    TELEGRAM_BOT_TOKEN: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()