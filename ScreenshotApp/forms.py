from django import forms
from .models import UserSubmission
import re

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = UserSubmission
        fields = [
            'name',
            'phone_number',
            'register_number',
            'company_email',
            'backup_screenshot',
            'chat_screenshot',
        ]
        
        labels = {
            'backup_screenshot': 'Upload Backup Screenshot',
            'chat_screenshot': 'Upload Chat Screenshot',
            
        }
        widgets = {
            'timestamp': forms.HiddenInput(),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter You Full Name'
            }),
            'phone_number': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Provided Phone Number',
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'title': 'Enter digits only'
                
            }),
            'register_number': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Provided Phone Number',
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'title': 'Enter digits only'
            }),
            'company_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Avodha email ID'
            }),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        # ✅ Allow only 10 digits (no letters or special chars)
        if not re.fullmatch(r'\d{10}', phone):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_register_number(self):
        register = self.cleaned_data.get('register_number', '').strip()
        # ✅ Only numbers allowed (can adjust if alphanumeric is needed)
        if not register.isdigit():
            raise forms.ValidationError("Register number must contain digits only.")
        return register

    def clean_company_email(self):
        email = self.cleaned_data.get('company_email', '').strip().lower()
        if "avodha" not in email:
            raise forms.ValidationError("Please use your Avodha email address.")
        return email

    def clean_backup_screenshot(self):
        screenshot = self.cleaned_data.get('backup_screenshot')
        if screenshot:
            if screenshot.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5MB.')
            if screenshot.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                raise forms.ValidationError('Only JPEG, PNG, or GIF images are allowed.')
        return screenshot

    def clean_chat_screenshot(self):
        screenshot = self.cleaned_data.get('chat_screenshot')
        if screenshot:
            if screenshot.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5MB.')
            if screenshot.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                raise forms.ValidationError('Only JPEG, PNG, or GIF images are allowed.')
        return screenshot
