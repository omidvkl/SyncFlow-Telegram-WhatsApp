import httpx
import logging

# تنظیمات لاگر برای ثبت خطاهای ارتباطی با API
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WHAPI_BASE_URL = "https://gate.whapi.cloud/messages"

async def send_text_message(token: str, channel_id: str, text: str) -> bool:
    """
    ارسال پیام متنی به کانال واتس‌اپ
    """
    url = f"{WHAPI_BASE_URL}/text"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "typing_time": 0,
        "to": channel_id,
        "body": text
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=15.0)
            response.raise_for_status()
            return True, None
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP Error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Request Failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

async def send_media_message(token: str, channel_id: str, media_url: str, caption: str, media_type: str = "image", filename: str = None) -> bool:
    url = f"{WHAPI_BASE_URL}/{media_type}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": channel_id,
        "media": media_url
    }

    # اضافه کردن کپشن
    if caption:
        payload["caption"] = caption
        
    # اضافه کردن نام فایل (این همون چیزیه که جا مونده بود و ارور می‌داد!)
    if filename:
        payload["filename"] = filename

    async with httpx.AsyncClient() as client:
        try:
            # تایم‌اوت رو بالاتر بردیم (60 ثانیه) تا ویدیوهای سنگین هم راحت ارسال بشن
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            return True, None
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP Error {media_type}: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Media Error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg