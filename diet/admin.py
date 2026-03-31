from django.contrib import admin
from .models import PatientHealthProfile, Food, DietPlan, DailyMealPlan

@admin.register(PatientHealthProfile)
class PatientHealthProfileAdmin(admin.ModelAdmin):
    list_display = ['patient', 'age', 'gender', 'bmi', 'goal', 'created_at']
    list_filter = ['gender', 'goal', 'diabetes', 'hypertension']
    search_fields = ['patient__username', 'patient__full_name']

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories', 'is_veg', 'cuisine']
    list_filter = ['category', 'is_veg', 'cuisine']
    search_fields = ['name']

class DailyMealPlanInline(admin.TabularInline):
    model = DailyMealPlan
    extra = 0
    readonly_fields = ['day_number', 'meal_type', 'food_name', 'calories']

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'status', 'daily_calories', 'created_at']
    list_filter = ['status']
    search_fields = ['patient__username']
    inlines = [DailyMealPlanInline]

@admin.register(DailyMealPlan)
class DailyMealPlanAdmin(admin.ModelAdmin):
    list_display = ['diet_plan', 'day_number', 'meal_type', 'food_name', 'calories']
    list_filter = ['day_number', 'meal_type']