import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

from home.models import Patient
from diet.models import DietPlan, PatientHealthProfile
from diet.ai_logic import generate_7_day_diet_plan

def test_regeneration():
    patient = Patient.objects.filter(username='raajashree').first()
    if not patient:
        print("Patient 'raajashree' not found.")
        return

    print(f"Testing for patient: {patient.username}")
    
    # Check health profile
    try:
        has_profile = hasattr(patient, 'health_profile')
        print(f"Has health profile (hasattr): {has_profile}")
        if has_profile:
            print(f"Profile data: {patient.health_profile}")
    except Exception as e:
        print(f"Error checking health profile: {e}")
        return

    # Try to generate plan
    try:
        print("Attempting to generate plan...")
        plan = generate_7_day_diet_plan(patient)
        print(f"Plan generated successfully: {plan}")
    except Exception as e:
        print(f"ERROR GENERATING PLAN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_regeneration()
