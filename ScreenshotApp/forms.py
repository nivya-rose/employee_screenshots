from django import forms  # Import Django's forms module for creating form classes.
from .models import UserSubmission  # Import your UserSubmission model to base the form on it.

class SubmissionForm(forms.ModelForm):
    # This is a ModelForm, which automatically generates form fields based on the UserSubmission model.
    # It handles validation, saving to the database, and rendering in templates.
    # Use this in your views and templates instead of raw HTML forms for better security and ease.
    class Meta:
        # The Meta class defines how the form interacts with the model.
        model = UserSubmission  # Specifies the model this form is tied to.
        fields = [
            'name',  # Field for the user's name (text input).
            'phone_number',  # Field for the phone number (text input).
            'register_number',  # Field for the register number (text input).
            'company_email',  # Field for the company-provided email (email input with validation).
            'backup_screenshot',  # Field for uploading the backup screenshot (file input, restricted to images).
            'chat_screenshot',  # Field for uploading the chat screenshot (file input, restricted to images).
        ]
        widgets = {
            'timestamp': forms.HiddenInput(),  # <- hides the field automatically
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'register_number': forms.TextInput(attrs={'class': 'form-control'}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        # Note: 'fields' lists all the model fields you want in the form. If you add more to the model, include them here.
    
    # Optional: Customize widgets or add validation if needed.
    # For example, you can specify HTML attributes like placeholders or CSS classes.
    def __init__(self, *args, **kwargs):
        # This method initializes the form and allows customization of fields.
        super().__init__(*args, **kwargs)
        # Example customizations (uncomment and adjust as needed):
        # self.fields['name'].widget.attrs.update({'placeholder': 'Enter your name'})
        # self.fields['company_email'].help_text = 'Use your company-provided email.'
        # For file fields, Django handles them securely by default.
    
    # Optional: Add custom validation methods if the default model validation isn't enough.
    # For example, to check file types or sizes:
    def clean_backup_screenshot(self):
        # This method validates the backup_screenshot field specifically.
        screenshot = self.cleaned_data.get('backup_screenshot')
        if screenshot:
            # Check file size (e.g., limit to 5MB; adjust as needed).
            if screenshot.size > 5 * 1024 * 1024:  # 5MB in bytes
                raise forms.ValidationError('File size must be under 5MB.')
            # Check file type (ensure it's an image).
            if not screenshot.content_type in ['image/jpeg', 'image/png', 'image/gif']:
                raise forms.ValidationError('Only JPEG, PNG, or GIF images are allowed.')
        return screenshot
    
    def clean_chat_screenshot(self):
        # Similar validation for the chat screenshot.
        screenshot = self.cleaned_data.get('chat_screenshot')
        if screenshot:
            if screenshot.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5MB.')
            if not screenshot.content_type in ['image/jpeg', 'image/png', 'image/gif']:
                raise forms.ValidationError('Only JPEG, PNG, or GIF images are allowed.')
        return screenshot
    
    # Note: Django's ModelForm automatically handles saving to the model when form.save() is called in the view.
    # If you need more advanced validation (e.g., cross-field checks), add a clean() method here.