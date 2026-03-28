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
            try:
                appointment = form.save(commit=False)
                appointment.status = 'pending'
                appointment.save() # This triggers the token generation in models.py
                
                # Double-check token generation
                if not appointment.token_number:
                    import uuid
                    appointment.token_number = str(uuid.uuid4())[:8].upper()
                    appointment.save()

                # Send confirmation email with token (fail silently)
                try:
                    send_appointment_confirmation_email(appointment)
                except Exception as email_err:
                    print(f"Email Error (non-critical): {email_err}")
                
                messages.success(request, f'✓ Appointment booked successfully! Token: {appointment.token_number}')
                return redirect('appointment_success', token=appointment.token_number)
            except Exception as e:
                import traceback
                print("CRITICAL ERROR DURING APPOINTMENT SAVE:")
                print(traceback.format_exc())
                # Return a visible error instead of a generic 500
                from django.http import HttpResponse
                return HttpResponse(f"Error saving appointment: {str(e)}. Please check console logs.", status=500)
        else:
            # Form is invalid, re-render form with errors
            context = {'form': form, 'doctors': doctors}
            return render(request, 'appointments/appointments.html', context)

    else:
        form = AppointmentForm()
    
    context = {'form': form, 'doctors': doctors}
    return render(request, 'appointments/appointments.html', context)

def appointment_success(request, token):
    try:
        # Search for appointment by token
        appointment = Appointment.objects.get(token_number=token)
    except Appointment.DoesNotExist:
        # Fallback search if something went wrong with the case or lookup
        appointment = Appointment.objects.filter(token_number__iexact=token).first()
        if not appointment:
            messages.error(request, 'Appointment not found in our records.')
            return redirect('appointments')
    
    context = {
        'appointment': appointment,
        'token_from_url': token # Pass the raw token as fallback
    }
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