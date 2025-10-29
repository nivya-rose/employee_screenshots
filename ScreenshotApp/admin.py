from django.contrib import admin
from .models import UserSubmission, WhatsAppAnalysis

@admin.register(UserSubmission)
class UserSubmissionAdmin(admin.ModelAdmin):
         list_display = ['name', 'phone_number', 'register_number', 'company_email', 'timestamp']
         # Add more customizations if needed


@admin.register(WhatsAppAnalysis)
class WhatsAppAnalysisAdmin(admin.ModelAdmin):
    """
    Admin configuration for viewing WhatsApp OCR analysis results.
    Shows both backup and chat analysis info for quick review.
    """

    # 🧾 Columns to display in admin list view
    list_display = [
        'submission',              # Linked user submission
        'backup_system_time',      # 1️⃣ System time from backup screenshot
        'Last_back_up',            # 2️⃣ Last backup text
        'Last_backup_today',       # 3️⃣ Backup occurred today (Yes/No)
        'manage_google_storage',   # 4️⃣ Manage Google Storage value
        'google_storage_account',  # 5️⃣ Google account used for backup
        'google_account_org',      # 6️⃣ Whether .org account
        'include_videos_toggle',   # 7️⃣ Videos toggle ON/OFF
        'device_time_chat',        # 8️⃣ Chat screenshot top-bar time
        'last_message_ok',         # 9️⃣ Whether last message has time (Yes/No)
        'created_at',              # Timestamp
    ]

    # 🧭 Filters to help narrow down results in admin
    list_filter = [
        'Last_backup_today',
        'google_account_org',
        'include_videos_toggle',
        'last_message_ok',
        'created_at',
    ]

    # 🔍 Search bar for admin page
    search_fields = [
        'submission__name',
        'google_storage_account',
        'backup_system_time',
    ]

    # 🕒 Default ordering (newest first)
    ordering = ['-created_at']
