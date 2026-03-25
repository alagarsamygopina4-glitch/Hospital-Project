from django.db import models
from django.utils import timezone
import datetime

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    username = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    bmi = models.FloatField(null=True, blank=True, help_text="Body Mass Index")
    address = models.TextField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.full_name if self.full_name else self.username

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
        self.save()

class OTP(models.Model):
    user_id = models.IntegerField()
    role = models.CharField(max_length=50)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # 5 minutes expiry
        return timezone.now() > self.created_at + datetime.timedelta(minutes=5)

    def __str__(self):
        return f"{self.role} - {self.user_id} - {self.otp}"