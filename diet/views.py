from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DietPlan, DailyMealPlan, PatientHealthProfile, Food
from home.models import Patient
import random

def get_current_patient(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return None
    try:
        return Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return None

def diet_dashboard(request):
    patient = get_current_patient(request)
    if not patient:
        return redirect('patient_login')
    
    try:
        diet_plan = DietPlan.objects.get(patient=patient)
    except DietPlan.DoesNotExist:
        diet_plan = None
    
    recommendations = None
    if diet_plan and diet_plan.status in ['approved', 'published']:
        recommendations = DailyMealPlan.objects.filter(diet_plan=diet_plan).order_by('day_number', 'meal_type')
    elif diet_plan:
         # If not approved/published, don't show recommendations or show pending message
         pass
    
    context = {'diet_plan': diet_plan, 'recommendations': recommendations, 'patient': patient}
    return render(request, 'diet/diet_dashboard.html', context)

# Admin/Doctor view to create/upload plan
def create_diet_plan(request):
    # This view should ideally be protected for admin/doctor only
    # For now, we'll assume it's accessible or protected via Django Admin, 
    # but the user asked for "admin can upload". We might need a separate login or check user.is_staff
    if not request.user.is_staff:
         messages.error(request, "Access denied. Admins only.")
         return redirect('home')

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        diet_type = request.POST.get('diet_type')
        calories = request.POST.get('calories')
        ai_content = request.POST.get('ai_content')
        
        patient = get_object_or_404(Patient, id=patient_id)
        
        diet_plan, created = DietPlan.objects.update_or_create(
            patient=patient,
            defaults={
                'diet_type': diet_type, 
                'calories_per_day': calories,
                'ai_generated_plan': ai_content,
                'status': 'draft', # Pending doctor approval
                'created_by': request.user if request.user.is_authenticated else None
            }
        )
        messages.success(request, f"Diet plan {'created' if created else 'updated'} for {patient.username}.")
        return redirect('/admin/diet/dietplan/') # Redirect to admin list
    
    patients = Patient.objects.all()
    return render(request, 'diet/create_diet_plan.html', {'patients': patients})

def doctor_approve_plan(request, plan_id):
    if not request.user.is_staff: # Assuming doctors are staff
        return redirect('home')
        
    plan = get_object_or_404(DietPlan, id=plan_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            plan.status = 'approved'
            plan.doctor_notes = request.POST.get('notes', '')
            plan.save()
            messages.success(request, "Plan approved.")
        elif action == 'reject':
            plan.status = 'draft' # Or rejected
            plan.save()
    
    return redirect('/admin/diet/dietplan/')

def regenerate_diet_plan(request):
    patient = get_current_patient(request)
    if not patient:
        return redirect('patient_login')
        
    if not hasattr(patient, 'health_profile'):
        messages.warning(request, "Please complete your Health Profile first.")
        return redirect('health_profile_form')

    try:
        from diet.ai_logic import generate_7_day_diet_plan
        generate_7_day_diet_plan(patient)
        messages.success(request, "Diet plan generated successfully based on your profile!")
    except Exception as e:
        messages.error(request, f"Error generating plan: {str(e)}")
        # If it failed, we should probably redirect back
    
    return redirect('patient_dashboard')

def health_profile_form(request):
    patient = get_current_patient(request)
    if not patient:
        return redirect('patient_login')
        
    profile, created = PatientHealthProfile.objects.get_or_create(patient=patient)

    if request.method == 'POST':
        # Parse Personal & Body Metrics
        profile.age = int(request.POST.get('age', 30))
        profile.gender = request.POST.get('gender')
        profile.height = float(request.POST.get('height', 170.0))
        profile.weight = float(request.POST.get('weight', 70.0))
        profile.goal = request.POST.get('goal', 'maintain')
        
        # Patient model sync (keeping them in sync for BMI calculation)
        patient.height = profile.height
        patient.weight = profile.weight
        patient.save()

        # Parse Medical History
        profile.diabetes = request.POST.get('diabetes') == 'on'
        profile.hypertension = request.POST.get('hypertension') == 'on'
        profile.thyroid = request.POST.get('thyroid') == 'on'
        profile.heart_disease = request.POST.get('heart_disease') == 'on'
        profile.pcos = request.POST.get('pcos') == 'on'
        profile.other_symptoms = request.POST.get('other_symptoms', '')

        # Parse Food Prefs
        profile.dietary_preference = request.POST.get('dietary_preference', 'veg')
        profile.meal_frequency = int(request.POST.get('meal_frequency', 3))
        profile.cuisine_preference = request.POST.get('cuisine_preference', 'mixed')
        
        profile.milk_allergy = request.POST.get('milk_allergy') == 'on'
        profile.nuts_allergy = request.POST.get('nuts_allergy') == 'on'
        profile.gluten_allergy = request.POST.get('gluten_allergy') == 'on'
        profile.seafood_allergy = request.POST.get('seafood_allergy') == 'on'
        profile.custom_allergies = request.POST.get('custom_allergies', '')

        # Parse Lifestyle
        profile.activity_level = request.POST.get('activity_level', 'sedentary')
        profile.sleep_hours = float(request.POST.get('sleep_hours', 8))
        profile.water_intake = float(request.POST.get('water_intake', 2))
        profile.smoking_alcohol = request.POST.get('smoking_alcohol') == 'on'

        profile.save()

        # Generate Diet Plan automatically
        from diet.ai_logic import generate_7_day_diet_plan
        generate_7_day_diet_plan(patient)

        messages.success(request, "Health Profile saved! Your personalized AI diet plan has been generated.")
        return redirect('patient_dashboard')

    context = {'patient': patient, 'profile': profile}
    return render(request, 'diet/health_profile.html', context)