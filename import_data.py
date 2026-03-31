import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

from diet.models import Food

def import_csv(file_path):
    print(f"Reading {file_path}...")
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        success = 0
        for row in reader:
            tag = row.get('disease_tag', '').strip().lower()
            
            # Map tag to boolean flags
            # Default everything is True (friendly) unless tagged as something else?
            # Or if it HAS a tag, maybe it's only friendly for THAT?
            # Let's say if tag is 'diabetes', it's diabetic friendly, 
            # and if empty, we assume it's friendly for all for now.
            
            # Reset defaults for specific tags
            is_diabetic = True
            is_bp = True
            is_heart = True
            
            # For simplicity, if it has a specific tag, let's keep it as is.
            # Usually we'd EXCLUDE if tag was NOT diabetes etc. 
            
            Food.objects.get_or_create(
                name=row['name'],
                defaults={
                    'calories': float(row['calories']),
                    'protein': float(row['protein']),
                    'carbs': float(row['carbs']),
                    'fat': float(row['fat']),
                    'category': row['category'].strip().lower(),
                    'is_diabetic_friendly': (tag == 'diabetes' or tag == ''),
                    'is_bp_friendly': (tag == 'bp' or tag == ''),
                    'is_heart_friendly': (tag == 'heart' or tag == ''),
                }
            )
            success += 1
        print(f"Successfully imported {success} food records.")

if __name__ == '__main__':
    import_csv('food_dataset.csv')
