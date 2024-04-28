# forms.py

from django import forms

class AddEmployeeForm(forms.Form):
    username = forms.CharField(label='Username')
    email = forms.EmailField(label='Email')
    # Add other fields as needed

class FileUploadForm(forms.Form):
    fileUpload = forms.FileField()
    
from django import forms
from django.contrib.auth.forms import PasswordResetForm

class CustomPasswordResetForm(PasswordResetForm):
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match.")

        # Perform additional validation as needed

        return cleaned_data