from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DietPlan, DietRecommendation
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
        recommendations = DietRecommendation.objects.filter(diet_plan=diet_plan)
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