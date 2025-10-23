import re
from django.shortcuts import render, get_object_or_404,redirect
from .models import EmployeeScreenshotUpload, ScreenshotAnalysis
from .drive_utils import list_screenshots_from_folder
from .drive_utils import upload_file_to_drive 
from django.contrib import messages
from .google_utils import append_to_sheet


FOLDER_ID = '13qefxLpR3ZitbyCHbKR73h9Wl4pcEov-'

def parse_filename(filename):
    """
    Parse filenames like 'nivya_9061705145_10_2025.jpeg'
    Returns: name, phone_number, month
    """
    match = re.match(r"(\w+)_(\d+)_(\d{2}_\d{4})", filename)
    if match:
        return match.groups()
    return ("Unknown", "Unknown", "Unknown")

def upload_screenshot(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone_number")
        register = request.POST.get("register_number")
        email = request.POST.get("useremail")
        backup_file = request.FILES.get("backup_file")
        chat_file = request.FILES.get("chat_file")

        EmployeeScreenshotUpload.objects.create(
            name=name,
            phone_number=phone,
            register_number=register,
            company_email=email,
            backup_file=backup_file,
            chat_file=chat_file
        )
    return render(request, "screenshots/user_upload.html")

