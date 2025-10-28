import pytesseract
from PIL import Image
import re


def analyze_whatsapp_chat_screenshot(image_path):
    """
    OCR analysis for WhatsApp chat screenshot.
    Extracts:
      - System time (status bar)
      - Whether messages contain time instead of date
    """

    text = pytesseract.image_to_string(Image.open(image_path))
    text_clean = text.replace("\n", " ").strip()
    result = {}

    # 1️⃣ Extract system time (from status bar)
    time_pattern = r'\b([01]?\d|2[0-3]):[0-5]\d(?: ?[APMapm]{2})?\b'
    times = re.findall(time_pattern, text_clean)
    result['system_time'] = times[-1] if times else "Not found"

    # 2️⃣ Check message timestamps (must be time, not date)
    date_pattern = r'(\bYesterday\b|\bToday\b|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    time_found = re.search(time_pattern, text_clean)
    date_found = re.search(date_pattern, text_clean, re.IGNORECASE)

    result['last_message_ok'] = "Yes" if time_found and not date_found else "No"

    # Store OCR text
    result['raw_text'] = text_clean
    return result
