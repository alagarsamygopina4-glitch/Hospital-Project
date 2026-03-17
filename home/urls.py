from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('patient-login/', views.patient_login, name='patient_login'),
    path('patient-register/', views.patient_register, name='patient_register'),
    path('doctor-login/', views.doctor_login, name='doctor_login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:email>/', views.reset_password, name='reset_password'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient-logout/', views.patient_logout, name='patient_logout'),
]