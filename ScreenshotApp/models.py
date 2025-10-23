import os
from django.db import models
from django.utils import timezone


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
    timestamp = models.DateTimeField(auto_now_add=True)  # when analysis happens
    employee_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    register_number = models.CharField(max_length=50)
    
    # Backup screenshot analysis
    device_time_backup = models.DateTimeField(null=True, blank=True)  # always current time
    last_backup_time_ok = models.CharField(max_length=3)  # Yes/No
    manage_google_storage_ok = models.CharField(max_length=3)  # Yes/No
    google_account_ok = models.CharField(max_length=3)  # Yes/No
    videos_toggle_ok = models.CharField(max_length=3)  # Yes/No

    # Chat screenshot analysis
    device_time_chat = models.DateTimeField(null=True, blank=True)  # always current time
    last_message_ok = models.CharField(max_length=3)  # Yes/No

    def __str__(self):
        return f"{self.employee_name} - {self.register_number} - {self.timestamp}"
