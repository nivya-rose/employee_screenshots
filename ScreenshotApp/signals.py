from django.db.models.signals import post_save  # Example signal import (adjust based on your needs)
from django.dispatch import receiver
from .models import UserSubmission, ScreenshotAnalysis  # Fixed import to match models.py

# Example signal handler (customize as needed)
@receiver(post_save, sender=UserSubmission)
def handle_submission_save(sender, instance, created, **kwargs):
    if created:
        # Example: Trigger OCR or other logic here after saving
        print(f"New submission created: {instance.name}")
        # You could call your OCR functions here if needed