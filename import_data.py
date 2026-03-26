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
            # Map columns to Food model
            Food.objects.get_or_create(
                name=row['name'],
                defaults={
                    'calories': float(row['calories']),
                    'protein': float(row['protein']),
                    'carbs': float(row['carbs']),
                    'fat': float(row['fat']),
                    'category': row['category'].strip().lower(),
                    'disease_tag': row.get('disease_tag', '').strip()
                }
            )
            success += 1
        print(f"Successfully imported {success} food records.")

if __name__ == '__main__':
    import_csv('food_dataset.csv')
