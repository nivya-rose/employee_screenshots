from django.contrib import admin
from .models import EmployeeScreenshotUpload, ScreenshotAnalysis

@admin.register(EmployeeScreenshotUpload)
class EmployeeScreenshotUploadAdmin(admin.ModelAdmin):
    list_display = ("name", "register_number", "timestamp")

@admin.register(ScreenshotAnalysis)
class ScreenshotAnalysisAdmin(admin.ModelAdmin):
    list_display = ("employee_name", "register_number", "timestamp", "backup_time", "last_backup_time")
