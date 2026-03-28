from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, Doctor
from .forms import AppointmentForm
from .emails import (
    send_appointment_confirmation_email,
    send_appointment_rescheduled_email,
    send_appointment_cancelled_email,
)

def appointments(request):
    doctors = Doctor.objects.all()
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'pending'
            appointment.save()
            
            # Send confirmation email with token
            try:
                send_appointment_confirmation_email(appointment)
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            messages.success(request, f'✓ Appointment booked successfully! Your Token: {appointment.token_number}')
            return redirect('appointment_success', token=appointment.token_number)
        else:
            context = {'form': form, 'doctors': doctors}
            return render(request, 'appointments/appointments.html', context)

    else:
        form = AppointmentForm()
    
    context = {'form': form, 'doctors': doctors}
    return render(request, 'appointments/appointments.html', context)

def appointment_success(request, token):
    try:
        appointment = Appointment.objects.get(token_number=token)
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