import requests

TOKEN = "YOUR_WHAPI_TOKEN"
TARGET_CHANNEL_NAME = "your_channel_name"

# استفاده از اندپوینت اختصاصی کانال‌ها (خبرنامه‌ها) بر اساس داکیومنت
url = "https://gate.whapi.cloud/newsletters"

headers = {
    "accept": "application/json",
    "authorization": f"Bearer {TOKEN}"
}

print(f"🔍 در حال جستجوی کانال: '{TARGET_CHANNEL_NAME}' ...\n")

response = requests.get(url, headers=headers)

if response.status_code == 200:
    # دریافت لیست کانال‌ها
    newsletters = response.json().get('newsletters', [])
    found = False
    
    for nl in newsletters:
        name = nl.get('name', '')
        nl_id = nl.get('id', '')
        
        if name == TARGET_CHANNEL_NAME:
            print("✅ کانال با موفقیت پیدا شد!")
            print("-" * 40)
            print(f"🏷️ نام کانال: {name}")
            print(f"🆔 آیدی کانال: {nl_id}")
            print("-" * 40)
            found = True
            break
            
    if not found:
        print(f"❌ کانال پیدا نشد. خروجی خام سرور برای بررسی دقیق‌تر:")
        print(response.text)
else:
    print(f"❌ خطا در ارتباط با سرور Whapi. کد خطا: {response.status_code}")
    print(response.text)