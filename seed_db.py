import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

from home.models import Patient
from appointments.models import Doctor, Department, Appointment, MedicalRecord, Prescription
from diet.models import DietPlan

def seed_data():
    print("Seeding database...")

    # 1. Create Departments
    deps = [
        ("Cardiology", "Heart and blood vessel health"),
        ("Pediatrics", "Medical care for infants, children, and adolescents"),
        ("Neurology", "Disorders of the nervous system"),
        ("Orthopedics", "Musculoskeletal system issues"),
        ("Dermatology", "Skin, hair, and nail conditions"),
        ("General Medicine", "Primary healthcare and general checkups")
    ]
    
    dep_objects = []
    for name, desc in deps:
        dep, created = Department.objects.get_or_create(name=name, defaults={'description': desc})
        dep_objects.append(dep)
        print(f"Department: {name}")

    # 2. Create Doctors
    specializations = {
        "Cardiology": ["Cardiologist", "Heart Surgeon"],
        "Pediatrics": ["Pediatrician"],
        "Neurology": ["Neurologist"],
        "Orthopedics": ["Orthopedic Surgeon"],
        "Dermatology": ["Dermatologist"],
        "General Medicine": ["General Physician"]
    }

    doctors_data = [
        ("Dr. John Smith", "johnsmith", "Cardiology"),
        ("Dr. Sarah Wilson", "sarahwilson", "Pediatrics"),
        ("Dr. Michael Brown", "michaelbrown", "Neurology"),
        ("Dr. Emily Davis", "emilydavis", "Orthopedics"),
        ("Dr. Robert Lee", "robertlee", "Dermatology"),
        ("Dr. Alice Johnson", "alicejohnson", "General Medicine"),
    ]

    doctor_objects = []
    for name, user, dep_name in doctors_data:
        dep = Department.objects.get(name=dep_name)
        spec = random.choice(specializations[dep_name])
        doc, created = Doctor.objects.get_or_create(
            username=user,
            defaults={
                'name': name,
                'password': 'password123',
                'specialization': spec,
                'department': dep,
                'available_days': "Monday, Wednesday, Friday",
                'available_time_start': "09:00",
                'available_time_end': "17:00"
            }
        )
        doctor_objects.append(doc)
        print(f"Doctor: {name} ({spec})")

    # 3. Create Patients
    patients_data = [
        ("Alice Wonder", "alice", "alice@example.com"),
        ("Bob Builder", "bob", "bob@example.com"),
        ("Charlie Brown", "charlie", "charlie@example.com"),
        ("Diana Prince", "diana", "diana@example.com"),
        ("Edward Norton", "edward", "edward@example.com"),
    ]

    patient_objects = []
    for name, user, email in patients_data:
        p, created = Patient.objects.get_or_create(
            username=user,
            defaults={
                'full_name': name,
                'email': email,
                'password': 'password123',
                'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+']),
                'date_of_birth': '1990-01-01',
                'gender': random.choice(['M', 'F']),
                'contact': '1234567890',
                'address': '123 Hospital Lane',
                'emergency_contact': '9876543210'
            }
        )
        patient_objects.append(p)
        print(f"Patient: {name}")

    # 4. Create Appointments
    reasons = ["Regular checkup", "Chest pain", "Fever", "Back pain", "Skin rash"]
    for i in range(10):
        p = random.choice(patient_objects)
        d = random.choice(doctor_objects)
        Appointment.objects.create(
            patient_name=p.full_name,
            patient_email=p.email,
            patient_phone=p.contact,
            doctor=d,
            appointment_date=datetime.now().date() + timedelta(days=random.randint(1, 10)),
            appointment_time="10:00",
            reason=random.choice(reasons),
            status='pending'
        )
    print("Appointments created.")

    # 5. Create Medical Records & Prescriptions
    for p in patient_objects[:3]:
        d = random.choice(doctor_objects)
        record = MedicalRecord.objects.create(
            patient_email=p.email,
            doctor=d,
            diagnosis="Common Flu",
            symptoms="Fever, cough, tiredness",
            treatment_plan="Rest and hydration"
        )
        Prescription.objects.create(
            medical_record=record,
            medication_name="Paracetamol",
            dosage="500mg",
            frequency="Thrice a day",
            duration="5 days",
            instructions="After meals"
        )
    print("Medical records created.")

    print("Success! Database seeded.")

if __name__ == "__main__":
    seed_data()
