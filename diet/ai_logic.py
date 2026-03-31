import random
from .models import DietPlan, DailyMealPlan, Food, PatientHealthProfile

def calculate_daily_calories(profile):
    """
    Calculate TDEE (Total Daily Energy Expenditure) based on Mifflin-St Jeor Equation
    """
    # Baseline BMR estimation
    # 10 * weight (kg) + 6.25 * height (cm) - 5 * age (y) + s
    # s is +5 for male and -161 for female
    
    age = profile.age or 30
    weight = profile.weight
    height = profile.height
    gender = profile.gender or 'M'
    
    if gender == 'M':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    # Activity Multiplier
    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'heavy': 1.725
    }
    
    tdee = bmr * multipliers.get(profile.activity_level, 1.2)
    
    # Adjust for goals
    if profile.goal == 'loss':
        tdee -= 500
    elif profile.goal == 'gain':
        tdee += 500
        
    return int(tdee)

def generate_7_day_diet_plan(patient):
    """
    Generates a personalized 7-day diet plan based on the Patient's Health Profile
    """
    profile = patient.health_profile
    daily_calories = calculate_daily_calories(profile)
    
    # Step 1: Filter Foods based on Medical History and Allergies
    foods = Food.objects.all()
    
    # Medical Restrictions
    if profile.diabetes:
        foods = foods.filter(is_diabetic_friendly=True)
    if profile.hypertension:
        foods = foods.filter(is_bp_friendly=True)
    if profile.heart_disease:
        foods = foods.filter(is_heart_friendly=True)
        
    # Allergies
    if profile.milk_allergy:
        foods = foods.exclude(contains_milk=True)
    if profile.nuts_allergy:
        foods = foods.exclude(contains_nuts=True)
    if profile.gluten_allergy:
        foods = foods.exclude(contains_gluten=True)
        
    # Dietary Preference
    if profile.dietary_preference == 'veg':
        foods = foods.filter(is_veg=True)
    elif profile.dietary_preference == 'vegan':
        # Simple vegan check: veg and no milk (assuming milk is the only non-vegan veg)
        foods = foods.filter(is_veg=True, contains_milk=False)
    
    # Cuisine Preference
    # Try to favor preference, but fallback if empty
    cuisine_foods = foods.filter(cuisine=profile.cuisine_preference)
    if cuisine_foods.exists():
        foods = cuisine_foods

    # Step 2: Categorize meals
    breakfasts = foods.filter(category='breakfast')
    lunches = foods.filter(category='lunch')
    dinners = foods.filter(category='dinner')
    
    # Fallbacks to all foods if filtering was too strict
    if not breakfasts.exists(): breakfasts = Food.objects.filter(category='breakfast')
    if not lunches.exists(): lunches = Food.objects.filter(category='lunch')
    if not dinners.exists(): dinners = Food.objects.filter(category='dinner')

    # Step 3: Create DietPlan
    DietPlan.objects.filter(patient=patient).delete() # Remove old plan
    plan = DietPlan.objects.create(
        patient=patient,
        health_profile=profile,
        daily_calories=daily_calories,
        status='draft'
    )
    
    # Step 4: Generate 7 Days
    for day in range(1, 8):
        # Pick one for each meal type
        for meal_type, meal_list in [('Breakfast', breakfasts), ('Lunch', lunches), ('Dinner', dinners)]:
            food = random.choice(list(meal_list)) if meal_list.exists() else None
            if food:
                DailyMealPlan.objects.create(
                    diet_plan=plan,
                    day_number=day,
                    meal_type=meal_type,
                    food_name=food.name,
                    calories=food.calories,
                    protein=food.protein,
                    carbs=food.carbs,
                    fat=food.fat
                )
    
    return plan
