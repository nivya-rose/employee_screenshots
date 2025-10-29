import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import UserSubmission, WhatsAppAnalysis
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

        # --- Step 7: Save results to WhatsAppAnalysis model ---
        WhatsAppAnalysis.objects.create(
            submission=submission,
            backup_system_time=backup_result.get('backup_system_time'),
            Last_back_up=backup_result.get('last_backup'),                # corrected key
            Last_backup_today=backup_result.get('last_backup_today'),
            manage_google_storage=backup_result.get('google_storage_value'),  # corrected key
            google_storage_account=backup_result.get('google_storage_account'),
            google_account_org=backup_result.get('google_account_org'),
            include_videos_toggle=backup_result.get('videos_toggle_status'),
            device_time_chat=chat_result.get('device_time_chat'),
            last_message_ok=chat_result.get('last_message_today'),
            raw_text_backup=backup_result.get('raw_text'),
            raw_text_chat=chat_result.get('raw_text'),
        )

        messages.success(request, "OCR analysis completed successfully!")
        return redirect("/")

    return render(request, "screenshots/user_upload.html")
