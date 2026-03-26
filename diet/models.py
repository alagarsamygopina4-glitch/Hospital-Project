from django.db import models
from django.contrib.auth.models import User
from home.models import Patient

class PatientProfile(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    bmi = models.FloatField(null=True, blank=True)
    disease = models.CharField(max_length=200, null=True, blank=True, help_text="e.g., diabetes, BP, None")
    goal = models.CharField(max_length=50, choices=[
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('maintenance', 'Maintenance'),
    ], default='maintenance')

    def save(self, *args, **kwargs):
        if self.height and self.weight:
            h_meters = self.height / 100
            if h_meters > 0:
                self.bmi = round(self.weight / (h_meters * h_meters), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile: {self.patient.username}"

class Food(models.Model):
    name = models.CharField(max_length=200)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    category = models.CharField(max_length=50, choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ])
    disease_tag = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated diseases to avoid or suitable diseases")

    def __str__(self):
        return f"{self.name} ({self.category})"

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