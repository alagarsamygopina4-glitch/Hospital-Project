import threading
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Appointment, Doctor
from .forms import AppointmentForm
from .emails import (
    send_appointment_confirmation_email,
    send_appointment_rescheduled_email,
    send_appointment_cancelled_email,
)

def appointments(request):
    try:
        doctors = Doctor.objects.all()
        
        if request.method == 'POST':
            form = AppointmentForm(request.POST)
            if form.is_valid():
                try:
                    # Use a transaction to ensure no two people get the same token simultaneously
                    with transaction.atomic():
                        appointment = form.save(commit=False)
                        appointment.status = 'pending'
                        
                        # Ensure appointment_date is set (it should be from the form)
                        if not appointment.appointment_date:
                            from django.utils import timezone
                            appointment.appointment_date = timezone.now().date()
                        
                        # Sequential Logic: Get the count for this specific day
                        day_count = Appointment.objects.filter(
                            appointment_date=appointment.appointment_date
                        ).count()
                        
                        token_number_only = day_count + 1
                        date_str = appointment.appointment_date.strftime('%Y%m%d')
                        appointment.token_number = f"T{date_str}{token_number_only:02d}"
                        
                        appointment.save()

                        # Send confirmation email in the background to prevent Timeout
                        threading.Thread(target=send_appointment_confirmation_email, args=(appointment,)).start()

                        messages.success(request, f'✓ Appointment booked successfully! Your Token: {appointment.token_number}')
                        return redirect('appointment_success', pk=appointment.id)
                except Exception as e:
                    print(f"Inner booking failure: {e}")
                    messages.error(request, f"Submission error: {str(e)}")
            else:
                context = {'form': form, 'doctors': doctors}
                return render(request, 'appointments/appointments.html', context)
        else:
            form = AppointmentForm()
        
        context = {'form': form, 'doctors': doctors}
        return render(request, 'appointments/appointments.html', context)
    except Exception as global_e:
        from django.http import HttpResponse
        return HttpResponse(f"<h2 style='color:red;'>System Error: {str(global_e)}</h2><p>Check if your database exists and migrations are run.</p>")

def appointment_success(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found')
        return redirect('appointments')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_success.html', context)


def get_current_patient_email(request):
    return request.session.get('patient_email') # Assuming email is in session or we fetch from patient object

def my_appointments(request):
    # Since we are using a custom Patient model and sessions, we should check session
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    
    from home.models import Patient
    try:
        patient = Patient.objects.get(id=patient_id)
        user_appointments = Appointment.objects.filter(patient_email=patient.email)
    except Patient.DoesNotExist:
        user_appointments = []
        
    context = {'appointments': user_appointments}
    return render(request, 'appointments/my_appointments.html', context)

def reschedule_appointment(request, appointment_id):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        old_date = appointment.appointment_date
        old_time = appointment.appointment_time
        
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save()
            send_appointment_rescheduled_email(appointment, old_date, old_time)
            messages.success(request, 'Appointment rescheduled! Notification sent to your email.')
            return redirect('my_appointments')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {'form': form, 'appointment': appointment}
    return render(request, 'appointments/reschedule_appointment.html', context)

def cancel_appointment(request, appointment_id):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        send_appointment_cancelled_email(appointment)
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
        return redirect('my_appointments')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/confirm_cancel.html', context)

def home(request):
    return render(request, 'appointments/home.html')

def doctor_dashboard(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('doctor_login')
    
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        # Get all appointments for this doctor
        doctor_appointments = Appointment.objects.filter(doctor=doctor).order_by('appointment_date', 'appointment_time')
    except Doctor.DoesNotExist:
        return redirect('doctor_login')
        
    context = {
        'doctor': doctor,
        'appointments': doctor_appointments
    }
    return render(request, 'appointments/doctor_dashboard.html', context)

def setup_database(request):
    """Temporary view to initialize the Render database without a shell."""
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    from django.core.management import call_command
    from .models import Doctor, Department

    output = []

    # 1. Run Migrations Automatically
    try:
        call_command('migrate')
        output.append("✅ All migrations applied successfully")
    except Exception as e:
        output.append(f"❌ Migration error: {str(e)}")

    # 2. Create Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
        output.append("✅ Superuser 'admin' created (PW: adminpassword123)")
    else:
        output.append("ℹ️ Superuser 'admin' already exists")

    # 3. Seed Departments and Doctors
    deps = [
        ("Cardiology", "Heart and blood vessel health"),
        ("Pediatrics", "Medical care for infants, children, and adolescents"),
        ("Neurology", "Disorders of the nervous system"),
        ("Orthopedics", "Musculoskeletal system issues"),
        ("Dermatology", "Skin, hair, and nail conditions"),
        ("General Medicine", "Primary healthcare and general checkups")
    ]
    
    for name, desc in deps:
        Department.objects.get_or_create(name=name, defaults={'description': desc})
    output.append(f"✅ {len(deps)} Departments created/verified")

    doctors_data = [
        ("Dr. John Smith", "johnsmith", "Cardiology", "Cardiologist"),
        ("Dr. Sarah Wilson", "sarahwilson", "Pediatrics", "Pediatrician"),
        ("Dr. Michael Brown", "michaelbrown", "Neurology", "Neurologist"),
        ("Dr. Emily Davis", "emilydavis", "Orthopedics", "Orthopedic Surgeon"),
        ("Dr. Robert Lee", "robertlee", "Dermatology", "Dermatologist"),
        ("Dr. Alice Johnson", "alicejohnson", "General Medicine", "General Physician"),
    ]

    for name, user, dep_name, spec in doctors_data:
        dep = Department.objects.get(name=dep_name)
        Doctor.objects.get_or_create(
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
    output.append(f"✅ {len(doctors_data)} Doctors created/verified")

    return HttpResponse("<br>".join(output) + "<br><br><b>Success! You can now log into /admin and also see doctors in the dropdown.</b>")