from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient_name', 'patient_email', 'patient_phone', 'doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your full name'
            }),
            'patient_email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your email address'
            }),
            'patient_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your phone number'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'appointment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control form-control-lg'
            }),
            'appointment_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control form-control-lg'
            }),
            'reason': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control form-control-lg',
                'placeholder': 'Describe your symptoms or reason for the visit'
            }),
        }