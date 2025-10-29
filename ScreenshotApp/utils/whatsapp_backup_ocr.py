# utils/whatsapp_backup_ocr.py
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # change if needed

def _preprocess_for_ocr(img: Image.Image, resize_factor=2):
    # convert to grayscale, resize, increase contrast, slight sharpen, then threshold
    img = img.convert("L")
    w, h = img.size
    img = img.resize((w * resize_factor, h * resize_factor), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.6)
    img = img.filter(ImageFilter.SHARPEN)
    # simple adaptive-ish threshold
    img = ImageOps.invert(img)
    return img

def _extract_time_from_text(text):
    # matches 12:34, 12:34 AM/PM, 12.34 am formats
    time_re = re.compile(r'\b(?:[01]?\d|2[0-3])[:.][0-5]\d(?:\s?[AaPp][Mm])?\b')
    m = time_re.findall(text)
    return m

def _parse_size_to_bytes(size_text):
    """
    Parse '12 TB', '2.2 GB', '144 MB' to bytes (int).
    Returns integer bytes or None if not parseable.
    """
    m = re.search(r'([\d.,]+)\s*(TB|GB|MB|KB|B)', size_text, re.IGNORECASE)
    if not m:
        return None
    num = float(m.group(1).replace(',', '.'))
    unit = m.group(2).upper()
    factor = {'B':1, 'KB':1024, 'MB':1024**2, 'GB':1024**3, 'TB':1024**4}
    return int(num * factor[unit])

def analyze_whatsapp_backup_screenshot(image_path):
    img = Image.open(image_path)
    w, h = img.size
    result = {}

    # 1) STATUS BAR (top) -> backup_system_time
    status_crop = img.crop((0, 0, w, int(0.07 * h)))  # top 7% - tune if needed
    status_text = pytesseract.image_to_string(_preprocess_for_ocr(status_crop), config='--psm 6')
    times = _extract_time_from_text(status_text)
    result['backup_system_time'] = times[-1] if times else "Not found"

    # 2) MAIN BODY OCR (for backup info) - crop an area roughly where the "Last Backup" label exists
    # heuristics: backup labels are near top-left below title; crop vertical slice 8%-45%
    body_crop = img.crop((int(0.03*w), int(0.08*h), int(0.9*w), int(0.45*h)))
    body_text = pytesseract.image_to_string(_preprocess_for_ocr(body_crop), config='--psm 6')
    result['raw_text'] = body_text

    # 3) Extract Last Backup (explicit regex)
    # Look for "Last Backup[: ]* 8:30 am" or "Last Backup: 8:30 am"
    m = re.search(r'Last\s*Backup[:\s\-]*([0-9]{1,2}[:.][0-5][0-9](?:\s?[AaPp][Mm])?)', body_text, re.IGNORECASE)
    if m:
        last_backup_val = m.group(1).strip()
    else:
        # fallback - any time near "backup" phrase
        m2 = re.search(r'Last.*?backup[:\s\-]*([A-Za-z0-9, :.\sAMPamp]+)', body_text, re.IGNORECASE)
        last_backup_val = m2.group(1).strip() if m2 else "Not found"
    result['last_backup'] = last_backup_val

    # 4) last_backup_today --> check if the extracted last_backup contains a time and not 'yesterday' or date
    if _extract_time_from_text(last_backup_val) and 'yesterday' not in last_backup_val.lower():
        result['last_backup_today'] = "Yes"
    else:
        result['last_backup_today'] = "No"

    # 5) Manage Google Storage -> crop area around "Manage Google storage" label or search body_text
    # Try find it in whole image first
    full_text = pytesseract.image_to_string(_preprocess_for_ocr(img), config='--psm 6')
    storage_match = re.search(r'Manage\s*Google\s*storage[:\s\-]*([\d.,]+\s*(?:TB|GB|MB|KB|B))', full_text, re.IGNORECASE)
    if storage_match:
        storage_value = storage_match.group(1).strip()
        result['manage_google_storage'] = "Yes" if _parse_size_to_bytes(storage_value) and _parse_size_to_bytes(storage_value) > 0 else "No"
        result['google_storage_value'] = storage_value
    else:
        # fallback: try to find near the phrase in body_text
        storage_match2 = re.search(r'Manage\s*Google\s*storage[\s\S]{0,60}([\d.,]+\s*(?:TB|GB|MB|KB|B))', body_text, re.IGNORECASE)
        if storage_match2:
            storage_value = storage_match2.group(1).strip()
            result['manage_google_storage'] = "Yes" if _parse_size_to_bytes(storage_value) and _parse_size_to_bytes(storage_value) > 0 else "No"
            result['google_storage_value'] = storage_value
        else:
            result['manage_google_storage'] = "No"
            result['google_storage_value'] = "Not found"

    # 6) Google account & org
    acct_match = re.search(r'[\w\.-]+@[\w\.-]+', full_text)
    result['google_storage_account'] = acct_match.group(0) if acct_match else "Not found"
    result['google_account_org'] = "Yes" if result['google_storage_account'] != "Not found" and result['google_storage_account'].endswith('.org') else "No"

    # 7) Include videos toggle -> two strategies:
    #    a) If the text under "Include videos" mentions "backed up" or a numeric, assume ON
    #    b) Visual detect: crop right-side of the "Include videos" row and check knob position brightness
    iv_match = re.search(r'Include\s*videos[\s\S]{0,40}([\d.,]+\s*(?:TB|GB|MB|KB|B)|backed up)', full_text, re.IGNORECASE)
    if iv_match:
        result['include_videos_toggle'] = "Yes"
    else:
        # try visual: crop approximate area right half middle and inspect bright circle position
        # heuristic crop: middle-right area (tweak if your screenshots differ)
        try:
            toggle_crop = img.crop((int(0.65*w), int(0.35*h), int(0.95*w), int(0.52*h)))
            # convert to grayscale and threshold: white knob on dark background or vice-versa
            t = _preprocess_for_ocr(toggle_crop)
            # compute center of bright region
            bbox = t.getbbox()
            # simple brightness check - if bright area present -> likely ON if knob at right (hard to generalize)
            result['include_videos_toggle'] = "Yes" if bbox else "No"
        except Exception:
            result['include_videos_toggle'] = "No"

    return result
