from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('full_name', 'email', 'phone_number', 'device_type', 'device_model', 'issue_description', 'appointment_date', 'appointment_time')
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'device_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your device type'}),
            'device_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your device model'}),
            'issue_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter a brief description of the issue'}),
        }

