import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

from appointments.models import Appointment, Doctor
import datetime

# Create a dummy doctor if none exist
if not Doctor.objects.exists():
    from appointments.models import Department
    dept, _ = Department.objects.get_or_create(name="General")
    Doctor.objects.create(
        name="Test Doctor",
        specialization="General",
        department=dept,
        available_days="Monday",
        available_time_start=datetime.time(9, 0),
        available_time_end=datetime.time(17, 0)
    )

try:
    doctor = Doctor.objects.first()
    app = Appointment.objects.create(
        patient_name="Tester",
        patient_email="tester@example.com",
        patient_phone="1234567890",
        doctor=doctor,
        appointment_date=datetime.date.today(),
        appointment_time=datetime.time(10, 0),
        reason="Test booking unique token"
    )
    print(f"Appointment created successfully!")
    print(f"Token: {app.token_number}")
    if app.token_number:
        print("PASS: Token generated.")
    else:
        print("FAIL: Token missing.")
except Exception as e:
    print(f"FAIL: Error occurred: {e}")
