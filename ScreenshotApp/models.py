from django.db import models

class UserSubmission(models.Model):
    """
    Stores the basic employee submission details and uploaded screenshots.
    """
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    register_number = models.CharField(max_length=50)
    company_email = models.EmailField()
    
    # Uploaded screenshots
    backup_screenshot = models.ImageField(upload_to='screenshots/')
    chat_screenshot = models.ImageField(upload_to='screenshots/')
    
    # Timestamp of submission
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.register_number}"


class ScreenshotAnalysis(models.Model):
    """
    Stores analysis results linked to a specific user submission.
    """
    submission = models.ForeignKey(UserSubmission, on_delete=models.CASCADE)
    
    # Backup screenshot analysis
    backup_device_time = models.DateTimeField()
    last_backup_time_ok = models.CharField(max_length=3, default='No')
    manage_google_storage_ok = models.CharField(max_length=3, default='No')
    google_account_ok = models.CharField(max_length=3, default='No')
    videos_toggle_ok = models.CharField(max_length=3, default='No')
    
    # Chat screenshot analysis
    chat_device_time = models.DateTimeField()
    last_message_ok = models.CharField(max_length=3, default='No')

    def __str__(self):
        return f"Analysis for {self.submission.name}"
