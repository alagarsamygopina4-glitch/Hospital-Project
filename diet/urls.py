from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.diet_dashboard, name='diet_dashboard'),
    path('regenerate/', views.regenerate_diet_plan, name='regenerate_diet_plan'),
    path('create/', views.create_diet_plan, name='create_diet_plan'),
    path('approve/<int:plan_id>/', views.doctor_approve_plan, name='doctor_approve_plan'),
]