import asyncio
import uvicorn
from app.main import app
from app.services.telegram_bot import dp, bot

async def start_fastapi():
    """اجرای سرور وب FastAPI"""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def start_bot():
    """اجرای ربات تلگرام با Aiogram"""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

async def main():
    """اجرای همزمان هر دو سرویس"""
    await asyncio.gather(
        start_fastapi(),
        start_bot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot and Web Server stopped.")