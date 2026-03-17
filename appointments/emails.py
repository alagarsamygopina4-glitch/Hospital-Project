from django.core.mail import send_mail
from django.utils.html import strip_tags


def send_appointment_confirmation_email(appointment):
    """Send confirmation email when appointment is booked"""
    subject = f'Appointment Confirmed - Token: {appointment.token_number}'

    doctor_name = appointment.doctor.name if appointment.doctor else 'To be assigned'
    doctor_spec = appointment.doctor.specialization if appointment.doctor else 'N/A'

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Appointment Confirmation</h2>
            <p>Dear {appointment.patient_name},</p>
            <p>Your appointment has been successfully booked.</p>

            <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border: 2px solid #28a745;">
                <h3 style="color: #28a745;">YOUR APPOINTMENT TOKEN: <strong>{appointment.token_number}</strong></h3>
                <p><strong>Please keep this token for your records</strong></p>
            </div>

            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Doctor:</strong> {doctor_name}</p>
                <p><strong>Specialization:</strong> {doctor_spec}</p>
                <p><strong>Date:</strong> {appointment.appointment_date}</p>
                <p><strong>Time:</strong> {appointment.appointment_time}</p>
                <p><strong>Reason:</strong> {appointment.reason}</p>
                <p><strong>Status:</strong> {appointment.get_status_display()}</p>
            </div>

            <p>If you need to reschedule or cancel, please login to your account.</p>
            <p>Thank you for choosing our hospital!</p>
        </body>
    </html>
    """

    try:
        send_mail(
            subject,
            strip_tags(html_message),
            'noreply@hospital.com',
            [appointment.patient_email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email error: {e}")


def send_appointment_rescheduled_email(appointment, old_date, old_time):
    """Send notification when appointment is rescheduled"""
    doctor_name = appointment.doctor.name if appointment.doctor else 'To be assigned'

    subject = f'Appointment Rescheduled - {doctor_name}'

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Appointment Rescheduled</h2>
            <p>Dear {appointment.patient_name},</p>
            <p>Your appointment has been rescheduled.</p>

            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Previous Time:</strong> {old_date} at {old_time}</p>
                <p><strong>New Time:</strong> {appointment.appointment_date} at {appointment.appointment_time}</p>
                <p><strong>Doctor:</strong> {doctor_name}</p>
            </div>

            <p>Thank you!</p>
        </body>
    </html>
    """

    try:
        send_mail(
            subject,
            strip_tags(html_message),
            'noreply@hospital.com',
            [appointment.patient_email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email error: {e}")


def send_appointment_cancelled_email(appointment):
    """Send notification when appointment is cancelled"""
    doctor_name = appointment.doctor.name if appointment.doctor else 'To be assigned'

    subject = f'Appointment Cancelled - {doctor_name}'

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Appointment Cancelled</h2>
            <p>Dear {appointment.patient_name},</p>
            <p>Your appointment has been cancelled.</p>

            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Doctor:</strong> {doctor_name}</p>
                <p><strong>Original Date:</strong> {appointment.appointment_date}</p>
                <p><strong>Original Time:</strong> {appointment.appointment_time}</p>
            </div>

            <p>If you wish to book another appointment, please login to your account.</p>
        </body>
    </html>
    """

    try:
        send_mail(
            subject,
            strip_tags(html_message),
            'noreply@hospital.com',
            [appointment.patient_email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email error: {e}")