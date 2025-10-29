# utils/whatsapp_chat_ocr.py
from PIL import Image
import pytesseract
import re

def _preprocess_small(img: Image.Image, resize_factor=2):
    img = img.convert("L")
    w, h = img.size
    img = img.resize((w*resize_factor, h*resize_factor), Image.LANCZOS)
    return img

def analyze_whatsapp_chat_screenshot(image_path):
    img = Image.open(image_path)
    w, h = img.size
    result = {}

    # 1) Try status bar top crop for device time (top 7% like backup)
    status_crop = img.crop((0, 0, w, int(0.07*h)))
    status_text = pytesseract.image_to_string(_preprocess_small(status_crop), config='--psm 6')
    times = re.findall(r'\b(?:[01]?\d|2[0-3])[:.][0-5]\d(?:\s?[AaPp][Mm])?\b', status_text)
    result['device_time_chat'] = times[-1] if times else "Not found"

    # 2) Chat list times (right column). Crop right strip and OCR to get per-chat times.
    right_col = img.crop((int(0.7*w), int(0.12*h), w, int(0.9*h)))
    right_text = pytesseract.image_to_string(_preprocess_small(right_col), config='--psm 6')
    # find first occurrence of a time like 12:21 pm etc
    tmatch = re.search(r'\b(?:[01]?\d|2[0-3])[:.][0-5]\d(?:\s?[AaPp][Mm])?\b', right_text)
    result['top_chat_time'] = tmatch.group(0) if tmatch else "Not found"

    # 3) last_message_ok -> check for time presence and absence of 'Yesterday' or date pattern
    if tmatch and not re.search(r'\b(Yesterday|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', right_text, re.IGNORECASE):
        result['last_message_today'] = "Yes"
    else:
        result['last_message_today'] = "No"

    result['raw_text'] = right_text
    return result
