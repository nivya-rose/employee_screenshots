from django.contrib import admin
from .models import UserSubmission, ScreenshotAnalysis

@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
         list_display = ['name', 'phone_number', 'register_number', 'company_email', 'timestamp']
         # Add more customizations if needed

@admin.register(ScreenshotAnalysis)
class ScreenshotAnalysisAdmin(admin.ModelAdmin):
         list_display = ['submission',
                         'system_time', 
                         'backup_value', 
                         'google_account', 
                         'google_storage_value',
                         'google_storage_status',
                         'google_account_status',
                         'videos_toggle_status',
                         'chat_device_time',
                          'last_message_ok',
                            'analyzed_at',
                            'raw_text_backup',
                            'raw_text_chat',
                         ]
        
    