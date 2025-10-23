import os
from django.db import models


def backup_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"screenshots/{instance.name}_{instance.register_number}_backup.{ext}"

def chat_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"screenshots/{instance.name}_{instance.register_number}_chat.{ext}"

class EmployeeScreenshotUpload(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    register_number = models.CharField(max_length=50)
    company_email = models.EmailField()
    
    backup_file = models.FileField(upload_to=backup_upload_path)
    chat_file = models.FileField(upload_to=chat_upload_path)
    
    def __str__(self):
        return f"{self.name} - {self.register_number}"
    
class ScreenshotAnalysis(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    employee_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    register_number = models.CharField(max_length=50)
    
    # backup file analysis fields
    backup_time = models.DateTimeField(null= True, blank= True)
    last_backup_time = models.DateTimeField(null= True, blank= True)
    manage_google_storage_data = models.CharField(max_length=10, null= True, blank= True)
    google_account=models.CharField( max_length=255, null= True, blank= True)
    videos_toggle_on = models.BooleanField(null= True, blank= True)
    
    #chat file analysis fields
    chats_ss_time = models.DateTimeField(null= True, blank= True)
    last_message_time = models.DateTimeField(null= True, blank= True)
    
    def __str__(self):
        return f"{self.employee_name} - {self.register_number} - {self.timestamp}"