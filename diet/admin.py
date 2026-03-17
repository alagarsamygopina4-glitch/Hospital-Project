from django.contrib import admin
from .models import DietPlan, DietRecommendation

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'diet_type', 'calories_per_day', 'status']
    search_fields = ['patient__username']
    list_filter = ['status', 'diet_type']

@admin.register(DietRecommendation)
class DietRecommendationAdmin(admin.ModelAdmin):
    list_display = ['diet_plan', 'meal_time', 'recommendation', 'calories']
    search_fields = ['recommendation']