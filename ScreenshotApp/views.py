import os
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import WhatsAppAnalysis
from .forms import SubmissionForm
from .utils.whatsapp_backup_ocr import analyze_whatsapp_backup_screenshot
from .utils.whatsapp_chat_ocr import analyze_whatsapp_chat_screenshot
from django.db.models import Q
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime

def upload_screenshot(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)

            today_str = datetime.now().strftime("%Y-%m-%d")
            name = submission.name
            phone = submission.phone_number

            # Rename uploaded files
            if submission.backup_screenshot:
                backup_ext = os.path.splitext(submission.backup_screenshot.name)[1]
                submission.backup_screenshot.name = f"{name}_{phone}_{today_str}_backup{backup_ext}"

            if submission.chat_screenshot:
                chat_ext = os.path.splitext(submission.chat_screenshot.name)[1]
                submission.chat_screenshot.name = f"{name}_{phone}_{today_str}_chat{chat_ext}"

            submission.save()

            # OCR extraction
            backup_path = os.path.join(settings.MEDIA_ROOT, submission.backup_screenshot.name)
            chat_path = os.path.join(settings.MEDIA_ROOT, submission.chat_screenshot.name)

            backup_result = analyze_whatsapp_backup_screenshot(backup_path)
            chat_result = analyze_whatsapp_chat_screenshot(chat_path)

            backup_time = backup_result.get("backup_system_time")
            chat_time = chat_result.get("device_time_chat")

            # --- 1️⃣ Duplicate check first (UI notification only) ---
            existing = WhatsAppAnalysis.objects.filter(
                submission__phone_number=phone,
                backup_system_time__iexact=backup_time,
                device_time_chat__iexact=chat_time
            ).exists()

            if existing:
                submission.delete()  # remove uploaded files
                messages.error(
                    request,
                    "Screenshot rejected! Both device times match a previous upload for this number. "
                    "Please upload the latest screenshots."
                )
                return redirect("user_upload")

            # --- 2️⃣ Validation checks ---
            issues = []

            if backup_result.get('last_backup_today') != 'Yes':
                issues.append("Your last backup is not today.")
            storage_str = backup_result.get('google_storage_value', '').strip()
            if storage_str.lower() in ["0 kb", "0kb", "0 b", "0b", "0"]:
                issues.append("Your backup size is 0. Please back up properly.")
            if backup_result.get('google_account_org') != 'Yes':
                issues.append("Please use an organization account for backup.")
            if chat_result.get('last_message_today') != 'Yes':
                issues.append("Please upload the latest chat screenshot.")

            if issues:
                submission.delete()  # remove uploaded files

                # Send email to user explaining issues
                if submission.company_email:
                    send_mail(
                        subject="Screenshot Upload Rejected",
                        message=(
                              f"Dear {submission.name},\n\n"
                                "Your WhatsApp screenshots upload cannot be accepted due to the following reasons:\n\n"
                                f"- " + "\n- ".join(issues) + "\n\n"
                                "As a result, this submission may be considered for Loss of Pay (LOP).\n\n"
                                "Please correct the issues and upload again.\n\nThank you."
                                            ),
                       
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[submission.company_email],
                        fail_silently=False,
                    ) 
                    print("mail sent")

                # Show UI notification
                messages.error(
                    request,
                    "Screenshot rejected! " + " ".join(issues)
                )
                return redirect("user_upload")

            # --- 3️⃣ Save new OCR record ---
            WhatsAppAnalysis.objects.create(
                submission=submission,
                backup_system_time=backup_time,
                Last_back_up=backup_result.get('last_backup'),
                Last_backup_today=backup_result.get('last_backup_today'),
                manage_google_storage=backup_result.get('google_storage_value'),
                google_storage_account=backup_result.get('google_storage_account'),
                google_account_org=backup_result.get('google_account_org'),
                include_videos_toggle=backup_result.get('videos_toggle_status'),
                device_time_chat=chat_time,
                last_message_ok=chat_result.get('last_message_today'),
                raw_text_backup=backup_result.get('raw_text'),
                raw_text_chat=chat_result.get('raw_text'),
            )

            messages.success(request, "OCR analysis completed successfully!")
            return redirect('user_upload')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SubmissionForm()

    return render(request, "screenshots/user_upload.html", {"form": form})


def is_superuser(user):
    return user.is_superuser


# 2️ Admin Login
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("analysis_results")
        else:
            messages.error(request, "Invalid credentials or not an admin user.")
    return render(request, "screenshots/login.html")


@user_passes_test(is_superuser, login_url='/admin_login/')
def analysis_results(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
      
    analyses = WhatsAppAnalysis.objects.select_related('submission').all().order_by('-created_at')
   
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            # Include entire end date
            end = end.replace(hour=23, minute=59, second=59)
            analyses = analyses.filter(created_at__range=[start, end])
        except ValueError:
            pass

    return render(request, "screenshots/analysis_results.html", {
        "analyses": analyses,
        "start_date": start_date or "",
        "end_date": end_date or "",
    })


def admin_logout(request):
    logout(request)
    return redirect("admin_login")


# 4️ Export to Excel
@login_required(login_url='/admin_login/')
def export_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "WhatsApp Analysis"
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Define headers
    headers = [
        'Name', 'Phone Number', 'Backup System Time', 'Last Backup',
        'Last Backup Today', 'Manage Google Storage', 'Google Storage Account',
        'Google Account Org', 'Device Time Chat', 'Last Message OK', 'Created At'
    ]
    ws.append(headers)

    # Get all records
    analysis = WhatsAppAnalysis.objects.select_related('submission').all().order_by('-created_at')
    
    # Filter by date range if provided
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            # include full end day
            end = end.replace(hour=23, minute=59, second=59)
            analysis = analysis.filter(created_at__range=(start, end))
        except ValueError:
            pass  # invalid date, ignore

    analysis = analysis.order_by('-created_at')
    # Add data rows
    for record in analysis:
        ws.append([
            record.submission.name if record.submission else '',
            record.submission.phone_number if record.submission else '',
            record.backup_system_time or '',
            record.Last_back_up or '',
            record.Last_backup_today or '',
            record.manage_google_storage or '',
            record.google_storage_account if record.google_storage_account else '',
            record.google_account_org or '',
            record.device_time_chat or '',
            record.last_message_ok or '',
            record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else '',
        ])

    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=whatsapp_screenshot_analysis.xlsx'

    wb.save(response)
    return response
