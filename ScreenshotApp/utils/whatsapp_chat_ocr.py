from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import pytesseract
import re
import cv2

# Adjust Tesseract path if needed
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
    """
    Extracts all time-like strings from text, fixing missing or malformed OCR cases.
    Handles:
      - 12:45, 9.05PM, 145 -> 1:45, etc.
    """
    time_re = re.compile(r'\b(?:[01]?\d|2[0-3])[:.\s]?[0-5]?\d?(?:\s?[AaPp][Mm])?\b')
    all_times = time_re.findall(text)
    cleaned_times = []

    for t in all_times:
        t_clean = t.replace(' ', '').replace('.', ':').upper()

        # Handle missing colon (e.g. 145 -> 1:45)
        if ':' not in t_clean and len(t_clean) >= 3:
            ampm = ''
            if t_clean.endswith('AM') or t_clean.endswith('PM'):
                ampm = t_clean[-2:]
                t_clean = t_clean[:-2]
            t_clean = t_clean[:-2] + ':' + t_clean[-2:] + ampm

        # Fix OCR cases like '55' or '455' becoming malformed
        if re.fullmatch(r'\d{2}', t_clean):
            t_clean = f"{t_clean[0]}:{t_clean[1:]}"
        elif re.fullmatch(r'\d{3}', t_clean):
            t_clean = f"{t_clean[0]}:{t_clean[1:]}"

        cleaned_times.append(t_clean)

    return cleaned_times


def analyze_whatsapp_chat_screenshot(image_path):
    """
    Extracts:
      - Device system time (from top bar)
      - Top chat time (from right column)
      - Whether last message is from today
    """
    result = {}
    img = Image.open(image_path)
    w, h = img.size

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
            result["device_time_chat"] = best_time
        else:
            result["device_time_chat"] = f"Not found ({ocr_text})"

    except Exception as e:
        result["device_time_chat"] = f"Error: {e}"

    # --- 2️⃣ TOP CHAT TIME (right column) ---
    right_col = img.crop((int(0.7 * w), int(0.12 * h), w, int(0.9 * h)))
    right_text = pytesseract.image_to_string(_preprocess_for_ocr(right_col), config="--psm 6")
    times_in_right = _extract_time_from_text(right_text)
    result['top_chat_time'] = times_in_right[0] if times_in_right else "Not found"

    # --- 3️⃣ Check if last message is from today ---
    if times_in_right and not re.search(r'\b(Yesterday|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', right_text, re.IGNORECASE):
        result['last_message_today'] = "Yes"
    else:
        result['last_message_today'] = "No"

    result['raw_text'] = right_text
    return result
