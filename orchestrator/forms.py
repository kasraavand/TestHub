from django import forms
from .models import TestRequest
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User



class RequestForm(forms.ModelForm):
    
    class Meta:
        model = TestRequest
        fields = ('environment','interface', 'file')
        labels = {
        "environment": "environment",
        "interface":"interface",
        "file_field": "select file"
        }
        widgets = {
            'file': forms.ClearableFileInput(
                attrs={
                    'multiple': True,
                    'class':"custom-file-upload"
                    })
        }