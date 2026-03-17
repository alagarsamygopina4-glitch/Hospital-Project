from django.db import models
from django.contrib.auth.models import User
from home.models import Patient

class DietPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft (AI Generated)'),
        ('approved', 'Approved by Doctor'),
        ('published', 'Published by Admin'),
    ]

    DIET_TYPES = [
        ('balanced', 'Balanced Diet'),
        ('keto', 'Keto Diet'),
        ('vegan', 'Vegan Diet'),
        ('low_carb', 'Low Carb'),
    ]
    
    # Link to Patient model from home app since patient login uses that
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, null=True, blank=True)
    # Keeping user field for backward compatibility or admin/doctor linkage if needed, but making it optional
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_diet_plans')
    
    diet_type = models.CharField(max_length=20, choices=DIET_TYPES, null=True, blank=True)
    calories_per_day = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', null=True, blank=True)
    
    # AI Content
    ai_generated_plan = models.TextField(blank=True, null=True, help_text="AI generated diet plan content")
    doctor_notes = models.TextField(blank=True, null=True, help_text="Notes from doctor approval")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        p_name = self.patient.username if self.patient else "Unknown Patient"
        return f"{p_name} - {self.diet_type} ({self.status})"

class DietRecommendation(models.Model):
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE)
    meal_time = models.CharField(max_length=50, choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Dinner', 'Dinner')], null=True, blank=True)
    recommendation = models.CharField(max_length=200, null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.meal_time}: {self.recommendation}"