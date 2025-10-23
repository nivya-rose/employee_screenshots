from django.contrib import admin
from .models import EmployeeScreenshotUpload, ScreenshotAnalysis

@admin.register(EmployeeScreenshotUpload)
class EmployeeScreenshotUploadAdmin(admin.ModelAdmin):
    list_display = ("name", "register_number", "timestamp")

@admin.register(ScreenshotAnalysis)
class ScreenshotAnalysis(admin.ModelAdmin):
    list_display = ( "timestamp", "employee_name","phone_number",  "register_number","device_time_backup","last_backup_time_ok",
                    "manage_google_storage_ok","google_account_ok","videos_toggle_ok","device_time_chat","last_message_ok")