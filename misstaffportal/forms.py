from django import forms
from misclientportal.models import Appointment
from .models import ServiceRequest

class AppointmentNotesForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('TO_FOLLOW_UP', 'To Follow-Up'),
    ]
    id = forms.CharField(label='Full Name', disabled=True)
    full_name = forms.CharField(label='Full Name', disabled=True)
    email = forms.EmailField(label='Email', disabled=True)
    phone_number = forms.CharField(label='Phone Number', disabled=True)
    device_type = forms.CharField(label='Device Type', disabled=True)
    device_model = forms.CharField(label='Device Model', disabled=True)
    issue_description = forms.CharField(label='Issue Description', widget=forms.Textarea(attrs={'rows': 4}), disabled=True)
    notes = forms.CharField(label='Notes', widget=forms.Textarea(attrs={'rows': 4}))
    status = forms.ChoiceField(label='Status', choices=STATUS_CHOICES)
    appointment_date = forms.DateField(label='Appointment Date', widget=forms.DateInput(attrs={'type': 'date'}), disabled=True)
    appointment_time = forms.TimeField(label='Appointment Time', widget=forms.TimeInput(attrs={'type': 'time'}), disabled=True)

    class Meta:
        model = Appointment
        fields = ['id', 'full_name', 'email', 'phone_number', 'device_type', 'device_model', 'issue_description', 'notes', 'status', 'appointment_date', 'appointment_time']

class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['full_name', 'email', 'phone_number', 'device_model', 'device_type', 'issue_description', 'appointment_date', 'appointment_time']
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

class ServiceRequestForm(forms.ModelForm):
    VERIFIED_CHOICES = [
        (True, 'Yes'),
        (False, 'No')
    ]
    
    verified_by_client = forms.ChoiceField(
        choices=VERIFIED_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = ServiceRequest
        fields = [
            'department',
            'service_type',
            'scheduled_response_date',
            'scheduled_response_time',
            'verified_by_client',
            'problem_found',
            'recommendation',
            'service_completed_date',
            'service_verified_by_client_date'
        ]
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_response_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_response_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'problem_found': forms.Textarea(attrs={'class': 'form-control'}),
            'recommendation': forms.Textarea(attrs={'class': 'form-control'}),
            'service_completed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'service_verified_by_client_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }
