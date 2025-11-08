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



class WhatsAppAnalysis(models.Model):
    """
    Stores OCR-extracted data from two uploaded screenshots:
    1️⃣ WhatsApp Backup screen
    2️⃣ WhatsApp Chat screen

    Each record is linked to a user submission (UserSubmission model)
    and holds details extracted by OCR for validation and reporting.
    """

    # -------------------------------------------------------
    # 🔗 RELATIONSHIP FIELD
    # -------------------------------------------------------
    submission = models.ForeignKey(
        'UserSubmission',
        on_delete=models.CASCADE,
        related_name='whatsapp_analysis'
    )

    # Snapshot of user info from submission
    name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    register_number = models.CharField(max_length=50, null=True, blank=True)
    company_email = models.EmailField(null=True, blank=True)

    # ... your existing OCR fields ...

    # -------------------------------------------------------
    # 📸 BACKUP SCREENSHOT DATA (OCR Extracted)
    # -------------------------------------------------------

    # 1. Time shown on the top bar of the backup screenshot
    backup_system_time = models.CharField(max_length=50, null=True, blank=True)

    # 2. The "Last backup" value (e.g., "Today, 10:30 AM" or "Yesterday, 9:00 PM")
    Last_back_up = models.CharField(max_length=100, null=True, blank=True)

    # 3. Whether the last backup occurred today ("Yes" or "No")
    Last_backup_today = models.CharField(max_length=10, null=True, blank=True)

    # 4. "Manage Google Storage" value — if greater than 0, marked "Yes"
    manage_google_storage = models.CharField(max_length=50, null=True, blank=True)

    # 5. Google storage account address (e.g., user@gmail.com)
    google_storage_account = models.CharField(max_length=150, null=True, blank=True)

    # 6. Whether the Google account contains "avodha" ("Yes" or "No")
    google_account_org = models.CharField(max_length=10, null=True, blank=True)

    # 7. Whether the "Include videos" toggle button is ON ("Yes" or "No")
    include_videos_toggle = models.CharField(max_length=10, null=True, blank=True)

    # -------------------------------------------------------
    # 💬 CHAT SCREENSHOT DATA (OCR Extracted)
    # -------------------------------------------------------

    # 8. Device time shown on the top bar of the chat screenshot
    device_time_chat = models.CharField(max_length=50, null=True, blank=True)

    # 9. Whether the last visible message shows a time (not a date/yesterday)
    last_message_ok = models.CharField(max_length=10, null=True, blank=True)

    # -------------------------------------------------------
    # 🧾 RAW OCR TEXT (Optional for Debugging or Review)
    # -------------------------------------------------------

    # Full OCR text extracted from backup screenshot (for traceability)
    raw_text_backup = models.TextField(null=True, blank=True)

    # Full OCR text extracted from chat screenshot (for traceability)
    raw_text_chat = models.TextField(null=True, blank=True)

    # -------------------------------------------------------
    # 🕒 META INFO
    # -------------------------------------------------------

    # Automatically records when the analysis entry was created
    created_at = models.DateTimeField(auto_now_add=True)

    # -------------------------------------------------------
    # 🧩 STRING REPRESENTATION
    # -------------------------------------------------------
    
    def save(self, *args, **kwargs):
        if self.submission:
            self.name = self.submission.name
            self.phone_number = self.submission.phone_number
            self.register_number = self.submission.register_number
            self.company_email = self.submission.company_email
        super().save(*args, **kwargs)
        

    def __str__(self):
        """Returns a readable name in Django Admin."""
        return f"WhatsApp Analysis - {self.submission.name}"
