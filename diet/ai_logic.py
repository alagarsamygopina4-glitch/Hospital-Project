import random
from diet.models import DietPlan, DietRecommendation, Food, PatientProfile
from home.models import Patient

def generate_diet_plan_for_patient(patient_id):
    patient = Patient.objects.get(id=patient_id)
    profile, created = PatientProfile.objects.get_or_create(patient=patient)
    
    # Calculate daily calories target
    # Simple formulas
    if not profile.weight or not profile.height:
        cal_target = 2000
    else:
        # TDEE basic estimation
        cal_target = profile.weight * 24
        
    if profile.goal == 'weight_loss':
        cal_target -= 500
        diet_type = 'low_carb'
    elif profile.goal == 'weight_gain':
        cal_target += 500
        diet_type = 'balanced'
    else:
        diet_type = 'balanced'

    # Filter foods
    foods = Food.objects.all()
    if profile.disease:
        diseases = [d.strip().lower() for d in profile.disease.split(',')]
        # This is a naive logic: exclude foods whose disease_tag is exactly the disease or containing it
        # Actually, let's include foods that don't clash or specifically handle tags
        # For a basic rule-based AI, let's just avoid bad tags (assuming disease_tag is bad if it matches)
        # But wait, in the dummy data format: disease_tag="diabetes" means "good for diabetes"
        # The prompt says: "Filters foods based on disease"
        # Let's say if disease_tag matches, it's good. If it's a conflict, it's bad.
        # Let's just do a simple filter.
        filtered_foods = []
        for f in foods:
            if not f.disease_tag:
                filtered_foods.append(f)
            else:
                tags = [t.strip().lower() for t in f.disease_tag.split(',')]
                # if any tag matches patient disease, include it
                if any(d in tags for d in diseases):
                    filtered_foods.append(f)
        if len(filtered_foods) > 0:
            foods = filtered_foods

    breakfasts = [f for f in foods if f.category == 'breakfast']
    lunches = [f for f in foods if f.category == 'lunch']
    dinners = [f for f in foods if f.category == 'dinner']
    snacks = [f for f in foods if f.category == 'snack']
    
    # fallback if empty
    if not breakfasts: breakfasts = Food.objects.filter(category='breakfast')
    if not lunches: lunches = Food.objects.filter(category='lunch')
    if not dinners: dinners = Food.objects.filter(category='dinner')

    # Ensure uniqueness or replace old plan
    DietPlan.objects.filter(patient=patient).delete()
    plan = DietPlan.objects.create(
        patient=patient,
        diet_type=diet_type,
        calories_per_day=cal_target,
        status='draft',
        ai_generated_plan=f"AI Rule-Based Plan for Goal: {profile.goal}"
    )
    
    # Add recommendations
    def add_meal(meal_time, meal_list):
        if meal_list:
            meal = random.choice(meal_list)
            DietRecommendation.objects.create(
                diet_plan=plan,
                meal_time=meal_time,
                recommendation=f"{meal.name} (P:{meal.protein}g, C:{meal.carbs}g, F:{meal.fat}g)",
                calories=meal.calories
            )
            
    add_meal('Breakfast', breakfasts)
    add_meal('Lunch', lunches)
    add_meal('Dinner', dinners)
    
    return plan
