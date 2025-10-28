from django.db import models
import re
from PIL import Image
import pytesseract


# Explicitly tell pytesseract where to find the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class UserSubmission(models.Model):
    """
    Stores employee or user details and uploaded screenshots.
    One submission corresponds to one WhatsApp backup & one chat screenshot.
    """
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    register_number = models.CharField(max_length=50)
    company_email = models.EmailField()

    # Uploaded screenshots (saved under MEDIA_ROOT/screenshots/)
    backup_screenshot = models.ImageField(upload_to='screenshots/')
    chat_screenshot = models.ImageField(upload_to='screenshots/')

    # Auto timestamp for submission
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.register_number}"

class ScreenshotAnalysis(models.Model):
    """
    Stores OCR results from WhatsApp screenshots.
    Each record corresponds to one user submission.
    """
    submission = models.ForeignKey(UserSubmission, on_delete=models.CASCADE, related_name='analysis')

    # ---------- BACKUP SCREENSHOT OCR RESULTS ----------
    system_time = models.CharField(max_length=50, blank=True, null=True, help_text="System/device time extracted from backup screenshot.")
    backup_value = models.CharField(max_length=100, blank=True, null=True, help_text="Raw text for 'Last backup' value (e.g. 'Today, 11:23 AM').")
    backup_time_status = models.CharField(max_length=10, default="No", help_text="Yes if backup shows time, not date.")

    google_storage_value = models.CharField(max_length=50, blank=True, null=True, help_text="Storage value text (e.g. '25.3 MB').")
    google_storage_status = models.CharField(max_length=10, default="No", help_text="Yes if storage > 0KB.")

    google_account = models.CharField(max_length=255, blank=True, null=True, help_text="Extracted Google account (if any).")
    google_account_status = models.CharField(max_length=10, default="No", help_text="Yes if account contains '.org'.")

    videos_toggle_status = models.CharField(max_length=10, default="No", help_text="Yes if 'Include videos' toggle detected as ON.")

    # ---------- CHAT SCREENSHOT OCR RESULTS ----------
    chat_device_time = models.CharField(max_length=50, blank=True, null=True, help_text="System/device time from chat screenshot.")
    last_message_ok = models.CharField(max_length=10, default="No", help_text="Yes if last message timestamp found.")

    # ---------- RAW TEXT (DEBUGGING / LOGGING) ----------
    raw_text_backup = models.TextField(blank=True, null=True, help_text="Full OCR text extracted from backup screenshot.")
    raw_text_chat = models.TextField(blank=True, null=True, help_text="Full OCR text extracted from chat screenshot.")

    analyzed_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when OCR was completed.")

    def __str__(self):
        return f"OCR Analysis for {self.submission.name}"

def analyze_whatsapp_chat_screenshot(image_path):
    """
    Analyzes a WhatsApp chat screenshot to extract:
    1️⃣ System time (from status bar)
    2️⃣ Whether the latest messages contain time instead of date
    """
    # Extract text using Tesseract
    text = pytesseract.image_to_string(Image.open(image_path))
    text_clean = text.replace("\n", " ").strip()

    result = {}

    # 1️⃣ Extract system time
    # Matches "12:45", "12:45 PM", "23:15", etc.
    time_pattern = r'\b([01]?\d|2[0-3]):[0-5]\d(?: ?[APMapm]{2})?\b'
    times = re.findall(time_pattern, text_clean)
    result['system_time'] = times[-1] if times else "Not found"

    # 2️⃣ Check message timestamps
    # WhatsApp messages may have either time (12:34 PM) or date (Yesterday, 25/10/2025, etc.)
    # We consider it valid if time exists and no date-like pattern dominates
    date_pattern = r'(\bYesterday\b|\bToday\b|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'

    # Find all timestamps
    time_found = re.search(time_pattern, text_clean)
    date_found = re.search(date_pattern, text_clean, re.IGNORECASE)

    if time_found and not date_found:
        result['last_message_ok'] = "Yes"
    else:
        result['last_message_ok'] = "No"

    # Save raw OCR text for debugging
    result['raw_text'] = text_clean

    return result