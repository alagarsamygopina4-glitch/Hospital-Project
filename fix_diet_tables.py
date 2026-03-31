import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
print("Database path:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop with no FK issues - SQLite allows this
cursor.execute("PRAGMA foreign_keys = OFF")

for table in ['diet_dailymealplan', 'diet_dietplan', 'diet_patienthealthprofile', 'diet_food']:
    cursor.execute(f"DROP TABLE IF EXISTS [{table}]")
    print(f"Dropped: {table}")

cursor.execute("DELETE FROM django_migrations WHERE app='diet'")
print("Cleared diet migration records")

cursor.execute("PRAGMA foreign_keys = ON")
conn.commit()

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'diet_%'")
remaining = [r[0] for r in cursor.fetchall()]
print("Remaining diet tables:", remaining)

cursor.execute("SELECT * FROM django_migrations WHERE app='diet'")
records = cursor.fetchall()
print("Diet migration records:", records)

conn.close()
print("\nNow run: python manage.py migrate")
