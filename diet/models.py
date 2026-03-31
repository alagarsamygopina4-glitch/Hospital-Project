from django.db import models
from django.contrib.auth.models import User

class PatientHealthProfile(models.Model):
    GOAL_CHOICES = [
        ('loss', 'Weight Loss'),
        ('gain', 'Weight Gain'),
        ('maintain', 'Maintain Weight'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    DIETARY_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-vegetarian'),
        ('vegan', 'Vegan'),
        ('egg', 'Eggetarian'),
    ]
    ACTIVITY_CHOICES = [
        ('sedentary', 'Sedentary (Office job)'),
        ('light', 'Light Activity'),
        ('moderate', 'Moderate Activity'),
        ('heavy', 'Heavy Activity (Athlete)'),
    ]
    CUISINE_CHOICES = [
        ('south', 'South Indian'),
        ('north', 'North Indian'),
        ('mixed', 'Mixed'),
    ]

    patient = models.OneToOneField('home.Patient', on_delete=models.CASCADE, related_name='health_profile')
    
    # Section 1: Personal Info
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    # Section 2: Body Metrics
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    bmi = models.FloatField(null=True, blank=True)
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, default='maintain')
    
    # Section 3: Medical History
    diabetes = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False, verbose_name="Blood Pressure")
    thyroid = models.BooleanField(default=False)
    heart_disease = models.BooleanField(default=False)
    pcos = models.BooleanField(default=False, verbose_name="PCOS (Females)")
    other_symptoms = models.TextField(blank=True, null=True, help_text="e.g., Acidity, Joint pain")
    
    # Section 4: Food Prefs
    milk_allergy = models.BooleanField(default=False)
    nuts_allergy = models.BooleanField(default=False)
    gluten_allergy = models.BooleanField(default=False)
    seafood_allergy = models.BooleanField(default=False)
    custom_allergies = models.CharField(max_length=200, blank=True, null=True)
    
    dietary_preference = models.CharField(max_length=10, choices=DIETARY_CHOICES, default='veg')
    meal_frequency = models.IntegerField(default=3, help_text="Number of meals per day")
    cuisine_preference = models.CharField(max_length=10, choices=CUISINE_CHOICES, default='mixed')
    
    # Section 5: Lifestyle
    activity_level = models.CharField(max_length=15, choices=ACTIVITY_CHOICES, default='sedentary')
    sleep_hours = models.FloatField(default=8)
    water_intake = models.FloatField(default=2, help_text="Liters per day")
    smoking_alcohol = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate BMI
        if self.height and self.weight:
            h_meters = self.height / 100
            self.bmi = round(self.weight / (h_meters * h_meters), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Health Profile: {self.patient.full_name or self.patient.username}"

class Food(models.Model):
    NAME_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    name = models.CharField(max_length=200)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    category = models.CharField(max_length=50, choices=NAME_CHOICES)
    
    # Attributes for Generation Logic
    is_veg = models.BooleanField(default=True)
    is_diabetic_friendly = models.BooleanField(default=True)
    is_heart_friendly = models.BooleanField(default=True)
    is_bp_friendly = models.BooleanField(default=True)
    contains_milk = models.BooleanField(default=False)
    contains_nuts = models.BooleanField(default=False)
    contains_gluten = models.BooleanField(default=False)
    cuisine = models.CharField(max_length=10, choices=[('south', 'South Indian'), ('north', 'North Indian'), ('mixed', 'Mixed')], default='mixed')

    def __str__(self):
        return f"{self.name} ({self.category})"

class DietPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', 'AI Generated'),
        ('reviewed', 'Reviewed by Admin'),
        ('approved', 'Approved'),
    ]
    patient = models.OneToOneField('home.Patient', on_delete=models.CASCADE, related_name='diet_plan')
    health_profile = models.ForeignKey(PatientHealthProfile, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    daily_calories = models.IntegerField(null=True, blank=True)
    doctor_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"7-Day Diet Plan for {self.patient.full_name}"

class DailyMealPlan(models.Model):
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meals')
    day_number = models.IntegerField() # 1-7
    meal_type = models.CharField(max_length=20) # Breakfast, Lunch, Dinner
    food_name = models.CharField(max_length=200)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()

    def __str__(self):
        return f"Day {self.day_number} - {self.meal_type}"