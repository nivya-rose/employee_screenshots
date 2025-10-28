import pytesseract
from PIL import Image
import re


def analyze_whatsapp_backup_screenshot(image_path):
    """
    OCR-based WhatsApp backup screenshot analyzer.
    Extracts system time, last backup time, Google account info,
    storage usage, and videos toggle status.
    """

    text = pytesseract.image_to_string(Image.open(image_path))
    text_clean = text.replace("\n", " ").strip()
    result = {}

    # 1️⃣ System Time
    time_pattern = r'\b([01]?\d|2[0-3]):[0-5]\d(?: ?[APMapm]{2})?\b'
    times = re.findall(time_pattern, text_clean)
    result['system_time'] = times[-1] if times else "Not found"

    # 2️⃣ Last Backup (must be a time, not a date)
    backup_pattern = r'Last\s*backup\s*[:\-]?\s*([A-Za-z0-9 ,:AMPamp]+)'
    backup_match = re.search(backup_pattern, text_clean, re.IGNORECASE)
    backup_value = backup_match.group(1).strip() if backup_match else "Not found"
    if re.search(r'\d{1,2}\s*[A-Za-z]+', backup_value):
        result['backup_time_status'] = "No"
    elif re.search(time_pattern, backup_value):
        result['backup_time_status'] = "Yes"
    else:
        result['backup_time_status'] = "No"
    result['backup_value'] = backup_value

    # 3️⃣ Manage Google Storage
    storage_pattern = r'Manage\s*Google\s*Storage\s*[:\-]?\s*([0-9.,]+\s*[KMG]?B)'
    storage_match = re.search(storage_pattern, text_clean, re.IGNORECASE)
    if storage_match:
        value = storage_match.group(1)
        numeric = float(re.findall(r'\d+(?:\.\d+)?', value)[0])
        result['google_storage_status'] = "Yes" if numeric > 0 else "No"
        result['google_storage_value'] = value
    else:
        result['google_storage_status'] = "No"
        result['google_storage_value'] = "Not found"

    # 4️⃣ Google Account (.org check)
    account_pattern = r'[\w\.-]+@[\w\.-]+'
    accounts = re.findall(account_pattern, text_clean)
    account_with_org = [a for a in accounts if ".org" in a]
    result['google_account_status'] = "Yes" if account_with_org else "No"
    result['google_account'] = account_with_org[0] if account_with_org else "Not found"

    # 5️⃣ Include Videos Toggle
    if re.search(r'include\s*videos\s*[:\-]?\s*(on|yes|enabled)', text_clean, re.IGNORECASE):
        result['videos_toggle_status'] = "Yes"
    else:
        result['videos_toggle_status'] = "No"

    result['raw_text'] = text_clean
    return result
