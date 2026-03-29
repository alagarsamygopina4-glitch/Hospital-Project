from django.db import models
from django.contrib.auth.models import User
import uuid

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    specialization = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    available_days = models.CharField(max_length=200, help_text="e.g., Monday, Tuesday, Wednesday")
    available_time_start = models.TimeField()
    available_time_end = models.TimeField()
    
    def __str__(self):
        return f"{self.name} - {self.specialization}"

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
        self.save()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Patient Information
    patient_name = models.CharField(max_length=100)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=20)
    
    # Appointment Details
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    token_number = models.CharField(max_length=20, editable=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-appointment_date']
    
    
    def save(self, *args, **kwargs):
        if not self.token_number:
            # Get date string (e.g., 20260329)
            date_prefix = self.appointment_date.strftime('%Y%m%d') if self.appointment_date else "00000000"
            
            # Count existing appointments for this date to get a sequence
            count = Appointment.objects.filter(
                appointment_date=self.appointment_date
            ).count()

            # Generate a unique token using: DATE + SEQUENCE + RANDOM_SUFFIX
            # Random suffix helps avoid collisions if multiple saves happen simultaneously
            import uuid
            unique_suffix = uuid.uuid4().hex[:4].upper()
            
            # Example: 20260329-1-A4B2
            self.token_number = f"{date_prefix}-{count + 1}-{unique_suffix}"

        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name if self.doctor else 'No Doctor'} - {self.appointment_date} (Token: {self.token_number})"

class MedicalRecord(models.Model):
    patient_email = models.EmailField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    symptoms = models.TextField()
    treatment_plan = models.TextField()
    visit_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Record for {self.patient_email} on {self.visit_date}"

class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medication_name} - {self.dosage}"