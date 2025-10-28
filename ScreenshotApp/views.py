import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import UserSubmission, ScreenshotAnalysis
from .utils.whatsapp_backup_ocr import analyze_whatsapp_backup_screenshot
from .utils.whatsapp_chat_ocr import analyze_whatsapp_chat_screenshot


def upload_screenshot(request):
    """
    Handles file upload, runs OCR on both WhatsApp screenshots,
    analyzes them, and saves results into the database.
    """
    if request.method == "POST":
        # --- Step 1: Get form data ---
        name = request.POST.get("name")
        phone = request.POST.get("phone_number")
        register = request.POST.get("register_number")
        email = request.POST.get("useremail")
        backup_file = request.FILES.get("backup_file")
        chat_file = request.FILES.get("chat_file")

        # --- Step 2: Validate ---
        if not all([name, phone, register, email, backup_file, chat_file]):
            messages.error(request, "Please fill all fields and upload both screenshots.")
            return redirect("/")

        # --- Step 3: Rename uploaded files ---
        today_str = datetime.now().strftime("%Y-%m-%d")
        backup_ext = os.path.splitext(backup_file.name)[1]
        chat_ext = os.path.splitext(chat_file.name)[1]
        backup_file.name = f"{name}_{phone}_{today_str}_backup{backup_ext}"
        chat_file.name = f"{name}_{phone}_{today_str}_chat{chat_ext}"

        # --- Step 4: Save UserSubmission ---
        submission = UserSubmission.objects.create(
            name=name,
            phone_number=phone,
            register_number=register,
            company_email=email,
            backup_screenshot=backup_file,
            chat_screenshot=chat_file,
        )

        # --- Step 5: Get absolute file paths ---
        backup_path = os.path.join(settings.MEDIA_ROOT, submission.backup_screenshot.name)
        chat_path = os.path.join(settings.MEDIA_ROOT, submission.chat_screenshot.name)

        # --- Step 6: Run OCR analysis for both screenshots ---
        backup_result = analyze_whatsapp_backup_screenshot(backup_path)
        chat_result = analyze_whatsapp_chat_screenshot(chat_path)

        # --- Step 7: Save results to ScreenshotAnalysis model ---
        ScreenshotAnalysis.objects.create(
            submission=submission,

            # Backup OCR
            system_time=backup_result.get("system_time"),
            backup_value=backup_result.get("backup_value"),
            backup_time_status=backup_result.get("backup_time_status"),
            google_storage_value=backup_result.get("google_storage_value"),
            google_storage_status=backup_result.get("google_storage_status"),
            google_account=backup_result.get("google_account"),
            google_account_status=backup_result.get("google_account_status"),
            videos_toggle_status=backup_result.get("videos_toggle_status"),

            # Chat OCR
            chat_device_time=chat_result.get("system_time"),
            last_message_ok=chat_result.get("last_message_ok"),

            # Raw text logs
            raw_text_backup=backup_result.get("raw_text"),
            raw_text_chat=chat_result.get("raw_text"),
        )

        messages.success(request, "OCR analysis completed successfully!")
        return redirect("/")
    
    return render(request, "screenshots/user_upload.html")
