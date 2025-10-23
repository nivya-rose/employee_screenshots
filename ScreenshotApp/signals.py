from django.db.models.signals import post_save
from django.dispatch import receiver    
from .models import EmployeeScreenshotUpload, ScreenshotAnalysis

@receiver(post_save, sender=EmployeeScreenshotUpload)
def analyze_uploaded_files(sender, instance, created, **kwargs):
    if created:
        # Analyze backup file
        backup_data = analyze_backup(instance.backup_file.path)
        
        # Analyze chat file
        chat_data = analyze_chat(instance.chat_file.path)
        
        # Save results
        ScreenshotAnalysis.objects.create(
            employee_name=instance.name,
            phone_number=instance.phone_number,
            register_number=instance.register_number,
            backup_time=backup_data.get('backup_time'),
            last_backup_time=backup_data.get('last_backup_time'),
            manage_google_storage_data=backup_data.get('manage_google_storage_data'),
            google_account=backup_data.get('google_account'),
            videos_toggle_on=backup_data.get('videos_toggle_on'),
            chats_ss_time=chat_data.get('chats_ss_time'),
            last_message_time=chat_data.get('last_message_time'),
        )

# Dummy analysis functions
def analyze_backup(file_path):
    # Replace with real logic (OCR, CSV parsing, etc.)
    return {
        'backup_time': None,
        'last_backup_time': None,
        'manage_google_storage_data': None,
        'google_account': None,
        'videos_toggle_on': None
    }

def analyze_chat(file_path):
    return {
        'chats_ss_time': None,
        'last_message_time': None
    }