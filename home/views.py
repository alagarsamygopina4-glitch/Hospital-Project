from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
from .models import Patient, OTP
from appointments.models import Doctor, Appointment
from diet.models import DietPlan, DietRecommendation

# Home Page
def home(request):
    return render(request, 'home/index.html')

# Patient Registration
def patient_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        blood_group = request.POST.get("blood_group")
        dob = request.POST.get("dob")
        contact = request.POST.get("contact")
        height = request.POST.get("height")
        weight = request.POST.get("weight")

        # Check if username already exists
        if Patient.objects.filter(username=username).exists():
            return render(request, 'home/patient_register.html', {'error': 'Username already exists!'})
        
        if Patient.objects.filter(email=email).exists():
            return render(request, 'home/patient_register.html', {'error': 'Email already exists!'})

        # Calculate BMI if height and weight are provided
        bmi = None
        try:
            h = float(height)
            w = float(weight)
            if h > 0 and w > 0:
                bmi = round(w / ((h / 100) ** 2), 2)
        except (TypeError, ValueError):
            bmi = None

        patient = Patient.objects.create(
            username=username,
            full_name=full_name,
            email=email,
            password=password,
            blood_group=blood_group,
            date_of_birth=dob if dob else None,
            contact=contact,
            height=float(height) if height else None,
            weight=float(weight) if weight else None,
            bmi=bmi,
        )

        # Auto-login after registration
        request.session['patient_id'] = patient.id
        request.session['patient_username'] = patient.username

        return redirect('patient_dashboard')

    return render(request, 'home/patient_register.html')

# Patient Login
def patient_login(request):
    message = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            patient = Patient.objects.get(username=username, password=password)
            request.session['patient_id'] = patient.id
            request.session['patient_username'] = patient.username
            return redirect('patient_dashboard')
        except Patient.DoesNotExist:
            message = "Invalid Username or Password"

    return render(request, 'home/patient_login.html', {"message": message})

# Patient Logout
def patient_logout(request):
    if 'patient_id' in request.session:
        del request.session['patient_id']
    if 'patient_username' in request.session:
        del request.session['patient_username']
    return redirect('home')

# Patient Dashboard
def patient_dashboard(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    
    try:
        patient = Patient.objects.get(id=patient_id)
        # Fetch appointments
        appointments = Appointment.objects.filter(patient_email=patient.email).order_by('-appointment_date')
        
        # Fetch Diet Plan
        try:
            diet_plan = DietPlan.objects.get(patient=patient)
            diet_recommendations = DietRecommendation.objects.filter(diet_plan=diet_plan)
        except DietPlan.DoesNotExist:
            diet_plan = None
            diet_recommendations = None
            
        # Get first name for welcome message
        first_name = patient.full_name.split(' ')[0] if patient.full_name else patient.username
            
        context = {
            'patient': patient,
            'first_name': first_name,
            'appointments': appointments,
            'diet_plan': diet_plan,
            'diet_recommendations': diet_recommendations
        }
        return render(request, 'home/patient_dashboard.html', context)
    except Patient.DoesNotExist:
        return redirect('patient_login')

# Doctor Login
def doctor_login(request):
    message = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            doctor = Doctor.objects.get(username=username, password=password)
            request.session['doctor_id'] = doctor.id
            request.session['doctor_username'] = doctor.username
            return redirect('doctor_dashboard') 
        except Doctor.DoesNotExist:
            message = "Invalid Username or Password"

    return render(request, 'home/doctor_login.html', {"message": message})

# Admin Login (Custom)
def admin_login(request):
    message = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            return redirect('admin_dashboard')
        else:
            message = "Invalid Admin Credentials"

    return render(request, 'home/admin_login.html', {"message": message})

# Admin Dashboard
def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')
    patients = Patient.objects.all()
    appointments = Appointment.objects.all().order_by('-appointment_date')
    doctors = Doctor.objects.all()
    
    context = {
        'patients': patients,
        'appointments': appointments,
        'doctors': doctors,
    }
    return render(request, 'home/admin_dashboard.html', context)

# Forgot Password - Request
def forgot_password(request):
    message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        
        # Detect role
        role = None
        user_id = None
        
        if Patient.objects.filter(email=email).exists():
            patient = Patient.objects.get(email=email)
            role = 'Patient'
            user_id = patient.id
        elif Doctor.objects.filter(email=email).exists():
            doctor = Doctor.objects.get(email=email)
            role = 'Doctor'
            user_id = doctor.id
        elif User.objects.filter(email=email).exists():
            admin = User.objects.get(email=email)
            role = 'Admin'
            user_id = admin.id
            
        if role:
            # Generate 6-digit OTP
            otp_val = str(random.randint(100000, 999999))
            
            # Store OTP in DB
            OTP.objects.create(user_id=user_id, role=role, otp=otp_val)
            
            # Send Email
            try:
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp_val}. It expires in 5 minutes.',
                    'admin@hospital.com',
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                # Fallback to ignore during development instead of failing hard.
                pass
            # Store necessary info in session
            request.session['reset_user_id'] = user_id
            request.session['reset_role'] = role
            request.session['reset_email'] = email
            
            return redirect('verify_otp')
        else:
            message = "No account found with that email address."

    return render(request, 'home/forgot_password.html', {"message": message})

# Verify OTP - Action
def verify_otp(request):
    message = ""
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == "POST":
        otp_input = request.POST.get("otp")
        role = request.session.get('reset_role')
        user_id = request.session.get('reset_user_id')

        # Check OTP
        otp_record = OTP.objects.filter(user_id=user_id, role=role).order_by('-created_at').first()
        
        if otp_record and otp_record.otp == otp_input:
            if not otp_record.is_expired():
                # OTP is valid
                request.session['otp_verified'] = True
                return redirect('reset_password')
            else:
                message = "OTP has expired. Please request a new one."
        else:
            message = "Invalid OTP."

    return render(request, 'home/verify_otp.html', {"message": message, "email": email})

# Reset Password - Action
def reset_password(request):
    message = ""
    # Check if OTP was verified
    if not request.session.get('otp_verified'):
        return redirect('forgot_password')

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        role = request.session.get('reset_role')
        user_id = request.session.get('reset_user_id')

        if new_password != confirm_password:
            message = "Passwords do not match!"
        else:
            if role == 'Patient':
                user = Patient.objects.get(id=user_id)
                user.set_password(new_password)
                login_url = 'patient_login'
            elif role == 'Doctor':
                user = Doctor.objects.get(id=user_id)
                user.set_password(new_password)
                login_url = 'doctor_login'
            elif role == 'Admin':
                user = User.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                login_url = 'admin_login'

            # Clean up session
            for key in ['reset_user_id', 'reset_role', 'reset_email', 'otp_verified']:
                if key in request.session:
                    del request.session[key]
            
            succ_msg = "Password updated successfully! Please login."
            if role == 'Patient':
                return render(request, 'home/patient_login.html', {"success": succ_msg})
            elif role == 'Doctor':
                return render(request, 'home/doctor_login.html', {"success": succ_msg})
            elif role == 'Admin':
                return render(request, 'home/admin_login.html', {"success": succ_msg})

    return render(request, 'home/reset_password.html', {"message": message})