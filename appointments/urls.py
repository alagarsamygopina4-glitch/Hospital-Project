from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointments, name='appointments'),
    path('success/<int:pk>/', views.appointment_success, name='appointment_success'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('home/', views.home, name='home'),
    path('setup-db/', views.setup_database, name='setup_database'),
]