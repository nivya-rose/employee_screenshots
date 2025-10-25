import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import UserSubmission, ScreenshotAnalysis
from .utils import extract_text_from_image


def upload_screenshot(request):
    """
    Handles:
    1. Receiving the form submission
    2. Validating input fields
    3. Renaming and saving uploaded files
    4. Extracting text from images via OCR
    5. Analyzing extracted text for key criteria
    6. Saving both submission and analysis to the database
    """
    if request.method == "POST":
        # --- Step 1: Extract form data ---
        name = request.POST.get("name")
        phone = request.POST.get("phone_number")
        register = request.POST.get("register_number")
        email = request.POST.get("useremail")
        backup_file = request.FILES.get("backup_file")
        chat_file = request.FILES.get("chat_file")

        # --- Step 2: Validate required fields ---
        if not all([name, phone, register, email, backup_file, chat_file]):
            messages.error(request, "Please fill all fields and upload both files.")
            return redirect("/")

        # --- Step 3: Rename uploaded files (for consistency & uniqueness) ---
        today_str = datetime.now().strftime("%Y-%m-%d")
        backup_ext = os.path.splitext(backup_file.name)[1]
        chat_ext = os.path.splitext(chat_file.name)[1]

        backup_file.name = f"{name}_{phone}_{today_str}_backup{backup_ext}"
        chat_file.name = f"{name}_{phone}_{today_str}_chat{chat_ext}"

        # --- Step 4: Save user submission (files + details) ---
        employee_entry = UserSubmission.objects.create(
            name=name,
            phone_number=phone,
            register_number=register,
            company_email=email,
            backup_screenshot=backup_file,
            chat_screenshot=chat_file,
        )

        # --- Step 5: Get file paths for OCR ---
        backup_path = os.path.join(settings.MEDIA_ROOT, employee_entry.backup_screenshot.name)
        chat_path = os.path.join(settings.MEDIA_ROOT, employee_entry.chat_screenshot.name)

        # --- Step 6: Run OCR on both images ---
        backup_text = extract_text_from_image(backup_path)
        chat_text = extract_text_from_image(chat_path)

        # --- Step 7: Analyze text content (simple keyword checks for now) ---
        # You can customize these based on actual screenshot text
        last_backup_ok = "Yes" if "Last Backup" in backup_text else "No"
        manage_storage_ok = "Yes" if "Google Storage" in backup_text else "No"
        google_account_ok = "Yes" if "Account:" in backup_text else "No"
        videos_toggle_ok = "Yes" if "Videos Toggle: On" in backup_text else "No"

        last_message_ok = "Yes" if "Last message" in chat_text else "No"

        # --- Step 8: Save OCR analysis results ---
        ScreenshotAnalysis.objects.create(
            submission=employee_entry,
            backup_device_time=datetime.now(),  # You can later parse from OCR text
            last_backup_time_ok=last_backup_ok,
            manage_google_storage_ok=manage_storage_ok,
            google_account_ok=google_account_ok,
            videos_toggle_ok=videos_toggle_ok,
            chat_device_time=datetime.now(),
            last_message_ok=last_message_ok,
        )

        # --- Step 9: User feedback ---
        messages.success(request, "Screenshots uploaded and analyzed successfully using OCR!")
        return redirect("/")

    # --- Step 10: Render upload form for GET requests ---
    return render(request, "screenshots/user_upload.html")
