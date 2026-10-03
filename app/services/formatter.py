import re

def remove_emojis(text: str) -> str:
    # الگوی جامع‌تر برای حذف تمام ایموجی‌های قدیمی و جدید (بدون آسیب به هشتگ و لینک)
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # Emoticons
        "\U0001f300-\U0001f5ff"  # Misc Symbols and Pictographs
        "\U0001f680-\U0001f6ff"  # Transport and Map
        "\U0001f1e0-\U0001f1ff"  # Regional indicator symbols (Flags)
        "\u2600-\u26FF"          # Misc symbols
        "\u2700-\u27BF"          # Dingbats
        "\u2B50"                 # Star
        "\U0001f900-\U0001f9ff"  # Supplemental Symbols (Newer emojis)
        "\U0001fa70-\U0001faff"  # Extended emojis
        "]+", flags=re.UNICODE)
    cleaned = emoji_pattern.sub(r'', text)
    return cleaned

def clean_footer(text: str) -> str:
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # برش متن به محض رسیدن به امضای کانال یا لینک‌های فوتر تلگرام
        if '@your_channel_name' in line or '   |' in line or '  |' in line or (' ' in line and 'ID' in line):
            break 
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

def format_for_whatsapp(text: str, is_title: bool, settings) -> str:
    if not text:
        return ""
        
    cleaned_text = clean_footer(text)
    cleaned_text = remove_emojis(cleaned_text)
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text).strip()
    
    if not cleaned_text:
        return ""
    
    lines = cleaned_text.split('\n')
    
    formatted_lines = []
    first_paragraph = True
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
            
        if not first_paragraph:
            formatted_lines.append("") 
            # استیکر مخصوص پاراگراف‌ها
            formatted_lines.append(f"🔻  {stripped_line}")
        else:
            # استیکر مخصوص عنوان اصلی
            formatted_lines.append(f"🔴 {stripped_line}")
            first_paragraph = False
            
    final_text = '\n'.join(formatted_lines)
    
    # اضافه کردن لینک‌های تمیز و اختصاصی از تنظیمات پنل
    footer_links = []
    if settings.link1_title and settings.link1_url:
        footer_links.append(f"{settings.link1_title}\n{settings.link1_url}")
    if settings.link2_title and settings.link2_url:
        footer_links.append(f"{settings.link2_title}\n{settings.link2_url}")
    if settings.link3_title and settings.link3_url:
        footer_links.append(f"{settings.link3_title}\n{settings.link3_url}")
    if settings.link4_title and settings.link4_url:
        footer_links.append(f"{settings.link4_title}\n{settings.link4_url}")
        
    if footer_links:
        footer_str = '\n\n'.join(footer_links)
        final_text = f"{final_text}\n\n{footer_str}"
        
    return final_text.strip()