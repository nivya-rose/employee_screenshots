from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import pytesseract
import re
import cv2

# Adjust this path according to your Tesseract installation location
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def _preprocess_for_ocr(img: Image.Image, resize_factor=2):
    """Enhance image readability for OCR."""
    img = img.convert("L")
    w, h = img.size
    img = img.resize((w * resize_factor, h * resize_factor), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.6)
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageOps.invert(img)
    return img


def _extract_time_from_text(text):
    """Extract all possible time strings and normalize format."""
    time_re = re.compile(r'\b(?:[01]?\d|2[0-3])[:.\s]?[0-5]?\d?(?:\s?[AaPp][Mm])?\b')
    all_times = time_re.findall(text)

    cleaned_times = []
    for t in all_times:
        t_clean = t.replace(' ', '').replace('.', ':').upper()

        if ':' not in t_clean and len(t_clean) >= 3:
            ampm = ''
            if t_clean.endswith('AM') or t_clean.endswith('PM'):
                ampm = t_clean[-2:]
                t_clean = t_clean[:-2]
            t_clean = t_clean[:-2] + ':' + t_clean[-2:] + ampm
        cleaned_times.append(t_clean)

    return cleaned_times


def analyze_whatsapp_backup_screenshot(image_path):
    """Extracts key WhatsApp backup info including backup time, storage, and Avodha email."""
    img = Image.open(image_path)
    w, h = img.size
    result = {}

    # 1️⃣ Extract backup system time from top status bar
    try:
        # --- 1️⃣ DEVICE SYSTEM TIME (top status bar) ---
        img_cv = cv2.imread(image_path)
        h_cv, w_cv, _ = img_cv.shape

        top_bar = img_cv[0:int(0.10 * h_cv), 0:w_cv]
        gray = cv2.cvtColor(top_bar, cv2.COLOR_BGR2GRAY)
        gray = cv2.fastNlMeansDenoising(gray, None, 7, 7, 21)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 15, 10
        )
 
        pil_img = Image.fromarray(thresh)
        ocr_text = pytesseract.image_to_string(pil_img, config="--psm 6").strip()

        times = _extract_time_from_text(ocr_text)
        if times:
            best_time = max(times, key=len)
            result["backup_system_time"] = best_time
        else:
            result["backup_system_time"] = f"Not found ({ocr_text})"

    except Exception as e:
        result["backup_system_time"] = f"Error: {e}"

    
    # 2️⃣ Extract Last Backup info
    body_crop = img.crop((int(0.03 * w), int(0.08 * h), int(0.9 * w), int(0.45 * h)))
    body_text = pytesseract.image_to_string(_preprocess_for_ocr(body_crop), config='--psm 6')
    result['raw_text'] = body_text
    

    m = re.search(
        r'Last\s*Backup[:\s\-]*([0-9]{1,2}[:.][0-5][0-9](?:\s?[AaPp][Mm])?)',
        body_text, re.IGNORECASE
    )
    if m:
        last_backup_val = m.group(1).strip()
    else:
        m2 = re.search(r'Last.*?backup[:\s\-]*([A-Za-z0-9, :.\sAMPamp]+)', body_text, re.IGNORECASE)
        last_backup_val = m2.group(1).strip() if m2 else "Not found"
    result['last_backup'] = last_backup_val

    if _extract_time_from_text(last_backup_val) and 'yesterday' not in last_backup_val.lower():
        result['last_backup_today'] = "Yes"
    else:
        result['last_backup_today'] = "No"

    # 3️⃣ Extract Google Storage info and Email
    full_text = pytesseract.image_to_string(_preprocess_for_ocr(img), config='--psm 6')

    storage_match = re.search(
        r'Manage\s*Google\s*storage[:\s\-]*([\d.,]+\s*(?:TB|GB|MB|KB|B))',
        full_text, re.IGNORECASE
    )
    if storage_match:
        result['manage_google_storage'] = "Yes"
        result['google_storage_value'] = storage_match.group(1).strip()
    else:
        result['manage_google_storage'] = "No"
        result['google_storage_value'] = "Not found"
    
       # --- Extract email(s) ---
    email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
    company_email = email_matches[0].strip() if email_matches else "Not found"
    result['google_storage_account'] = company_email

    # --- Normalize text and detect Avodha email robustly ---
    normalized_email = company_email.strip().lower()
    normalized_email = re.sub(r'[\s\n\r\t]', '', normalized_email)  # remove hidden chars

    if normalized_email != "notfound" and "avodha" in normalized_email:
        result['google_account_org'] = "Yes"
    else:
        result['google_account_org'] = "No"


    # 4️⃣ Detect Include Videos toggle
    iv_match = re.search(
        r'Include\s*videos[\s\S]{0,40}([\d.,]+\s*(?:TB|GB|MB|KB|B)|backed up)',
        full_text, re.IGNORECASE
    )
    if iv_match:
        result['include_videos_toggle'] = "Yes"
    else:
        try:
            toggle_crop = img.crop((int(0.65 * w), int(0.35 * h), int(0.95 * w), int(0.52 * h)))
            t = _preprocess_for_ocr(toggle_crop)
            bbox = t.getbbox()
            result['include_videos_toggle'] = "Yes" if bbox else "No"
        except Exception:
            result['include_videos_toggle'] = "No"
            
    return result



