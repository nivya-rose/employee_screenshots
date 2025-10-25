from django.contrib import admin
from .models import UserSubmission, ScreenshotAnalysis

@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
         list_display = ['name', 'phone_number', 'register_number', 'company_email', 'timestamp']
         # Add more customizations if needed

@admin.register(ScreenshotAnalysis)
class ScreenshotAnalysisAdmin(admin.ModelAdmin):
         list_display = ['submission', 'backup_device_time', 'chat_device_time']
         # Add more customizations if needed
     