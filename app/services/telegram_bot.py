import asyncio
import os
import base64
import tempfile
from aiogram import Bot, Dispatcher, types
from app.core.config import settings
from app.db.database import SessionLocal
from app.db import crud
from app.services.formatter import format_for_whatsapp
from app.services.whatsapp_api import send_text_message, send_media_message

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

sync_lock = asyncio.Lock()
pending_updates = []
batch_timer_task = None
# زمان انتظار بیشتر برای اطمینان از رسیدن ویدیوهای سنگین‌تر به تلگرام
DEBOUNCE_TIME = 8.0  

async def download_and_encode(file_id: str) -> str:
    file = await bot.get_file(file_id)
    file_path = file.file_path
    fd, temp_path = tempfile.mkstemp()
    try:
        await bot.download_file(file_path, temp_path)
        with open(temp_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode("utf-8")
        ext = file_path.split('.')[-1].lower()
        mime_type = "audio/mpeg"
        if ext in ["mp4", "webm", "mov"]: mime_type = "video/mp4"
        elif ext in ["ogg", "oga"]: mime_type = "audio/ogg"
        elif ext in ["mp3"]: mime_type = "audio/mpeg"
        elif ext in ["m4a", "aac"]: mime_type = "audio/mp4"
        elif ext in ["wav"]: mime_type = "audio/wav"
        return f"data:{mime_type};base64,{encoded_string}"
    finally:
        os.close(fd)
        os.remove(temp_path)

def is_valid_source(sys_settings, message: types.Message) -> bool:
    if not sys_settings.is_sync_active:
        return False
    target_channel = sys_settings.telegram_channel_id
    if target_channel:
        target_channel = target_channel.replace("@", "")
        if message.chat.username != target_channel and str(message.chat.id) != sys_settings.telegram_channel_id:
            return False
    return True

@dp.channel_post()
async def handle_all_posts(message: types.Message):
    global batch_timer_task, pending_updates
    
    # ۱. جلوگیری از ورود پیام تکراری به صف پردازش در حین زمان انتظار (Debounce)
    if any(msg.message_id == message.message_id for msg in pending_updates):
        return
         
    db = SessionLocal()
    sys_settings = crud.get_settings(db)
    is_valid = is_valid_source(sys_settings, message)
    
    # ۲. بررسی دیتابیس برای اطمینان از اینکه پیام قبلاً با موفقیت ارسال نشده باشد
    is_processed = crud.is_message_processed(db, str(message.message_id))
    
    db.close()
         
    # اگر منبع معتبر نیست یا پیام قبلاً پردازش شده است، عملیات متوقف شود
    if not is_valid or is_processed:
        return
         
    pending_updates.append(message)
         
    if batch_timer_task:
        batch_timer_task.cancel()
    batch_timer_task = asyncio.create_task(trigger_batch_processing())

async def trigger_batch_processing():
    try:
        await asyncio.sleep(DEBOUNCE_TIME)
    except asyncio.CancelledError:
        return
        
    asyncio.create_task(execute_batch())

async def execute_batch():
    global pending_updates
    
    async with sync_lock:
        if not pending_updates:
            return
            
        current_batch = pending_updates.copy()
        pending_updates.clear()
        
        current_batch.sort(key=lambda m: m.message_id)
        
        grouped_tasks = []
        groups = {}
        
        for msg in current_batch:
            if msg.media_group_id:
                if msg.media_group_id not in groups:
                    groups[msg.media_group_id] = []
                    grouped_tasks.append({"type": "album", "items": groups[msg.media_group_id]})
                groups[msg.media_group_id].append(msg)
            else:
                grouped_tasks.append({"type": "single", "items": [msg]})
                
        db = SessionLocal()
        sys_settings = crud.get_settings(db)
        
        if not sys_settings.whapi_token or not sys_settings.whatsapp_channel_id:
            db.close()
            return
            
        for task in grouped_tasks:
            if task["type"] == "single":
                await _process_single(task["items"][0], sys_settings, db)
            elif task["type"] == "album":
                await _process_album(task["items"], sys_settings, db)
                
        db.close()

# --- تابع جدید: ترمز دستی سیستم ---
async def apply_smart_delay(media_type: str):
    if media_type == "video":
        await asyncio.sleep(8.0) # ۸ ثانیه توقف کامل برای پردازش ویدیو در واتس‌اپ
    elif media_type == "document":
        await asyncio.sleep(5.0)
    else:
        await asyncio.sleep(2.0) # ۲ ثانیه توقف برای عکس‌ها

async def _process_single(message: types.Message, sys_settings, db):
    success, error = False, None
    try:
        if message.text:
            formatted_text = format_for_whatsapp(message.text, is_title=True, settings=sys_settings)
            success, error = await send_text_message(sys_settings.whapi_token, sys_settings.whatsapp_channel_id, formatted_text)
            if success:
                await asyncio.sleep(1.0)
                
        elif message.photo or message.video or message.audio or message.voice or message.document:
            raw_caption = message.caption or ""
            formatted_caption = format_for_whatsapp(raw_caption, is_title=False, settings=sys_settings)
            
            long_text_to_send_after = None
            if len(formatted_caption) > 1024:
                # واتس‌اپ محدودیت ۱۰۲۴ کاراکتری برای کپشن دارد
                split_point = 980
                long_text_to_send_after = "ادامه پست قبل:\n\n" + formatted_caption[split_point:]
                formatted_caption = formatted_caption[:split_point] + "...\n👇 (ادامه در پیام بعد)"
            
            file_id, media_type, filename = None, "image", None
            
            if message.photo: 
                file_id = message.photo[-1].file_id
            elif message.video: 
                file_id = message.video.file_id
                media_type = "video"
            elif message.audio: 
                file_id = message.audio.file_id
                media_type, filename = "document", message.audio.file_name or "audio_track.mp3"
            elif message.voice: 
                file_id = message.voice.file_id
                media_type, filename = "document", "voice_note.ogg"
            elif message.document:
                file_id = message.document.file_id
                media_type, filename = "document", message.document.file_name or "document.file"
            
            if file_id:
                base64_data = await download_and_encode(file_id)
                success, error = await send_media_message(
                    sys_settings.whapi_token, sys_settings.whatsapp_channel_id, 
                    base64_data, formatted_caption, media_type, filename
                )
                
                if success:
                    await apply_smart_delay(media_type) # اعمال ترمز دستی
                
                if success and long_text_to_send_after:
                    success, error = await send_text_message(
                        sys_settings.whapi_token, sys_settings.whatsapp_channel_id, long_text_to_send_after
                    )
                    if success:
                        await asyncio.sleep(1.0)
                    
    except Exception as e:
        error = f"Single Media Error: {str(e)}"
    crud.create_sync_log(db, str(message.message_id), "success" if success else "error", error)

async def _process_album(messages: list, sys_settings, db):
    caption = next((msg.caption for msg in messages if msg.caption), "")
    formatted_caption = format_for_whatsapp(caption, is_title=False, settings=sys_settings) if caption else ""
    
    long_text_to_send_after = None
    if len(formatted_caption) > 1024:
        # واتس‌اپ محدودیت ۱۰۲۴ کاراکتری برای کپشن دارد
        split_point = 980
        long_text_to_send_after = "ادامه پست قبل:\n\n" + formatted_caption[split_point:]
        formatted_caption = formatted_caption[:split_point] + "...\n👇 (ادامه در پیام بعد)"
        
    for i, msg in enumerate(messages):
        file_id, media_type = None, "image"
        if msg.photo: 
            file_id = msg.photo[-1].file_id
        elif msg.video:
            file_id, media_type = msg.video.file_id, "video"
        elif msg.document:
            file_id, media_type = msg.document.file_id, "document"
            
        if file_id:
            try:
                base64_data = await download_and_encode(file_id)
                current_caption = formatted_caption if i == len(messages) - 1 else ""
                success, error = await send_media_message(
                    sys_settings.whapi_token, sys_settings.whatsapp_channel_id, 
                    base64_data, current_caption, media_type
                )
                crud.create_sync_log(db, str(msg.message_id), "success" if success else "error", error)
                
                if success:
                    await apply_smart_delay(media_type) # اعمال ترمز دستی در آلبوم‌ها
                    
            except Exception as e:
                crud.create_sync_log(db, str(msg.message_id), "error", f"Album Media Error: {str(e)}")
                
    if long_text_to_send_after:
        try:
            success, _ = await send_text_message(
                sys_settings.whapi_token, sys_settings.whatsapp_channel_id, long_text_to_send_after
            )
            if success:
                await asyncio.sleep(1.0)
        except Exception as e:
            pass